"""Ghost API interaction utilities."""

import datetime
import httpx
import jwt
from typing import Dict, Any
from mcp.server.fastmcp import Context

from .config import API_URL
from .exceptions import GhostError

async def generate_token(staff_api_key: str, audience: str = "/admin/") -> str:
    """Generate a JWT token for Ghost Admin API authentication.
    
    Args:
        staff_api_key: API key in 'id:secret' format
        audience: Token audience (default: "/admin/")
        
    Returns:
        JWT token string
        
    Raises:
        ValueError: If staff_api_key is not in correct format
    """
    try:
        key_id, secret = staff_api_key.split(":")
    except ValueError:
        raise ValueError("STAFF_API_KEY must be in the format 'id:secret'")
    
    secret_bytes = bytes.fromhex(secret)
    now = datetime.datetime.now(datetime.UTC)
    exp = now + datetime.timedelta(minutes=5)
    
    payload = {
        "iat": now,
        "exp": exp,
        "aud": audience
    }
    
    token = jwt.encode(payload, secret_bytes, algorithm="HS256", headers={"kid": key_id})
    
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    
    return token

async def get_auth_headers(staff_api_key: str) -> Dict[str, str]:
    """Get authenticated headers for Ghost API requests.
    
    Args:
        staff_api_key: API key in 'id:secret' format
        
    Returns:
        Dictionary of request headers
    """
    token = await generate_token(staff_api_key)
    return {
        "Authorization": f"Ghost {token}",
        "Accept-Version": "v5"
    }

async def make_ghost_request(
    endpoint: str,
    headers: Dict[str, str],
    ctx: Context = None,
    is_resource: bool = False
) -> Dict[str, Any]:
    """Make an authenticated request to the Ghost API.
    
    Args:
        endpoint: API endpoint to call
        headers: Request headers
        ctx: Optional context for logging (not used for resources)
        is_resource: Whether this request is for a resource
        
    Returns:
        Parsed JSON response
        
    Raises:
        GhostError: If there is an error accessing the Ghost API
    """
    # Ensure clean URL construction with proper trailing slashes
    base_url = f"{API_URL.rstrip('/')}/ghost/api/admin"
    endpoint = endpoint.strip('/')
    url = f"{base_url}/{endpoint}/"
    
    async with httpx.AsyncClient(follow_redirects=True) as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            if not is_resource and ctx:
                ctx.log("info", f"API Request to {url} successful")
            return response.json()
        except httpx.HTTPError as e:
            error_msg = f"HTTP error accessing Ghost API: {str(e)}"
            if not is_resource and ctx:
                ctx.error(error_msg)
            raise GhostError(error_msg)
        except Exception as e:
            error_msg = f"Error accessing Ghost API: {str(e)}"
            if not is_resource and ctx:
                ctx.error(error_msg)
            raise GhostError(error_msg)
