
from typing import Dict, Any, List


def set_object_transform_attributes(
    object_name:str, 
    translate:List[float]=None, 
    rotate:List[float]=None, 
    scale:List[float]=None
) -> Dict[str, Any]:
    """ set an objects transform attributes. Only specify which attribute needs to change.
        Arguments translate, rotate, and scale are a 3d vector and needs to be a list of
        3 floating point values. Rotate values are in degrees. """

    import maya.cmds as cmds

    def _validate_and_normalize_vector3d(vec:List[float]):
        """Validate and normalize a 3D vector, accepting both int and float values"""
        if not isinstance(vec, list) or len(vec) != 3:
            return None
        # Check if all values are numeric (int or float)
        try:
            normalized = [float(v) for v in vec]
            return normalized
        except (ValueError, TypeError):
            return None

    if not cmds.objExists(object_name):
        raise ValueError(f"{object_name} doesn't exist in the scene")
    if not cmds.attributeQuery('translate', node=object_name, exists=True):
        raise ValueError(f"{object_name} doesn't have any transform attributes")

    if not translate and not rotate and not scale:
        raise ValueError("Must set at least one of the transform values (translate, rotate, or scale).")
    
    # Validate and normalize translate
    if translate:
        normalized_translate = _validate_and_normalize_vector3d(translate)
        if normalized_translate is None:
            raise ValueError("Invalid translate format. Must be a list of 3 numeric values (int or float).")
        translate = normalized_translate
    
    # Validate and normalize rotate
    if rotate:
        normalized_rotate = _validate_and_normalize_vector3d(rotate)
        if normalized_rotate is None:
            raise ValueError("Invalid rotate format. Must be a list of 3 numeric values (int or float) in degrees.")
        rotate = normalized_rotate
    
    # Validate and normalize scale
    if scale:
        normalized_scale = _validate_and_normalize_vector3d(scale)
        if normalized_scale is None:
            raise ValueError("Invalid scale format. Must be a list of 3 numeric values (int or float).")
        scale = normalized_scale

    try:
        if translate:
            cmds.setAttr(f'{object_name}.translate', translate[0], translate[1], translate[2], type="double3")
        if rotate:
            cmds.setAttr(f'{object_name}.rotate', rotate[0], rotate[1], rotate[2], type="double3")
        if scale:
            cmds.setAttr(f'{object_name}.scale', scale[0], scale[1], scale[2], type="double3")
        results = { "success": True }
    except Exception as e:
        raise RuntimeError(f"Unable to update the transform attributes on object_name {object_name}")

    return results
    
