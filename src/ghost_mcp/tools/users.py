"""User-related MCP tools for Ghost API."""

import json
from mcp.server.fastmcp import Context

from ..api import make_ghost_request, get_auth_headers
from ..config import STAFF_API_KEY
from ..exceptions import GhostError

async def list_users(
    format: str = "text",
    page: int = 1,
    limit: int = 15,
    ctx: Context = None
) -> str:
    """Get the list of users from your Ghost blog.
    
    Args:
        format: Output format - either "text" or "json" (default: "text")
        page: Page number for pagination (default: 1)
        limit: Number of users per page (default: 15)
        ctx: Optional context for logging
    
    Returns:
        Formatted string containing user information
    """
    if ctx:
        ctx.info(f"Listing users (page {page}, limit {limit}, format {format})")
    
    try:
        if ctx:
            ctx.debug("Getting auth headers")
        headers = await get_auth_headers(STAFF_API_KEY)
        
        if ctx:
            ctx.debug(f"Making API request to /users/ with pagination")
        data = await make_ghost_request(
            f"users/?page={page}&limit={limit}&include=roles",
            headers,
            ctx
        )
        
        if ctx:
            ctx.debug("Processing users list response")
        
        users = data.get("users", [])
        if not users:
            if ctx:
                ctx.info("No users found in response")
            return "No users found."

        if format.lower() == "json":
            if ctx:
                ctx.debug("Returning JSON format")
            return json.dumps(users, indent=2)
        
        formatted_users = []
        for user in users:
            roles = [role.get('name') for role in user.get('roles', [])]
            formatted_user = f"""
Name: {user.get('name', 'Unknown')}
Email: {user.get('email', 'Unknown')}
Roles: {', '.join(roles)}
Status: {user.get('status', 'Unknown')}
ID: {user.get('id', 'Unknown')}
"""
            formatted_users.append(formatted_user)
        return "\n---\n".join(formatted_users)
        
    except GhostError as e:
        if ctx:
            ctx.error(f"Failed to list users: {str(e)}")
        return str(e)

async def delete_user(
    user_id: str,
    ctx: Context = None
) -> str:
    """Delete a user from Ghost.
    
    Args:
        user_id: ID of the user to delete (required)
        ctx: Optional context for logging
    
    Returns:
        Success message if deletion was successful

    Raises:
        GhostError: If the Ghost API request fails or if attempting to delete the Owner
        ValueError: If user_id is not provided
    """
    if not user_id:
        raise ValueError("user_id is required")

    if ctx:
        ctx.info(f"Attempting to delete user with ID: {user_id}")

    try:
        # First get the user to check if they are the Owner
        if ctx:
            ctx.debug("Getting user details to check role")
        headers = await get_auth_headers(STAFF_API_KEY)
        
        user_data = await make_ghost_request(
            f"users/{user_id}/",
            headers,
            ctx
        )
        
        user = user_data.get("users", [{}])[0]
        roles = [role.get('name') for role in user.get('roles', [])]
        
        if 'Owner' in roles:
            error_msg = "Cannot delete the Owner user"
            if ctx:
                ctx.error(error_msg)
            raise GhostError(error_msg)
        
        # Proceed with deletion
        if ctx:
            ctx.debug(f"Making API request to delete user {user_id}")
        response = await make_ghost_request(
            f"users/{user_id}/",
            headers,
            ctx,
            http_method="DELETE"
        )
        
        return f"""
Successfully deleted user:
Name: {user.get('name', 'Unknown')}
Email: {user.get('email', 'Unknown')}
"""
    except Exception as e:
        if ctx:
            ctx.error(f"Failed to delete user: {str(e)}")
        raise

async def read_user(user_id: str, ctx: Context = None) -> str:
    """Get the details of a specific user.
  
    Args:
        user_id: The ID of the user to retrieve
        ctx: Optional context for logging
      
    Returns:
        Formatted string containing the user details
    """
    if ctx:
        ctx.info(f"Reading user details for ID: {user_id}")
    
    try:
        if ctx:
            ctx.debug("Getting auth headers")
        headers = await get_auth_headers(STAFF_API_KEY)
        
        if ctx:
            ctx.debug(f"Making API request to /users/{user_id}/")
        data = await make_ghost_request(
            f"users/{user_id}/?include=roles",
            headers,
            ctx
        )
        
        if ctx:
            ctx.debug("Processing user data")
      
        user = data["users"][0]
        roles = [role.get('name') for role in user.get('roles', [])]
      
        return f"""
Name: {user.get('name', 'Unknown')}
Email: {user.get('email', 'Unknown')}
Slug: {user.get('slug', 'Unknown')}
Status: {user.get('status', 'Unknown')}
Roles: {', '.join(roles)}
Location: {user.get('location', 'Not specified')}
Website: {user.get('website', 'None')}
Bio: {user.get('bio', 'No bio')}
Profile Image: {user.get('profile_image', 'None')}
Cover Image: {user.get('cover_image', 'None')}
Created: {user.get('created_at', 'Unknown')}
Last Seen: {user.get('last_seen', 'Never')}
"""
    except GhostError as e:
        return str(e)
