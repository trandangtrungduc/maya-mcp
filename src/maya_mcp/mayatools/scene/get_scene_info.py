from typing import Dict, Any, List, Optional

def get_scene_info() -> Dict[str, Any]:
    """Get detailed information about the current Maya scene including
    all objects, cameras, lights, materials, and scene settings.
    
    This provides a comprehensive overview of the scene that can be used
    to understand the current state before performing operations.
    
    Returns a dictionary containing:
    - scene_name: Current scene file name or "Untitled"
    - object_count: Total number of transform objects
    - objects: List of all objects with their properties (name, type, position, rotation, scale, bounding box, visibility)
    - cameras: List of all cameras in the scene
    - lights: List of all lights in the scene
    - materials: List of all materials/shaders in the scene
    - timeline: Timeline settings (start frame, end frame, current frame, FPS)
    """
    import maya.cmds as cmds
    
    # Get scene file info
    scene_name = cmds.file(query=True, sceneName=True) or "Untitled"
    
    # Get all transform objects (these are the main objects in the scene)
    all_transforms = cmds.ls(type='transform') or []
    
    objects = []
    for obj in all_transforms:
        try:
            # Skip default cameras and other system objects if desired
            # (uncomment if you want to filter them out)
            # if obj in ['front', 'side', 'top', 'persp']:
            #     continue
            
            obj_type = cmds.objectType(obj)
            shapes = cmds.listRelatives(obj, shapes=True) or []
            shape_type = None
            if shapes:
                try:
                    shape_type = cmds.objectType(shapes[0])
                except:
                    pass
            
            # Get transform attributes
            try:
                pos = cmds.xform(obj, query=True, worldSpace=True, translation=True)
            except:
                pos = [0.0, 0.0, 0.0]
                
            try:
                rot = cmds.xform(obj, query=True, worldSpace=True, rotation=True)
            except:
                rot = [0.0, 0.0, 0.0]
                
            try:
                scl = cmds.xform(obj, query=True, worldSpace=True, scale=True)
            except:
                scl = [1.0, 1.0, 1.0]
                
            try:
                bbox = cmds.xform(obj, query=True, worldSpace=True, boundingBox=True)
            except:
                bbox = None
            
            # Get visibility
            visible = True
            if cmds.attributeQuery("visibility", node=obj, exists=True):
                try:
                    visible = cmds.getAttr(f"{obj}.visibility")
                except:
                    pass
            
            objects.append({
                "name": obj,
                "type": shape_type or obj_type,
                "position": pos,
                "rotation": rot,
                "scale": scl,
                "bounding_box": bbox,
                "visible": visible
            })
        except Exception as e:
            # Skip objects that cause errors
            continue
    
    # Get timeline settings
    try:
        start_frame = cmds.playbackOptions(query=True, minTime=True)
        end_frame = cmds.playbackOptions(query=True, maxTime=True)
        current_frame = cmds.currentTime(query=True)
        fps = cmds.currentUnit(query=True, time=True)
    except:
        start_frame = end_frame = current_frame = fps = None
    
    time_info = {
        "start_frame": start_frame,
        "end_frame": end_frame,
        "current_frame": current_frame,
        "fps": fps
    }
    
    # Get cameras
    cameras = []
    try:
        camera_shapes = cmds.ls(type='camera') or []
        for cam_shape in camera_shapes:
            cam_transform = cmds.listRelatives(cam_shape, parent=True)[0] if cmds.listRelatives(cam_shape, parent=True) else cam_shape
            cameras.append(cam_transform)
    except:
        pass
    
    # Get lights
    lights = []
    try:
        light_types = ['directionalLight', 'pointLight', 'spotLight', 'areaLight', 
                       'aiAreaLight', 'aiSkyDomeLight', 'aiLightPortal', 'aiMeshLight']
        for light_type in light_types:
            light_shapes = cmds.ls(type=light_type) or []
            for light_shape in light_shapes:
                light_transform = cmds.listRelatives(light_shape, parent=True)[0] if cmds.listRelatives(light_shape, parent=True) else light_shape
                if light_transform not in lights:
                    lights.append(light_transform)
    except:
        pass
    
    # Get materials/shaders
    materials = []
    try:
        materials = cmds.ls(materials=True) or []
    except:
        pass
    
    return {
        "scene_name": scene_name,
        "object_count": len(objects),
        "objects": objects,
        "cameras": cameras,
        "lights": lights,
        "materials": materials,
        "timeline": time_info
    }
