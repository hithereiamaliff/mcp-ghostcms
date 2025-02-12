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

async def update_user(
    user_id: str,
    name: str = None,
    slug: str = None,
    email: str = None,
    profile_image: str = None,
    cover_image: str = None,
    bio: str = None,
    website: str = None,
    location: str = None,
    facebook: str = None,
    twitter: str = None,
    meta_title: str = None,
    meta_description: str = None,
    accessibility: str = None,
    comment_notifications: bool = None,
    free_member_signup_notification: bool = None,
    paid_subscription_started_notification: bool = None,
    paid_subscription_canceled_notification: bool = None,
    mention_notifications: bool = None,
    milestone_notifications: bool = None,
    ctx: Context = None
) -> str:
    """Update an existing user in Ghost.
    
    Args:
        user_id: ID of the user to update (required)
        name: User's full name (optional)
        slug: User's slug (optional)
        email: User's email address (optional)
        profile_image: URL for profile image (optional)
        cover_image: URL for cover image (optional)
        bio: User's bio (optional)
        website: User's website URL (optional)
        location: User's location (optional)
        facebook: Facebook username (optional)
        twitter: Twitter username (optional)
        meta_title: Meta title for SEO (optional)
        meta_description: Meta description for SEO (optional)
        accessibility: Accessibility settings (optional)
        comment_notifications: Enable comment notifications (optional)
        free_member_signup_notification: Enable free member signup notifications (optional)
        paid_subscription_started_notification: Enable paid subscription started notifications (optional)
        paid_subscription_canceled_notification: Enable paid subscription canceled notifications (optional)
        mention_notifications: Enable mention notifications (optional)
        milestone_notifications: Enable milestone notifications (optional)
        ctx: Optional context for logging
    
    Returns:
        String representation of the updated user

    Raises:
        GhostError: If the Ghost API request fails
        ValueError: If no fields to update are provided
    """
    # Check if at least one field to update is provided
    update_fields = {
        'name': name,
        'slug': slug,
        'email': email,
        'profile_image': profile_image,
        'cover_image': cover_image,
        'bio': bio,
        'website': website,
        'location': location,
        'facebook': facebook,
        'twitter': twitter,
        'meta_title': meta_title,
        'meta_description': meta_description,
        'accessibility': accessibility,
        'comment_notifications': comment_notifications,
        'free_member_signup_notification': free_member_signup_notification,
        'paid_subscription_started_notification': paid_subscription_started_notification,
        'paid_subscription_canceled_notification': paid_subscription_canceled_notification,
        'mention_notifications': mention_notifications,
        'milestone_notifications': milestone_notifications
    }

    if not any(v is not None for v in update_fields.values()):
        raise ValueError("At least one field must be provided to update")

    if ctx:
        ctx.info(f"Updating user with ID: {user_id}")

    # Construct update data with only provided fields
    update_data = {"users": [{}]}
    user_updates = update_data["users"][0]

    for field, value in update_fields.items():
        if value is not None:
            user_updates[field] = value

    try:
        if ctx:
            ctx.debug("Getting auth headers")
        headers = await get_auth_headers(STAFF_API_KEY)
        
        if ctx:
            ctx.debug(f"Making API request to update user {user_id}")
        response = await make_ghost_request(
            f"users/{user_id}/",
            headers,
            ctx,
            http_method="PUT",
            json_data=update_data
        )
        
        if ctx:
            ctx.debug("Processing updated user response")
        
        user = response.get("users", [{}])[0]
        roles = [role.get('name') for role in user.get('roles', [])]
        
        return f"""
User updated successfully:
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
Facebook: {user.get('facebook', 'None')}
Twitter: {user.get('twitter', 'None')}
Created: {user.get('created_at', 'Unknown')}
Updated: {user.get('updated_at', 'Unknown')}
Last Seen: {user.get('last_seen', 'Never')}
Notifications:
- Comments: {user.get('comment_notifications', False)}
- Free Member Signup: {user.get('free_member_signup_notification', False)}
- Paid Subscription Started: {user.get('paid_subscription_started_notification', False)}
- Paid Subscription Canceled: {user.get('paid_subscription_canceled_notification', False)}
- Mentions: {user.get('mention_notifications', False)}
- Milestones: {user.get('milestone_notifications', False)}
"""
    except Exception as e:
        if ctx:
            ctx.error(f"Failed to update user: {str(e)}")
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
