import os
import tempfile
import shutil
from typing import Dict, Any, Optional


def download_sketchfab_model(
    uid: str,
    target_size: float = 1.0,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """Download and import a Sketchfab model by its UID.
    
    The model will be scaled so its largest dimension equals target_size.
    
    Parameters:
    - uid: The unique identifier of the Sketchfab model (obtained from search_sketchfab_models)
    - target_size: The target size in Maya units for the largest dimension (default: 1.0)
    - api_key: Optional Sketchfab API key. If not provided, will try to get from environment variable SKETCHFAB_API_KEY
    
    Returns a dictionary with success status and information about the imported model.
    """
    import maya.cmds as cmds
    import requests
    import zipfile

    try:
        # Get API key
        if not api_key:
            api_key = os.getenv("SKETCHFAB_API_KEY")

        if not api_key:
            return {
                "success": False,
                "error": "Sketchfab API key is not configured. Set SKETCHFAB_API_KEY environment variable or provide api_key parameter.",
            }

        headers = {"Authorization": f"Token {api_key}"}

        # Request download info
        download_endpoint = f"https://api.sketchfab.com/v3/models/{uid}/download"

        response = requests.get(download_endpoint, headers=headers, timeout=30)

        if response.status_code == 401:
            return {"success": False, "error": "Authentication failed (401). Check your API key."}

        if response.status_code != 200:
            return {
                "success": False,
                "error": f"Download request failed with status code {response.status_code}",
            }

        data = response.json()

        if data is None:
            return {
                "success": False,
                "error": "Received empty response from Sketchfab API for download request",
            }

        # ------------------------------------------------------------------
        # 1. ƯU TIÊN: tải ZIP archive và tìm FBX/OBJ bên trong
        # ------------------------------------------------------------------
        temp_dir = tempfile.mkdtemp()
        model_file: Optional[str] = None
        model_ext: Optional[str] = None  # 'fbx', 'obj', 'gltf', ...

        archives = data.get("archives") or {}
        archive_info = None
        if isinstance(archives, dict):
            if "zip" in archives:
                archive_info = archives.get("zip")
            elif archives:
                # lấy bất kỳ archive đầu tiên nếu không có 'zip'
                archive_info = next(iter(archives.values()))

        if archive_info and isinstance(archive_info, dict) and archive_info.get("url"):
            zip_url = archive_info["url"]
            try:
                zip_resp = requests.get(zip_url, timeout=60)
                if zip_resp.status_code == 200:
                    zip_path = os.path.join(temp_dir, f"{uid}.zip")
                    with open(zip_path, "wb") as f:
                        f.write(zip_resp.content)

                    # Giải nén
                    extract_dir = os.path.join(temp_dir, "extracted")
                    os.makedirs(extract_dir, exist_ok=True)
                    with zipfile.ZipFile(zip_path, "r") as zf:
                        zf.extractall(extract_dir)

                    # Tìm file FBX / OBJ / ABC ưu tiên theo thứ tự
                    candidates: Dict[str, str] = {}
                    for root, _, files in os.walk(extract_dir):
                        for fn in files:
                            lower = fn.lower()
                            if lower.endswith(".fbx"):
                                candidates.setdefault("fbx", os.path.join(root, fn))
                            elif lower.endswith(".obj"):
                                candidates.setdefault("obj", os.path.join(root, fn))
                            elif lower.endswith(".abc"):
                                candidates.setdefault("abc", os.path.join(root, fn))

                    for ext in ["fbx", "obj", "abc"]:
                        if ext in candidates:
                            model_file = candidates[ext]
                            model_ext = ext
                            break
            except Exception:
                # Nếu ZIP thất bại, sẽ fallback sang GLTF ở bước 2
                pass

        # ------------------------------------------------------------------
        # 2. FALLBACK: dùng GLTF/GLB nếu không tìm thấy FBX/OBJ/ABC
        # ------------------------------------------------------------------
        if model_file is None:
            gltf_data = data.get("gltf")
            if not gltf_data:
                return {
                    "success": False,
                    "error": "No usable download (FBX/OBJ/GLTF) available for this model.",
                }

            download_url = gltf_data.get("url")
            if not download_url:
                return {
                    "success": False,
                    "error": "No GLTF download URL available for this model. Make sure the model is downloadable and you have access.",
                }

            # Download GLB
            model_response = requests.get(download_url, timeout=60)
            if model_response.status_code != 200:
                return {
                    "success": False,
                    "error": f"Failed to download GLTF model file: {model_response.status_code}",
                }

            model_file = os.path.join(temp_dir, f"{uid}.glb")
            with open(model_file, "wb") as f:
                f.write(model_response.content)
            model_ext = "gltf"

        # ------------------------------------------------------------------
        # 3. Import vào Maya dựa trên format đã chọn
        # ------------------------------------------------------------------
        try:
            previous_selection = cmds.ls(selection=True) or []

            # Chọn Maya import type theo định dạng
            if model_ext == "fbx":
                maya_type = "FBX"
            elif model_ext == "obj":
                maya_type = "OBJ"
            elif model_ext == "abc":
                maya_type = "Alembic"
            elif model_ext == "gltf":
                maya_type = "glTF"
            else:
                return {
                    "success": False,
                    "error": f"Unsupported imported format '{model_ext}'.",
                }

            # Thực hiện import
            try:
                cmds.file(
                    model_file,
                    i=True,
                    type=maya_type,
                    ignoreVersion=True,
                    mergeNamespacesOnClash=True,
                )
            except Exception as e:
                if model_ext == "gltf":
                    return {
                        "success": False,
                        "error": "Failed to import GLTF/GLB. Make sure a glTF import plugin is installed in Maya. "
                        f"Original error: {str(e)}",
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Failed to import model of type {maya_type}: {str(e)}",
                    }

            # Lấy danh sách object mới
            imported_objects = cmds.ls(selection=True) or []
            if not imported_objects:
                all_objects = cmds.ls(type="transform") or []
                imported_objects = [
                    obj
                    for obj in all_objects
                    if obj not in ["front", "side", "top", "persp"]
                ]

            # ------------------------------------------------------------------
            # 4. Tính bounding box + scale về target_size
            # ------------------------------------------------------------------
            if imported_objects and target_size > 0:
                bbox_min = None
                bbox_max = None

                for obj in imported_objects:
                    try:
                        obj_bbox = cmds.xform(
                            obj, query=True, worldSpace=True, boundingBox=True
                        )
                        if bbox_min is None:
                            bbox_min = [obj_bbox[0], obj_bbox[2], obj_bbox[4]]
                            bbox_max = [obj_bbox[1], obj_bbox[3], obj_bbox[5]]
                        else:
                            bbox_min[0] = min(bbox_min[0], obj_bbox[0])
                            bbox_min[1] = min(bbox_min[1], obj_bbox[2])
                            bbox_min[2] = min(bbox_min[2], obj_bbox[4])
                            bbox_max[0] = max(bbox_max[0], obj_bbox[1])
                            bbox_max[1] = max(bbox_max[1], obj_bbox[3])
                            bbox_max[2] = max(bbox_max[2], obj_bbox[5])
                    except Exception:
                        continue

                if bbox_min and bbox_max:
                    dimensions = [
                        bbox_max[0] - bbox_min[0],
                        bbox_max[1] - bbox_min[1],
                        bbox_max[2] - bbox_min[2],
                    ]
                    max_dimension = max(dimensions)

                    if max_dimension > 0:
                        scale_factor = target_size / max_dimension

                        for obj in imported_objects:
                            try:
                                current_scale = cmds.getAttr(f"{obj}.scale")[0]
                                new_scale = [
                                    current_scale[0] * scale_factor,
                                    current_scale[1] * scale_factor,
                                    current_scale[2] * scale_factor,
                                ]
                                cmds.setAttr(
                                    f"{obj}.scale",
                                    new_scale[0],
                                    new_scale[1],
                                    new_scale[2],
                                    type="double3",
                                )
                            except Exception:
                                pass

                        final_dimensions = [d * scale_factor for d in dimensions]
                    else:
                        final_dimensions = dimensions
                        scale_factor = 1.0
                else:
                    final_dimensions = None
                    scale_factor = 1.0
            else:
                final_dimensions = None
                scale_factor = 1.0

            # Restore previous selection
            cmds.select(previous_selection, replace=True)

            result: Dict[str, Any] = {
                "success": True,
                "message": f"Model {uid} imported successfully",
                "imported_objects": imported_objects,
                "object_count": len(imported_objects),
                "normalized": target_size > 0 and scale_factor != 1.0,
                "scale_factor": scale_factor if target_size > 0 else 1.0,
                "target_size": target_size,
                "source_format": model_ext,
            }

            if final_dimensions:
                result["dimensions"] = final_dimensions
                result["bounding_box"] = {"min": bbox_min, "max": bbox_max}

            return result

        finally:
            # Clean up temporary directory
            try:
                shutil.rmtree(temp_dir)
            except Exception:
                pass

    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "Request timed out. Check your internet connection.",
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to download model: {str(e)}",
        }
