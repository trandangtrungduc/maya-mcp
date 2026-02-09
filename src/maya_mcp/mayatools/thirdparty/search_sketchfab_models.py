from typing import Dict, Any, Optional


def search_sketchfab_models(
    query: str,
    categories: Optional[str] = None,
    count: int = 20,
    downloadable: bool = True,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """Search for models on Sketchfab with optional filtering.
    
    Sketchfab is a platform for publishing, sharing, and discovering 3D content.
    Requires a Sketchfab API key (can be set via SKETCHFAB_API_KEY environment variable).
    
    Parameters:
    - query: Text to search for
    - categories: Optional comma-separated list of categories
    - count: Maximum number of results to return (default: 20, max: 100)
    - downloadable: Whether to include only downloadable models (default: True)
    - api_key: Optional Sketchfab API key. If not provided, will try to get from environment variable SKETCHFAB_API_KEY
    
    Returns a dictionary with search results including model UIDs, names, descriptions, and metadata.
    """
    import os
    import requests
    
    try:
        # Get API key
        if not api_key:
            api_key = os.getenv("SKETCHFAB_API_KEY")
        
        if not api_key:
            return {
                "success": False,
                "error": "Sketchfab API key is not configured. Set SKETCHFAB_API_KEY environment variable or provide api_key parameter."
            }
        
        # Build search parameters
        params = {
            "type": "models",
            "q": query,
            "count": min(count, 100),  # Limit to 100 max
            "downloadable": downloadable,
            "archives_flavours": False
        }
        
        if categories:
            params["categories"] = categories
        
        # Make API request
        headers = {
            "Authorization": f"Token {api_key}"
        }
        
        response = requests.get(
            "https://api.sketchfab.com/v3/search",
            headers=headers,
            params=params,
            timeout=30
        )
        
        if response.status_code == 401:
            return {
                "success": False,
                "error": "Authentication failed (401). Check your API key."
            }
        
        if response.status_code != 200:
            return {
                "success": False,
                "error": f"API request failed with status code {response.status_code}"
            }
        
        response_data = response.json()
        
        if response_data is None:
            return {
                "success": False,
                "error": "Received empty response from Sketchfab API"
            }
        
        results = response_data.get("results", [])
        if not isinstance(results, list):
            return {
                "success": False,
                "error": f"Unexpected response format from Sketchfab API"
            }
        
        # Format results for easier use
        formatted_results = []
        for model in results:
            formatted_results.append({
                "uid": model.get("uid"),
                "name": model.get("name"),
                "description": model.get("description", ""),
                "downloadable": model.get("isDownloadable", False),
                "view_count": model.get("viewCount", 0),
                "like_count": model.get("likeCount", 0),
                "download_count": model.get("downloadCount", 0),
                "categories": model.get("categories", []),
                "tags": model.get("tags", []),
                "thumbnail_url": model.get("thumbnails", {}).get("images", [{}])[0].get("url", "") if model.get("thumbnails", {}).get("images") else ""
            })
        
        return {
            "success": True,
            "query": query,
            "results": formatted_results,
            "total_count": len(formatted_results),
            "has_more": response_data.get("next", None) is not None
        }
        
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "Request timed out. Check your internet connection."
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
