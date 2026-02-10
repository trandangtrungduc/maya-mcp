from typing import Dict, Any
import io
import contextlib

def execute_code(code: str) -> Dict[str, Any]:
    """Execute arbitrary Python code in Maya. This allows AI to execute custom code
    to understand context, perform complex operations, or work around limitations.
    
    The code will be executed in Maya's Python environment with access to all
    Maya modules (maya.cmds, maya.mel, etc.). Output from print statements and
    stdout will be captured and returned.
    
    Parameters:
    - code: The Python code to execute in Maya
    
    Returns:
    - Dictionary with 'success' status, 'result' (stdout output), and 'error' if any
    
    Example:
    execute_code("import maya.cmds as cmds; print('Objects:', cmds.ls())")
    """
    import maya.cmds as cmds
    import traceback
    
    # Capture stdout during execution
    capture_buffer = io.StringIO()
    
    try:
        # Create a namespace with Maya modules available
        namespace = {
            'maya': __import__('maya'),
            'cmds': cmds,
            'mel': __import__('maya.mel').mel,
            'OpenMaya': __import__('maya.OpenMaya'),
        }
        
        # Try to import other common Maya modules
        try:
            namespace['api'] = __import__('maya.api.OpenMaya')
        except:
            pass
        
        try:
            namespace['utils'] = __import__('maya.utils')
        except:
            pass
        
        # Execute the code with stdout capture
        with contextlib.redirect_stdout(capture_buffer):
            exec(code, namespace)
        
        captured_output = capture_buffer.getvalue()
        
        return {
            "success": True,
            "result": captured_output if captured_output else "Code executed successfully (no output)",
            "error": None
        }
        
    except Exception as e:
        # Capture error traceback
        error_buffer = io.StringIO()
        traceback.print_exc(file=error_buffer)
        error_traceback = error_buffer.getvalue()
        
        # Also get any stdout that was captured before the error
        captured_output = capture_buffer.getvalue()
        
        return {
            "success": False,
            "result": captured_output if captured_output else "",
            "error": str(e),
            "traceback": error_traceback
        }
