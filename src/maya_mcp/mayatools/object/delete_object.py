from typing import Dict, Any, List


def delete_object(object_names: List[str]) -> Dict[str, Any]:
    """Delete one or more objects from the Maya scene.
    
    Parameters:
    - object_names: List of object names to delete. Can be a single object or multiple objects.
    
    Returns a dictionary with success status and information about deleted objects.
    """
    import maya.cmds as cmds
    
    if not object_names:
        raise ValueError("Error: object_names list cannot be empty")
    
    if not isinstance(object_names, list):
        raise ValueError("Error: object_names must be a list")
    
    deleted_objects = []
    failed_objects = []
    
    for obj_name in object_names:
        if not isinstance(obj_name, str):
            failed_objects.append({"name": str(obj_name), "error": "Object name must be a string"})
            continue
            
        if not cmds.objExists(obj_name):
            failed_objects.append({"name": obj_name, "error": "Object does not exist"})
            continue
        
        try:
            # Get object type before deletion for reporting
            obj_type = cmds.objectType(obj_name)
            
            # Delete the object
            cmds.delete(obj_name)
            
            deleted_objects.append({
                "name": obj_name,
                "type": obj_type
            })
        except Exception as e:
            failed_objects.append({
                "name": obj_name,
                "error": str(e)
            })
    
    result = {
        "success": len(failed_objects) == 0,
        "deleted_count": len(deleted_objects),
        "deleted_objects": deleted_objects
    }
    
    if failed_objects:
        result["failed_objects"] = failed_objects
        if len(deleted_objects) == 0:
            raise RuntimeError(f"Failed to delete all objects: {failed_objects}")
    
    return result
