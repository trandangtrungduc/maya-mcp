from typing import Dict, Any


def rename_object(object_name: str, new_name: str) -> Dict[str, Any]:
    """Rename an object in the Maya scene.
    
    Parameters:
    - object_name: Current name of the object to rename
    - new_name: New name for the object
    
    Returns a dictionary with success status and the new object name.
    Note: Maya may modify the name if it conflicts with existing objects.
    """
    import maya.cmds as cmds
    
    if not object_name or not isinstance(object_name, str):
        raise ValueError("Error: object_name must be a non-empty string")
    
    if not new_name or not isinstance(new_name, str):
        raise ValueError("Error: new_name must be a non-empty string")
    
    if not cmds.objExists(object_name):
        raise ValueError(f"Error: Object '{object_name}' does not exist in the scene")
    
    # Check if new name already exists
    if cmds.objExists(new_name):
        raise ValueError(f"Error: Object with name '{new_name}' already exists in the scene")
    
    try:
        # Rename the object
        # Maya's rename command returns the actual new name (may be modified if conflicts)
        actual_new_name = cmds.rename(object_name, new_name)
        
        # Get object type for reporting
        obj_type = cmds.objectType(actual_new_name)
        
        result = {
            "success": True,
            "old_name": object_name,
            "requested_name": new_name,
            "actual_name": actual_new_name,
            "type": obj_type
        }
        
        # Warn if name was modified
        if actual_new_name != new_name:
            result["warning"] = f"Name was modified from '{new_name}' to '{actual_new_name}' due to naming conflicts"
        
        return result
        
    except Exception as e:
        raise RuntimeError(f"Error: Unable to rename object '{object_name}' to '{new_name}': {str(e)}")
