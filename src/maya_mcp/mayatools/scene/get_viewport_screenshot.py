import os
import tempfile
import base64
from typing import Dict, Any

def get_viewport_screenshot(max_size: int = 800) -> Dict[str, Any]:
    """Capture a screenshot of the current Maya 3D viewport.
    
    This function captures the active viewport and returns it as an image
    that can be analyzed by AI to understand the current scene state.
    
    Parameters:
    - max_size: Maximum size in pixels for the largest dimension (default: 800)
    
    Returns a dictionary with image data that will be converted to an Image object
    by the MCP server.
    """
    import maya.cmds as cmds
    
    try:
        # Create a temporary file for the screenshot
        # Use forward slashes to avoid backslash issues in MEL encoding
        temp_dir = tempfile.gettempdir().replace('\\', '/')
        pid = os.getpid()
        temp_file = temp_dir + '/maya_screenshot_' + str(pid) + '.png'
        
        # Get the active viewport panel
        active_panel = cmds.getPanel(withFocus=True)
        
        # If no active panel or not a model panel, try to find a model panel
        if not active_panel or cmds.getPanel(typeOf=active_panel) != 'modelPanel':
            # Find the first model panel
            model_panels = cmds.getPanel(type='modelPanel')
            if model_panels:
                active_panel = model_panels[0]
            else:
                return {
                    "_mcp_error": True,
                    "message": "No active 3D viewport found. Please ensure a 3D viewport is open."
                }
        
        # Get viewport dimensions to calculate proper size
        try:
            # Get the model editor's camera
            cam = cmds.modelEditor(active_panel, query=True, camera=True)
            
            # Get viewport size (approximate, as we can't easily get exact pixel size)
            # We'll use playblast with percent to control size
            viewport_width = max_size
            viewport_height = max_size
            
        except:
            viewport_width = max_size
            viewport_height = max_size
        
        # Capture the viewport using playblast
        # playblast captures the current frame from the active viewport
        try:
            # Calculate percent to get approximately max_size
            # playblast percent is relative to viewport size, so we use 100% and let widthHeight handle it
            # Use format='image' to get a single image file (not a sequence)
            # frame=cmds.currentTime(query=True) captures current frame
            # viewer=False prevents opening the viewer
            # showOrnaments=False hides UI elements like grid, axis, etc.
            # compression='png' for lossless quality
            # quality=100 for best quality
            
            # Note: playblast may add frame numbers to filename, so we'll search for the actual file
            result = cmds.playblast(
                format='image',
                filename=temp_file,
                frame=cmds.currentTime(query=True),
                viewer=False,
                showOrnaments=False,
                percent=100,
                compression='png',
                quality=100,
                widthHeight=[viewport_width, viewport_height],
                forceOverwrite=True
            )
            
            # playblast might return a different filename or add frame numbers
            # Find the actual created file
            # Use os.path methods but convert to forward slashes for consistency
            base_name = os.path.splitext(temp_file)[0].replace('\\', '/')
            dir_name = os.path.dirname(temp_file).replace('\\', '/')
            actual_file = None
            
            # First check if exact file exists (convert to native path for os.path.exists)
            temp_file_native = temp_file.replace('/', os.sep)
            if os.path.exists(temp_file_native):
                actual_file = temp_file_native
            else:
                # Look for files matching the pattern (playblast may add frame numbers)
                dir_name_native = dir_name.replace('/', os.sep)
                if os.path.exists(dir_name_native):
                    base_name_only = os.path.basename(base_name)
                    for file in os.listdir(dir_name_native):
                        if file.startswith(base_name_only) and file.endswith('.png'):
                            actual_file = os.path.join(dir_name_native, file)
                            break
            
            if not actual_file or not os.path.exists(actual_file):
                return {
                    "_mcp_error": True,
                    "message": "Screenshot file was not created"
                }
            
        except Exception as e:
            error_str = str(e)
            return {
                "_mcp_error": True,
                "message": "Failed to capture screenshot: " + error_str
            }
        
        # Read the image file (use native path for file operations)
        if not actual_file or not os.path.exists(actual_file):
            return {
                "_mcp_error": True,
                "message": "Screenshot file was not created"
            }
        
        # Read the image file as binary
        with open(actual_file, 'rb') as f:
            image_bytes = f.read()
        
        # Clean up temp file
        try:
            os.remove(actual_file)
        except:
            pass
        
        # Encode image as base64 for JSON transmission
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Return special format that server will recognize
        return {
            "_mcp_image_data": image_base64,
            "_mcp_image_format": "png",
            "_mcp_image_type": "base64"
        }
        
    except Exception as e:
        import traceback
        error_str = str(e)
        traceback_str = traceback.format_exc()
        error_msg = "Error capturing viewport screenshot: " + error_str + "\n" + traceback_str
        return {
            "_mcp_error": True,
            "message": error_msg
        }
