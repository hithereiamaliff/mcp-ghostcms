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

async def create_newsletter(
    name: str,
    description: str = None,
    status: str = "active",
    subscribe_on_signup: bool = True,
    opt_in_existing: bool = False,
    sender_reply_to: str = "newsletter",
    show_header_icon: bool = True,
    show_header_title: bool = True,
    show_header_name: bool = True,
    show_feature_image: bool = True,
    title_font_category: str = "sans_serif",
    title_alignment: str = "center",
    body_font_category: str = "sans_serif",
    show_badge: bool = True,
    ctx: Context = None
) -> str:
    """Create a new newsletter.
    
    Args:
        name: Name of the newsletter (required)
        description: Newsletter description
        status: Newsletter status ("active" or "archived")
        subscribe_on_signup: Whether to subscribe new members automatically
        opt_in_existing: Whether to subscribe existing members
        sender_reply_to: Reply-to setting ("newsletter" or "support")
        show_header_icon: Whether to show header icon
        show_header_title: Whether to show header title
        show_header_name: Whether to show header name
        show_feature_image: Whether to show feature image
        title_font_category: Font category for titles
        title_alignment: Title alignment
        body_font_category: Font category for body text
        show_badge: Whether to show badge
        ctx: Optional context for logging
    
    Returns:
        Formatted string containing the created newsletter details
    """
    if ctx:
        ctx.info(f"Creating new newsletter: {name}")
    
    try:
        if ctx:
            ctx.debug("Getting auth headers")
        headers = await get_auth_headers(STAFF_API_KEY)
        
        newsletter_data = {
            "newsletters": [{
                "name": name,
                "description": description,
                "status": status,
                "subscribe_on_signup": subscribe_on_signup,
                "sender_reply_to": sender_reply_to,
                "show_header_icon": show_header_icon,
                "show_header_title": show_header_title,
                "show_header_name": show_header_name,
                "show_feature_image": show_feature_image,
                "title_font_category": title_font_category,
                "title_alignment": title_alignment,
                "body_font_category": body_font_category,
                "show_badge": show_badge
            }]
        }

        if ctx:
            ctx.debug("Making API request to create newsletter")
        
        endpoint = f"newsletters/?opt_in_existing={'true' if opt_in_existing else 'false'}"
        data = await make_ghost_request(
            endpoint,
            headers,
            ctx,
            http_method="POST",
            json_data=newsletter_data
        )
        
        if ctx:
            ctx.debug("Processing create newsletter response")
        
        newsletter = data["newsletters"][0]
        return f"""
Newsletter created successfully!

Name: {newsletter.get('name')}
Description: {newsletter.get('description', 'No description')}
Status: {newsletter.get('status')}
ID: {newsletter.get('id')}
"""

    except GhostError as e:
        if ctx:
            ctx.error(f"Failed to create newsletter: {str(e)}")
        return str(e)
    
async def update_newsletter(
    newsletter_id: str,
    name: str = None,
    description: str = None,
    sender_name: str = None,
    sender_email: str = None,
    sender_reply_to: str = None,
    status: str = None,
    subscribe_on_signup: bool = None,
    sort_order: int = None,
    header_image: str = None,
    show_header_icon: bool = None,
    show_header_title: bool = None,
    show_header_name: bool = None,
    title_font_category: str = None,
    title_alignment: str = None,
    show_feature_image: bool = None,
    body_font_category: str = None,
    footer_content: str = None,
    show_badge: bool = None,
    ctx: Context = None
) -> str:
    """Update an existing newsletter.
    
    Args:
        newsletter_id: ID of the newsletter to update (required)
        name: New newsletter name
        description: New newsletter description
        sender_name: Name shown in email clients
        sender_email: Email address newsletters are sent from
        sender_reply_to: Reply-to setting ("newsletter" or "support")
        status: Newsletter status ("active" or "archived")
        subscribe_on_signup: Whether to subscribe new members automatically
        sort_order: Order in lists
        header_image: URL of header image
        show_header_icon: Whether to show header icon
        show_header_title: Whether to show header title
        show_header_name: Whether to show header name
        title_font_category: Font category for titles
        title_alignment: Title alignment
        show_feature_image: Whether to show feature image
        body_font_category: Font category for body text
        footer_content: Custom footer content
        show_badge: Whether to show badge
        ctx: Optional context for logging
    
    Returns:
        Formatted string containing the updated newsletter details
    """
    if ctx:
        ctx.info(f"Updating newsletter with ID: {newsletter_id}")
    
    try:
        if ctx:
            ctx.debug("Getting auth headers")
        headers = await get_auth_headers(STAFF_API_KEY)

        # Build update data with only provided fields
        update_data = {"newsletters": [{"id": newsletter_id}]}
        
        # Add non-None values to the update data
        fields = locals()
        for field in [
            "name", "description", "sender_name", "sender_email",
            "sender_reply_to", "status", "subscribe_on_signup",
            "sort_order", "header_image", "show_header_icon",
            "show_header_title", "show_header_name", "title_font_category",
            "title_alignment", "show_feature_image", "body_font_category",
            "footer_content", "show_badge"
        ]:
            if fields[field] is not None:
                update_data["newsletters"][0][field] = fields[field]

        if ctx:
            ctx.debug(f"Making API request to update newsletter {newsletter_id}")
        
        data = await make_ghost_request(
            f"newsletters/{newsletter_id}/",
            headers,
            ctx,
            http_method="PUT",
            json_data=update_data
        )
        
        if ctx:
            ctx.debug("Processing update newsletter response")
        
        newsletter = data["newsletters"][0]
        return f"""
Newsletter updated successfully!

Name: {newsletter.get('name')}
Description: {newsletter.get('description', 'No description')}
Status: {newsletter.get('status')}
Sender Name: {newsletter.get('sender_name', 'Not set')}
Sender Email: {newsletter.get('sender_email', 'Not set')}
Sort Order: {newsletter.get('sort_order', 0)}
ID: {newsletter.get('id')}
"""

    except GhostError as e:
        if ctx:
            ctx.error(f"Failed to update newsletter: {str(e)}")
        return str(e)