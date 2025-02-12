"""Member-related MCP tools for Ghost API."""

import json
from mcp.server.fastmcp import Context

from ..api import make_ghost_request, get_auth_headers
from ..config import STAFF_API_KEY
from ..exceptions import GhostError

async def list_members(
    format: str = "text",
    page: int = 1,
    limit: int = 15,
    ctx: Context = None
) -> str:
    """Get the list of members from your Ghost blog.
    
    Args:
        format: Output format - either "text" or "json" (default: "text")
        page: Page number for pagination (default: 1)
        limit: Number of members per page (default: 15)
        ctx: Optional context for logging
    
    Returns:
        Formatted string containing member information
    """
    if ctx:
        ctx.info(f"Listing members (page {page}, limit {limit}, format {format})")
    
    try:
        if ctx:
            ctx.debug("Getting auth headers")
        headers = await get_auth_headers(STAFF_API_KEY)
        
        if ctx:
            ctx.debug("Making API request to /members/ with pagination")
        data = await make_ghost_request(
            f"members/?page={page}&limit={limit}&include=newsletters,subscriptions",
            headers,
            ctx
        )
        
        if ctx:
            ctx.debug("Processing members list response")
        
        members = data.get("members", [])
        if not members:
            if ctx:
                ctx.info("No members found in response")
            return "No members found."

        if format.lower() == "json":
            if ctx:
                ctx.debug("Returning JSON format")
            return json.dumps(members, indent=2)
        
        formatted_members = []
        for member in members:
            newsletters = [nl.get('name') for nl in member.get('newsletters', [])]
            formatted_member = f"""
Name: {member.get('name', 'Unknown')}
Email: {member.get('email', 'Unknown')}
Status: {member.get('status', 'Unknown')}
Newsletters: {', '.join(newsletters) if newsletters else 'None'}
Created: {member.get('created_at', 'Unknown')}
ID: {member.get('id', 'Unknown')}
"""
            formatted_members.append(formatted_member)
        return "\n---\n".join(formatted_members)
        
    except GhostError as e:
        if ctx:
            ctx.error(f"Failed to list members: {str(e)}")
        return str(e)

async def read_member(member_id: str, ctx: Context = None) -> str:
    """Get the details of a specific member.
  
    Args:
        member_id: The ID of the member to retrieve
        ctx: Optional context for logging
      
    Returns:
        Formatted string containing the member details
    """
    if ctx:
        ctx.info(f"Reading member details for ID: {member_id}")
    
    try:
        if ctx:
            ctx.debug("Getting auth headers")
        headers = await get_auth_headers(STAFF_API_KEY)
        
        if ctx:
            ctx.debug(f"Making API request to /members/{member_id}/")
        data = await make_ghost_request(
            f"members/{member_id}/?include=newsletters,subscriptions",
            headers,
            ctx
        )
        
        if ctx:
            ctx.debug("Processing member response data")
      
        member = data["members"][0]
        newsletters = [nl.get('name') for nl in member.get('newsletters', [])]
        subscriptions = member.get('subscriptions', [])
      
        subscription_info = ""
        if subscriptions:
            for sub in subscriptions:
                subscription_info += f"""
                    Subscription Details:
                    Status: {sub.get('status', 'Unknown')}
                    Start Date: {sub.get('start_date', 'Unknown')}
                    Current Period Ends: {sub.get('current_period_end', 'Unknown')}
                    Price: {sub.get('price', {}).get('nickname', 'Unknown')} ({sub.get('price', {}).get('amount', 0)} {sub.get('price', {}).get('currency', 'USD')})
                    """
      
        return f"""
Name: {member.get('name', 'Unknown')}
Email: {member.get('email', 'Unknown')}
Status: {member.get('status', 'Unknown')}
Newsletters: {', '.join(newsletters) if newsletters else 'None'}
Created: {member.get('created_at', 'Unknown')}
Note: {member.get('note', 'No notes')}
Labels: {', '.join(label.get('name', '') for label in member.get('labels', []))}
Email Count: {member.get('email_count', 0)}
Email Opened Count: {member.get('email_opened_count', 0)}
Email Open Rate: {member.get('email_open_rate', 0)}%
Last Seen At: {member.get('last_seen_at', 'Never')}{subscription_info}
"""
    except GhostError as e:
        if ctx:
            ctx.error(f"Failed to read member: {str(e)}")
        return str(e)
