"""Newsletter-related MCP tools for Ghost API."""

import json
from mcp.server.fastmcp import Context

from ..api import make_ghost_request, get_auth_headers
from ..config import STAFF_API_KEY
from ..exceptions import GhostError

async def list_newsletters(
    format: str = "text",
    page: int = 1,
    limit: int = 15,
    ctx: Context = None
) -> str:
    """Get the list of newsletters from your Ghost blog.
    
    Args:
        format: Output format - either "text" or "json" (default: "text")
        page: Page number for pagination (default: 1)
        limit: Number of newsletters per page (default: 15)
        ctx: Optional context for logging
    
    Returns:
        Formatted string containing newsletter information
    """
    if ctx:
        ctx.info(f"Listing newsletters (page {page}, limit {limit}, format {format})")
    
    try:
        if ctx:
            ctx.debug("Getting auth headers")
        headers = await get_auth_headers(STAFF_API_KEY)
        
        if ctx:
            ctx.debug("Making API request to /newsletters/ with pagination")
        data = await make_ghost_request(
            f"newsletters/?page={page}&limit={limit}",
            headers,
            ctx
        )
        
        if ctx:
            ctx.debug("Processing newsletters list response")
        
        newsletters = data.get("newsletters", [])
        if not newsletters:
            if ctx:
                ctx.info("No newsletters found in response")
            return "No newsletters found."

        if format.lower() == "json":
            if ctx:
                ctx.debug("Returning JSON format")
            return json.dumps(newsletters, indent=2)
        
        formatted_newsletters = []
        for newsletter in newsletters:
            formatted_newsletter = f"""
Name: {newsletter.get('name', 'Unknown')}
Description: {newsletter.get('description', 'No description')}
Status: {newsletter.get('status', 'Unknown')}
Visibility: {newsletter.get('visibility', 'Unknown')}
Subscribe on Signup: {newsletter.get('subscribe_on_signup', False)}
ID: {newsletter.get('id', 'Unknown')}
"""
            formatted_newsletters.append(formatted_newsletter)
        return "\n---\n".join(formatted_newsletters)
        
    except GhostError as e:
        if ctx:
            ctx.error(f"Failed to list newsletters: {str(e)}")
        return str(e)

async def read_newsletter(newsletter_id: str, ctx: Context = None) -> str:
    """Get the details of a specific newsletter.
  
    Args:
        newsletter_id: The ID of the newsletter to retrieve
        ctx: Optional context for logging
      
    Returns:
        Formatted string containing the newsletter details
    """
    if ctx:
        ctx.info(f"Reading newsletter details for ID: {newsletter_id}")
    
    try:
        if ctx:
            ctx.debug("Getting auth headers")
        headers = await get_auth_headers(STAFF_API_KEY)
        
        if ctx:
            ctx.debug(f"Making API request to /newsletters/{newsletter_id}/")
        data = await make_ghost_request(
            f"newsletters/{newsletter_id}/",
            headers,
            ctx
        )
        
        if ctx:
            ctx.debug("Processing newsletter response data")
      
        newsletter = data["newsletters"][0]
      
        return f"""
Name: {newsletter.get('name', 'Unknown')}
Description: {newsletter.get('description', 'No description')}
Status: {newsletter.get('status', 'Unknown')}
Visibility: {newsletter.get('visibility', 'Unknown')}
Subscribe on Signup: {newsletter.get('subscribe_on_signup', False)}
Sort Order: {newsletter.get('sort_order', 0)}
Sender Email: {newsletter.get('sender_email', 'Not set')}
Sender Reply To: {newsletter.get('sender_reply_to', 'Not set')}
Show Header Icon: {newsletter.get('show_header_icon', True)}
Show Header Title: {newsletter.get('show_header_title', True)}
Show Header Name: {newsletter.get('show_header_name', True)}
Show Feature Image: {newsletter.get('show_feature_image', True)}
Title Font Category: {newsletter.get('title_font_category', 'Unknown')}
Body Font Category: {newsletter.get('body_font_category', 'Unknown')}
Show Badge: {newsletter.get('show_badge', True)}
Created: {newsletter.get('created_at', 'Unknown')}
Updated: {newsletter.get('updated_at', 'Unknown')}
"""
    except GhostError as e:
        if ctx:
            ctx.error(f"Failed to read newsletter: {str(e)}")
        return str(e)
