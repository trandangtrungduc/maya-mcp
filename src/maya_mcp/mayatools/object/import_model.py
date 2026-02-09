import os
from typing import Dict, Any, List, Optional


def import_model(
    filepath: str,
    file_format: Optional[str] = None,
    namespace: Optional[str] = None,
    group_name: Optional[str] = None,
) -> Dict[str, Any]:
    """Import a 3D model file into the Maya scene.

    Supported formats (depend on installed plugins):
    - FBX: .fbx
    - OBJ: .obj
    - USD: .usd, .usda, .usdc
    - Alembic: .abc

    Parameters:
    - filepath: Full path to the file to import
    - file_format: Optional explicit format ('fbx', 'obj', 'usd', 'usda', 'usdc', 'abc').
                   If not provided, inferred from file extension.
    - namespace: Optional namespace to import under (prevents name clashes)
    - group_name: Optional name of a transform group to parent all imported objects under

    Returns a dictionary with success status and information about imported objects.
    """
    import maya.cmds as cmds

    # Validate filepath
    if not filepath or not isinstance(filepath, str):
        raise ValueError("Error: filepath must be a non-empty string")

    # Normalize path for Maya
    filepath = filepath.replace("\\", "/")

    if not os.path.exists(filepath):
        raise ValueError(f"Error: File does not exist at path: {filepath}")

    # Infer format from extension if not provided
    _, ext = os.path.splitext(filepath)
    ext = ext.lower().lstrip(".")

    if file_format is None:
        file_format = ext
    else:
        file_format = file_format.lower()

    # Map extensions / formats to Maya file types
    format_map = {
        "fbx": "FBX",
        "obj": "OBJ",
        "usd": "USD Import",
        "usda": "USD Import",
        "usdc": "USD Import",
        "abc": "Alembic",
        "alembic": "Alembic",
    }

    if file_format not in format_map:
        raise ValueError(
            f"Error: Unsupported import format '{file_format}'. "
            "Supported formats: fbx, obj, usd, usda, usdc, abc"
        )

    maya_type = format_map[file_format]

    # Store objects before import so we can detect new ones
    before_transforms = set(cmds.ls(type="transform") or [])

    # Build file command flags
    file_kwargs: Dict[str, Any] = {
        "i": True,
        "type": maya_type,
        "ignoreVersion": True,
        "mergeNamespacesOnClash": True,
        "options": "v=0;",
    }

    if namespace:
        file_kwargs["namespace"] = namespace

    try:
        cmds.file(filepath, **file_kwargs)

        # Detect imported transforms
        after_transforms = set(cmds.ls(type="transform") or [])
        imported_transforms = sorted(list(after_transforms - before_transforms))

        # Optionally group imported objects
        group_node = None
        if group_name and imported_transforms:
            if cmds.objExists(group_name):
                # If group exists, parent under it
                group_node = group_name
            else:
                group_node = cmds.group(
                    imported_transforms, name=group_name, world=True
                )

        # Compute simple bounding box and dimensions for imported objects
        bbox_min = None
        bbox_max = None

        for obj in imported_transforms:
            try:
                bb = cmds.xform(obj, query=True, worldSpace=True, boundingBox=True)
                obj_min = [bb[0], bb[2], bb[4]]
                obj_max = [bb[1], bb[3], bb[5]]

                if bbox_min is None:
                    bbox_min = obj_min[:]
                    bbox_max = obj_max[:]
                else:
                    bbox_min = [
                        min(bbox_min[0], obj_min[0]),
                        min(bbox_min[1], obj_min[1]),
                        min(bbox_min[2], obj_min[2]),
                    ]
                    bbox_max = [
                        max(bbox_max[0], obj_max[0]),
                        max(bbox_max[1], obj_max[1]),
                        max(bbox_max[2], obj_max[2]),
                    ]
            except Exception:
                # Ignore objects that fail bbox query
                continue

        dimensions = None
        if bbox_min is not None and bbox_max is not None:
            dimensions = [
                bbox_max[0] - bbox_min[0],
                bbox_max[1] - bbox_min[1],
                bbox_max[2] - bbox_min[2],
            ]

        result: Dict[str, Any] = {
            "success": True,
            "filepath": filepath,
            "format": file_format,
            "maya_type": maya_type,
            "namespace": namespace,
            "group": group_node,
            "imported_objects": imported_transforms,
            "object_count": len(imported_transforms),
        }

        if dimensions is not None:
            result["dimensions"] = dimensions
            result["bounding_box"] = {"min": bbox_min, "max": bbox_max}

        return result

    except Exception as e:
        raise RuntimeError(f"Error importing model: {str(e)}")

