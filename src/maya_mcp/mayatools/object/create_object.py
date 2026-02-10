
from typing import Dict, List, Any


def create_object(
    name:str, 
    object_type:str, 
    translate:List[float]=[0.0, 0.0, 0.0], 
    rotate:List[float]=[0.0, 0.0, 0.0],
) -> Dict[str, Any]:
    """ Creates an object in the Maya scene. Object types available are
        cube, cone, sphere, cylinder, camera, spotLight, pointLight, directionalLight.
        Rotate values are in degrees. """
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

    # Validate and normalize translate
    normalized_translate = _validate_and_normalize_vector3d(translate)
    if normalized_translate is None:
        raise ValueError("Invalid translate format. Must be a list of 3 numeric values (int or float).")
    translate = normalized_translate
    
    # Validate and normalize rotate
    normalized_rotate = _validate_and_normalize_vector3d(rotate)
    if normalized_rotate is None:
        raise ValueError("Invalid rotate format. Must be a list of 3 numeric values (int or float).")
    rotate = normalized_rotate

    if object_type == "cube":
        obj = cmds.polyCube(name=name)
    elif object_type == "cone":
        obj = cmds.polyCone(name=name)
    elif object_type == "sphere":
        obj = cmds.polySphere(name=name)
    elif object_type == "cylinder":
        obj = cmds.polyCylinder(name=name)
    elif object_type == "camera":
        obj = cmds.camera(name=name)
    elif object_type == "spotLight":
        obj = cmds.spotLight(name=name)
    elif object_type == "pointLight":
        obj = cmds.pointLight(name=name)
    elif object_type == "directionalLight":
        obj = cmds.directionalLight(name=name)
    else:
        raise ValueError(f"Error: unknown {object_type}, use one of these types: cube, cone, sphere, cylinder, camera, spotLight, pointLight, directionalLight")

    cmds.setAttr(obj[0]+".translate", translate[0], translate[1], translate[2], type="double3")
    cmds.setAttr(obj[0]+".rotate", rotate[0], rotate[1], rotate[2], type="double3")

    return {
        "success": True,
        "name": obj[0],
        "shape": obj[1],
        "object_type": object_type,
        "translate": translate,
        "rotate": rotate,
    }
        

