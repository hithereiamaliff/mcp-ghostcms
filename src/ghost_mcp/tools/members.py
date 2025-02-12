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

async def update_member(
    member_id: str,
    email: str = None,
    name: str = None,
    note: str = None,
    labels: list = None,
    newsletter_ids: list = None,
    ctx: Context = None
) -> str:
    """Update an existing member in Ghost.
    
    Args:
        member_id: ID of the member to update (required)
        email: New email address for the member (optional)
        name: New name for the member (optional)
        note: New notes about the member (optional)
        labels: New list of labels. Each label should be a dict with 'name' and 'slug' (optional)
        newsletter_ids: New list of newsletter IDs to subscribe the member to (optional)
        ctx: Optional context for logging
    
    Returns:
        String representation of the updated member

    Raises:
        GhostError: If the Ghost API request fails
        ValueError: If no fields to update are provided
    """
    # Check if at least one field to update is provided
    if not any([email, name, note, labels, newsletter_ids]):
        raise ValueError("At least one field must be provided to update")

    if ctx:
        ctx.info(f"Updating member with ID: {member_id}")

    # Construct update data with only provided fields
    update_data = {"members": [{}]}
    member_updates = update_data["members"][0]

    if email is not None:
        member_updates["email"] = email
    if name is not None:
        member_updates["name"] = name
    if note is not None:
        member_updates["note"] = note
    if labels is not None:
        member_updates["labels"] = labels
    if newsletter_ids is not None:
        member_updates["newsletters"] = [
            {"id": newsletter_id} for newsletter_id in newsletter_ids
        ]

    try:
        if ctx:
            ctx.debug("Getting auth headers")
        headers = await get_auth_headers(STAFF_API_KEY)
        
        if ctx:
            ctx.debug(f"Making API request to update member {member_id}")
        response = await make_ghost_request(
            f"members/{member_id}/",
            headers,
            ctx,
            http_method="PUT",
            json_data=update_data
        )
        
        if ctx:
            ctx.debug("Processing updated member response")
        
        member = response.get("members", [{}])[0]
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
Member updated successfully:
Name: {member.get('name', 'Unknown')}
Email: {member.get('email')}
Status: {member.get('status', 'free')}
Newsletters: {', '.join(newsletters) if newsletters else 'None'}
Created: {member.get('created_at', 'Unknown')}
Updated: {member.get('updated_at', 'Unknown')}
Note: {member.get('note', 'No notes')}
Labels: {', '.join(label.get('name', '') for label in member.get('labels', []))}
Email Count: {member.get('email_count', 0)}
Email Open Rate: {member.get('email_open_rate', 0)}%
Last Seen At: {member.get('last_seen_at', 'Never')}{subscription_info}
ID: {member.get('id')}
"""
    except Exception as e:
        if ctx:
            ctx.error(f"Failed to update member: {str(e)}")
        raise

async def create_member(
    email: str,
    name: str = None,
    note: str = None,
    labels: list = None,
    newsletter_ids: list = None,
    ctx: Context = None
) -> str:
    """Create a new member in Ghost.
    
    Args:
        email: Member's email address (required)
        name: Member's name (optional)
        note: Notes about the member (optional)
        labels: List of labels to apply to the member. Each label should be a dict with 'name' and 'slug' (optional)
        newsletter_ids: List of newsletter IDs to subscribe the member to (optional)
        ctx: Optional context for logging
    
    Returns:
        String representation of the created member

    Raises:
        GhostError: If the Ghost API request fails
        ValueError: If required parameters are missing or invalid
    """
    if not email:
        raise ValueError("Email is required for creating a member")

    if ctx:
        ctx.info(f"Creating new member with email: {email}")

    # Construct member data
    member_data = {
        "members": [{
            "email": email
        }]
    }

    # Add optional fields if provided
    if name:
        member_data["members"][0]["name"] = name
    if note:
        member_data["members"][0]["note"] = note
    if labels:
        member_data["members"][0]["labels"] = labels
    if newsletter_ids:
        member_data["members"][0]["newsletters"] = [
            {"id": newsletter_id} for newsletter_id in newsletter_ids
        ]

    try:
        if ctx:
            ctx.debug("Getting auth headers")
        headers = await get_auth_headers(STAFF_API_KEY)
        
        if ctx:
            ctx.debug("Making API request to create member")
        response = await make_ghost_request(
            "members/",
            headers,
            ctx,
            http_method="POST",
            json_data=member_data
        )
        
        if ctx:
            ctx.debug("Processing created member response")
        
        member = response.get("members", [{}])[0]
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
Member created successfully:
Name: {member.get('name', 'Unknown')}
Email: {member.get('email')}
Status: {member.get('status', 'free')}
Newsletters: {', '.join(newsletters) if newsletters else 'None'}
Created: {member.get('created_at', 'Unknown')}
Note: {member.get('note', 'No notes')}
Labels: {', '.join(label.get('name', '') for label in member.get('labels', []))}
Email Count: {member.get('email_count', 0)}
Email Open Rate: {member.get('email_open_rate', 0)}%
Last Seen At: {member.get('last_seen_at', 'Never')}{subscription_info}
ID: {member.get('id')}
"""
    except Exception as e:
        if ctx:
            ctx.error(f"Failed to create member: {str(e)}")
        raise

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
