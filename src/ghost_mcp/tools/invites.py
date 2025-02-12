"""Invite-related MCP tools for Ghost API."""

import json
from mcp.server.fastmcp import Context

from ..api import make_ghost_request, get_auth_headers
from ..config import STAFF_API_KEY
from ..exceptions import GhostError

async def create_invite(
    role_id: str,
    email: str,
    ctx: Context = None
) -> str:
    """Create a staff user invite in Ghost.
    
    Args:
        role_id: ID of the role to assign to the invited user (required)
        email: Email address to send the invite to (required)
        ctx: Optional context for logging
    
    Returns:
        String representation of the created invite

    Raises:
        GhostError: If the Ghost API request fails
        ValueError: If required parameters are missing or invalid
    """
    if not all([role_id, email]):
        raise ValueError("Both role_id and email are required for creating an invite")

    if ctx:
        ctx.info(f"Creating invite for email: {email} with role: {role_id}")

    # Construct invite data
    invite_data = {
        "invites": [{
            "role_id": role_id,
            "email": email
        }]
    }

    try:
        if ctx:
            ctx.debug("Getting auth headers")
        headers = await get_auth_headers(STAFF_API_KEY)
        
        if ctx:
            ctx.debug("Making API request to create invite")
        response = await make_ghost_request(
            "invites/",
            headers,
            ctx,
            http_method="POST",
            json_data=invite_data
        )
        
        if ctx:
            ctx.debug("Processing created invite response")
        
        invite = response.get("invites", [{}])[0]
        
        return f"""
Invite created successfully:
Email: {invite.get('email')}
Role ID: {invite.get('role_id')}
Status: {invite.get('status', 'sent')}
Created: {invite.get('created_at', 'Unknown')}
Expires: {invite.get('expires', 'Unknown')}
ID: {invite.get('id')}
"""
    except Exception as e:
        if ctx:
            ctx.error(f"Failed to create invite: {str(e)}")
        raise
