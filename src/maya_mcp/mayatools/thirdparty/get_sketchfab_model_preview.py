import os
import base64
from typing import Dict, Any, Optional


def get_sketchfab_model_preview(
    uid: str,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """Get a preview thumbnail image of a Sketchfab model by its UID.
    
    Use this to visually confirm a model before downloading.
    
    Parameters:
    - uid: The unique identifier of the Sketchfab model
    - api_key: Optional Sketchfab API key. If not provided, will try to get from environment variable SKETCHFAB_API_KEY
    
    Returns a dictionary with base64-encoded image data that will be converted to an Image object by the MCP server.
    """
    import requests
    
    try:
        # Get API key
        if not api_key:
            api_key = os.getenv("SKETCHFAB_API_KEY")
        
        if not api_key:
            return {
                "_mcp_error": True,
                "message": "Sketchfab API key is not configured. Set SKETCHFAB_API_KEY environment variable or provide api_key parameter."
            }
        
        headers = {"Authorization": f"Token {api_key}"}
        
        # Get model info which includes thumbnails
        response = requests.get(
            f"https://api.sketchfab.com/v3/models/{uid}",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 401:
            return {
                "_mcp_error": True,
                "message": "Authentication failed (401). Check your API key."
            }
        
        if response.status_code == 404:
            return {
                "_mcp_error": True,
                "message": f"Model not found: {uid}"
            }
        
        if response.status_code != 200:
            return {
                "_mcp_error": True,
                "message": f"Failed to get model info: {response.status_code}"
            }
        
        data = response.json()
        thumbnails = data.get("thumbnails", {}).get("images", [])
        
        if not thumbnails:
            return {
                "_mcp_error": True,
                "message": "No thumbnail available for this model"
            }
        
        # Find a suitable thumbnail (prefer medium size ~640px)
        selected_thumbnail = None
        for thumb in thumbnails:
            width = thumb.get("width", 0)
            if 400 <= width <= 800:
                selected_thumbnail = thumb
                break
        
        # Fallback to the first available thumbnail
        if not selected_thumbnail:
            selected_thumbnail = thumbnails[0]
        
        thumbnail_url = selected_thumbnail.get("url")
        if not thumbnail_url:
            return {
                "_mcp_error": True,
                "message": "Thumbnail URL not found"
            }
        
        # Download the thumbnail image
        img_response = requests.get(thumbnail_url, timeout=30)
        if img_response.status_code != 200:
            return {
                "_mcp_error": True,
                "message": f"Failed to download thumbnail: {img_response.status_code}"
            }
        
        # Encode image as base64
        image_data = base64.b64encode(img_response.content).decode('ascii')
        
        # Determine format from content type or URL
        content_type = img_response.headers.get("Content-Type", "")
        if "png" in content_type or thumbnail_url.endswith(".png"):
            img_format = "png"
        else:
            img_format = "jpeg"
        
        # Get additional model info for context
        model_name = data.get("name", "Unknown")
        author = data.get("user", {}).get("username", "Unknown")
        
        # Return special format that server will recognize as image
        return {
            "_mcp_image_data": image_data,
            "_mcp_image_format": img_format,
            "_mcp_image_type": "base64",
            "model_name": model_name,
            "author": author,
            "uid": uid
        }
        
    except requests.exceptions.Timeout:
        return {
            "_mcp_error": True,
            "message": "Request timed out. Check your internet connection."
        }
    except Exception as e:
        return {
            "_mcp_error": True,
            "message": f"Failed to get model preview: {str(e)}"
        }
