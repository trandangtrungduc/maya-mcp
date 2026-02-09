import os
from typing import Dict, Any, List, Optional


def export_model(
    object_names: List[str],
    filepath: str,
    file_format: str = "fbx",
    export_selected: bool = False,
    export_all: bool = False
) -> Dict[str, Any]:
    """Export one or more objects from Maya to various file formats.
    
    Parameters:
    - object_names: List of object names to export. Can be empty if export_selected or export_all is True.
    - filepath: Full path where the exported file should be saved (including filename and extension)
    - file_format: Export format. Supported formats: fbx, obj, usd, alembic, dae (Collada), ma, mb
    - export_selected: If True, export currently selected objects (ignores object_names)
    - export_all: If True, export all objects in the scene (ignores object_names and export_selected)
    
    Returns a dictionary with success status and information about the exported file.
    """
    import maya.cmds as cmds
    
    # Validate filepath
    if not filepath or not isinstance(filepath, str):
        raise ValueError("Error: filepath must be a non-empty string")
    
    # Normalize filepath (convert backslashes to forward slashes for Maya)
    filepath = filepath.replace('\\', '/')
    
    # Get directory and ensure it exists
    directory = os.path.dirname(filepath)
    if directory and not os.path.exists(directory):
        try:
            os.makedirs(directory, exist_ok=True)
        except Exception as e:
            raise ValueError(f"Error: Cannot create directory {directory}: {str(e)}")
    
    # Determine objects to export
    objects_to_export = []
    
    if export_all:
        # Export all transform objects
        objects_to_export = cmds.ls(type='transform') or []
        # Filter out default cameras and system objects
        objects_to_export = [obj for obj in objects_to_export 
                           if obj not in ['front', 'side', 'top', 'persp']]
    elif export_selected:
        # Export selected objects
        selected = cmds.ls(selection=True) or []
        objects_to_export = [obj for obj in selected if cmds.objectType(obj) == 'transform']
    else:
        # Export specified objects
        if not object_names:
            raise ValueError("Error: Must specify object_names, or set export_selected=True or export_all=True")
        
        for obj_name in object_names:
            if not cmds.objExists(obj_name):
                raise ValueError(f"Error: Object '{obj_name}' does not exist in the scene")
            objects_to_export.append(obj_name)
    
    if not objects_to_export:
        raise ValueError("Error: No objects to export")
    
    # Validate file format
    file_format = file_format.lower()
    supported_formats = ['fbx', 'obj', 'usd', 'usda', 'usdc', 'alembic', 'abc', 'dae', 'ma', 'mb']
    
    if file_format not in supported_formats:
        raise ValueError(f"Error: Unsupported format '{file_format}'. Supported formats: {', '.join(supported_formats)}")
    
    try:
        # Store current selection
        previous_selection = cmds.ls(selection=True) or []
        
        # Select objects to export
        cmds.select(objects_to_export, replace=True)
        
        # Export based on format
        if file_format == 'fbx':
            # Export as FBX
            cmds.file(filepath, force=True, options="v=0;", type="FBX export", exportSelected=True)
            
        elif file_format == 'obj':
            # Export as OBJ
            cmds.file(filepath, force=True, options="groups=1;ptgroups=1;materials=1;smoothing=1;normals=1", 
                     type="OBJexport", exportSelected=True)
            
        elif file_format in ['usd', 'usda', 'usdc']:
            # Export as USD (requires USD plugin)
            try:
                if file_format == 'usda':
                    cmds.file(filepath, force=True, type="USD Export", exportSelected=True, 
                             options="exportUVs=1;exportColorSets=1;exportDisplayColor=1;defaultUSDFormat=usda")
                elif file_format == 'usdc':
                    cmds.file(filepath, force=True, type="USD Export", exportSelected=True,
                             options="exportUVs=1;exportColorSets=1;exportDisplayColor=1;defaultUSDFormat=usdc")
                else:
                    cmds.file(filepath, force=True, type="USD Export", exportSelected=True,
                             options="exportUVs=1;exportColorSets=1;exportDisplayColor=1")
            except Exception as e:
                raise RuntimeError(f"USD export failed. Make sure USD plugin is loaded: {str(e)}")
                
        elif file_format in ['alembic', 'abc']:
            # Export as Alembic
            try:
                cmds.file(filepath, force=True, type="Alembic", exportSelected=True,
                         options="-frameRange 1 1 -step 1.0 -writeUVSets -writeFaceSets -writeColorSets -writeCreases -dataFormat ogawa")
            except Exception as e:
                raise RuntimeError(f"Alembic export failed. Make sure Alembic plugin is loaded: {str(e)}")
                
        elif file_format == 'dae':
            # Export as Collada DAE
            try:
                cmds.file(filepath, force=True, type="DAE_FBX export", exportSelected=True)
            except:
                # Fallback to FBX if DAE not available
                cmds.file(filepath, force=True, type="FBX export", exportSelected=True)
                
        elif file_format == 'ma':
            # Export as Maya ASCII
            cmds.file(filepath, force=True, type="mayaAscii", exportSelected=True)
            
        elif file_format == 'mb':
            # Export as Maya Binary
            cmds.file(filepath, force=True, type="mayaBinary", exportSelected=True)
        
        # Restore previous selection
        cmds.select(previous_selection, replace=True)
        
        # Verify file was created
        if not os.path.exists(filepath):
            raise RuntimeError(f"Export completed but file was not created at {filepath}")
        
        file_size = os.path.getsize(filepath)
        
        result = {
            "success": True,
            "filepath": filepath,
            "format": file_format,
            "exported_objects": objects_to_export,
            "object_count": len(objects_to_export),
            "file_size_bytes": file_size
        }
        
        return result
        
    except Exception as e:
        # Restore selection on error
        try:
            cmds.select(previous_selection, replace=True)
        except:
            pass
        raise RuntimeError(f"Error exporting model: {str(e)}")
