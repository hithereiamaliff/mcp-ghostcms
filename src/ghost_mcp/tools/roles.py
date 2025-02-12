"""Role-related MCP tools for Ghost API."""

import json
from mcp.server.fastmcp import Context

from ..api import make_ghost_request, get_auth_headers
from ..config import STAFF_API_KEY
from ..exceptions import GhostError

async def list_roles(
    format: str = "text",
    page: int = 1,
    limit: int = 15,
    ctx: Context = None
) -> str:
    """Get the list of roles from your Ghost blog.
    
    Args:
        format: Output format - either "text" or "json" (default: "text")
        page: Page number for pagination (default: 1)
        limit: Number of roles per page (default: 15)
        ctx: Optional context for logging
    
    Returns:
        Formatted string containing role information
    """
    if ctx:
        ctx.info(f"Listing roles (page {page}, limit {limit}, format {format})")
    
    try:
        if ctx:
            ctx.debug("Getting auth headers")
        headers = await get_auth_headers(STAFF_API_KEY)
        
        if ctx:
            ctx.debug("Making API request to /roles/ with pagination")
        data = await make_ghost_request(
            f"roles/?page={page}&limit={limit}",
            headers,
            ctx
        )
        
        if ctx:
            ctx.debug("Processing roles list response")
        
        roles = data.get("roles", [])
        if not roles:
            if ctx:
                ctx.info("No roles found in response")
            return "No roles found."

        if format.lower() == "json":
            if ctx:
                ctx.debug("Returning JSON format")
            return json.dumps(roles, indent=2)
        
        formatted_roles = []
        for role in roles:
            formatted_role = f"""
Name: {role.get('name', 'Unknown')}
Description: {role.get('description', 'No description')}
Created: {role.get('created_at', 'Unknown')}
Updated: {role.get('updated_at', 'Unknown')}
ID: {role.get('id', 'Unknown')}
"""
            formatted_roles.append(formatted_role)
        return "\n---\n".join(formatted_roles)
        
    except GhostError as e:
        if ctx:
            ctx.error(f"Failed to list roles: {str(e)}")
        return str(e)
