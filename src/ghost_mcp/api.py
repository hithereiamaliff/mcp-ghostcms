"""Ghost API interaction utilities.

This module provides functions for interacting with the Ghost Admin API, including
JWT token generation, authentication, and making HTTP requests with proper error handling.
"""

import datetime
from typing import Dict, Any, Optional, Union
import httpx
import jwt
from mcp.server.fastmcp import Context

from .config import API_URL
from .exceptions import GhostError

# HTTP Methods
GET = "GET"
POST = "POST"
PUT = "PUT"
DELETE = "DELETE"

VALID_HTTP_METHODS = {GET, POST, PUT, DELETE}

# Default Ghost API version
DEFAULT_API_VERSION = "v5.109"

async def generate_token(staff_api_key: str, audience: str = "/admin/") -> str:
    """Generate a JWT token for Ghost Admin API authentication.
    
    Args:
        staff_api_key: API key in 'id:secret' format (e.g. "1234:abcd5678")
        audience: Token audience (default: "/admin/")
        
    Returns:
        JWT token string for use in Authorization header
        
    Raises:
        ValueError: If staff_api_key is not in correct 'id:secret' format
        
    Example:
        >>> token = await generate_token("1234:abcd5678")
        >>> print(token)
        'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1...'
    """
    try:
        key_id, secret = staff_api_key.split(":")
    except ValueError:
        raise ValueError("STAFF_API_KEY must be in the format 'id:secret'") 
        
    if not all([key_id, secret]):
        raise ValueError("Both key ID and secret are required")
    
    try:
        secret_bytes = bytes.fromhex(secret)
    except ValueError:
        raise ValueError("Invalid secret format - must be hexadecimal")
    
    now = datetime.datetime.now(datetime.UTC)
    exp = now + datetime.timedelta(minutes=5)
    
    payload = {
        "iat": now,
        "exp": exp,
        "aud": audience,
        "sub": key_id,  # Add subject claim
        "typ": "ghost-admin"  # Add token type
    }
    
    token = jwt.encode(payload, secret_bytes, algorithm="HS256", headers={"kid": key_id})
    
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    
    return token

async def get_auth_headers(
    staff_api_key: str,
    api_version: str = DEFAULT_API_VERSION
) -> Dict[str, str]:
    """Get authenticated headers for Ghost API requests.
    
    Args:
        staff_api_key: API key in 'id:secret' format
        api_version: Ghost API version to use (default: v5.109)
        
    Returns:
        Dictionary of request headers including authorization and version
        
    Example:
        >>> headers = await get_auth_headers("1234:abcd5678")
        >>> headers
        {
            'Authorization': 'Ghost eyJ0eXAiOiJKV1...',
            'Accept-Version': 'v5.109'
        }
    """
    token = await generate_token(staff_api_key)
    return {
        "Authorization": f"Ghost {token}",
        "Accept-Version": api_version,
        "Content-Type": "application/json"
    }

async def make_ghost_request(
    endpoint: str,
    headers: Dict[str, str],
    ctx: Optional[Context] = None,
    is_resource: bool = False,
    http_method: str = GET,
    json_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Make an authenticated request to the Ghost API.
    
    Args:
        endpoint: API endpoint to call (e.g. "posts" or "users")
        headers: Request headers from get_auth_headers()
        ctx: Optional context for logging (not used for resources)
        is_resource: Whether this request is for a resource
        http_method: HTTP method to use (GET, POST, PUT, or DELETE)
        json_data: Optional JSON data for POST/PUT requests
        
    Returns:
        Parsed JSON response from the Ghost API
        
    Raises:
        GhostError: For any Ghost API errors including:
            - Network connectivity issues
            - Invalid authentication
            - Rate limiting
            - Server errors
        ValueError: For invalid HTTP methods
        
    Example:
        >>> headers = await get_auth_headers("1234:abcd5678")
        >>> response = await make_ghost_request(
        ...     "posts",
        ...     headers,
        ...     http_method=GET
        ... )
    """
    # Validate HTTP method
    http_method = http_method.upper()
    if http_method not in VALID_HTTP_METHODS:
        raise ValueError(f"Invalid HTTP method: {http_method}")

    # Ensure clean URL construction
    base_url = f"{API_URL.rstrip('/')}/ghost/api/admin"
    endpoint = endpoint.strip('/')
    url = f"{base_url}/{endpoint}"

    async with httpx.AsyncClient(follow_redirects=True) as client:
        try:
            # Map HTTP methods to client methods
            method_map = {
                GET: client.get,
                POST: client.post,
                PUT: client.put,
                DELETE: client.delete
            }
            
            method_func = method_map[http_method]
            
            # Make the request
            if http_method in (POST, PUT):
                response = await method_func(url, headers=headers, json=json_data)
            else:
                response = await method_func(url, headers=headers)
            
            # Handle specific status codes
            if http_method == DELETE and response.status_code == 204:
                return {}
                
            response.raise_for_status()
            
            # Log success if context provided and not a resource request
            if not is_resource and ctx:
                ctx.log("info", f"API Request to {url} successful")
            
            return response.json()
            
        except httpx.HTTPError as e:
            error_msg = f"HTTP error accessing Ghost API: {str(e)}"
            if response := getattr(e, 'response', None):
                error_msg += f" (Status: {response.status_code})"
            if not is_resource and ctx:
                ctx.error(error_msg)
            raise GhostError(error_msg)
            
        except Exception as e:
            error_msg = f"Error accessing Ghost API: {str(e)}"
            if not is_resource and ctx:
                ctx.error(error_msg)
            raise GhostError(error_msg)
