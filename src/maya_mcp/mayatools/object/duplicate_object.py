from typing import Dict, Any, List, Optional


def duplicate_object(
    object_name: str,
    new_name: Optional[str] = None,
    translate: Optional[List[float]] = None,
    rotate: Optional[List[float]] = None,
    scale: Optional[List[float]] = None,
    instance: bool = False
) -> Dict[str, Any]:
    """Duplicate an object in the Maya scene.
    
    Parameters:
    - object_name: Name of the object to duplicate
    - new_name: Optional new name for the duplicated object. If not provided, Maya will auto-generate a name.
    - translate: Optional translation offset for the duplicate [x, y, z]. Default is [0, 0, 0] (same position).
    - rotate: Optional rotation offset for the duplicate [x, y, z] in degrees. Default is [0, 0, 0].
    - scale: Optional scale for the duplicate [x, y, z]. Default is [1, 1, 1] (same scale).
    - instance: If True, create an instance instead of a full duplicate. Instances share geometry but can have different transforms.
    
    Returns a dictionary with success status and information about the duplicated object.
    """
    import maya.cmds as cmds
    
    def _validate_vector3d(vec: List[float], name: str):
        if not isinstance(vec, list) or len(vec) != 3:
            raise ValueError(f"Error: {name} must be a list of 3 float values")
        if not all([isinstance(v, (int, float)) for v in vec]):
            raise ValueError(f"Error: {name} must contain numeric values")
        return [float(v) for v in vec]
    
    if not object_name or not isinstance(object_name, str):
        raise ValueError("Error: object_name must be a non-empty string")
    
    if not cmds.objExists(object_name):
        raise ValueError(f"Error: Object '{object_name}' does not exist in the scene")
    
    # Validate and set default values for transforms
    if translate is None:
        translate = [0.0, 0.0, 0.0]
    else:
        translate = _validate_vector3d(translate, "translate")
    
    if rotate is None:
        rotate = [0.0, 0.0, 0.0]
    else:
        rotate = _validate_vector3d(rotate, "rotate")
    
    if scale is None:
        scale = [1.0, 1.0, 1.0]
    else:
        scale = _validate_vector3d(scale, "scale")
    
    try:
        # Get original object info
        obj_type = cmds.objectType(object_name)
        original_translate = cmds.getAttr(f"{object_name}.translate")[0]
        original_rotate = cmds.getAttr(f"{object_name}.rotate")[0]
        
        # Duplicate the object
        if instance:
            duplicated = cmds.instance(object_name, name=new_name if new_name else None)
        else:
            duplicated = cmds.duplicate(object_name, name=new_name if new_name else None)
        
        # Handle return value (duplicate can return a list)
        if isinstance(duplicated, list):
            duplicated_name = duplicated[0]
        else:
            duplicated_name = duplicated
        
        # Apply transform offset
        if translate != [0.0, 0.0, 0.0]:
            new_translate = [
                original_translate[0] + translate[0],
                original_translate[1] + translate[1],
                original_translate[2] + translate[2]
            ]
            cmds.setAttr(f"{duplicated_name}.translate", new_translate[0], new_translate[1], new_translate[2], type="double3")
        
        if rotate != [0.0, 0.0, 0.0]:
            new_rotate = [
                original_rotate[0] + rotate[0],
                original_rotate[1] + rotate[1],
                original_rotate[2] + rotate[2]
            ]
            cmds.setAttr(f"{duplicated_name}.rotate", new_rotate[0], new_rotate[1], new_rotate[2], type="double3")
        
        if scale != [1.0, 1.0, 1.0]:
            cmds.setAttr(f"{duplicated_name}.scale", scale[0], scale[1], scale[2], type="double3")
        
        # Get final transform values
        final_translate = cmds.getAttr(f"{duplicated_name}.translate")[0]
        final_rotate = cmds.getAttr(f"{duplicated_name}.rotate")[0]
        final_scale = cmds.getAttr(f"{duplicated_name}.scale")[0]
        
        result = {
            "success": True,
            "original_name": object_name,
            "duplicated_name": duplicated_name,
            "type": obj_type,
            "is_instance": instance,
            "translate": list(final_translate),
            "rotate": list(final_rotate),
            "scale": list(final_scale)
        }
        
        return result
        
    except Exception as e:
        raise RuntimeError(f"Error: Unable to duplicate object '{object_name}': {str(e)}")
