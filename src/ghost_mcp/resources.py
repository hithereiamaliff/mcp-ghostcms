"""MCP resource handlers for Ghost API."""

import json
import datetime
from typing import Any

from .api import make_ghost_request, get_auth_headers
from .config import API_URL, STAFF_API_KEY
from .exceptions import GhostError

async def handle_user_resource(user_id: str) -> str:
    """Get a user as a resource.
    
    Args:
        user_id: The ID of the user to retrieve
        
    Returns:
        JSON string containing user data
    """
    try:
        headers = await get_auth_headers(STAFF_API_KEY)
        data = await make_ghost_request(
            f"users/{user_id}/?include=roles",
            headers,
            is_resource=True
        )
        user = data["users"][0]
        return json.dumps(user, indent=2)
    except GhostError as e:
        return json.dumps({"error": str(e)}, indent=2)

async def handle_member_resource(member_id: str) -> str:
    """Get a member as a resource.
    
    Args:
        member_id: The ID of the member to retrieve
        
    Returns:
        JSON string containing member data
    """
    try:
        headers = await get_auth_headers(STAFF_API_KEY)
        data = await make_ghost_request(
            f"members/{member_id}/?include=newsletters,subscriptions",
            headers,
            is_resource=True
        )
        member = data["members"][0]
        return json.dumps(member, indent=2)
    except GhostError as e:
        return json.dumps({"error": str(e)}, indent=2)

async def handle_tier_resource(tier_id: str) -> str:
    """Get a tier as a resource.
    
    Args:
        tier_id: The ID of the tier to retrieve
        
    Returns:
        JSON string containing tier data
    """
    try:
        headers = await get_auth_headers(STAFF_API_KEY)
        data = await make_ghost_request(
            f"tiers/{tier_id}/?include=monthly_price,yearly_price,benefits",
            headers,
            is_resource=True
        )
        tier = data["tiers"][0]
        return json.dumps(tier, indent=2)
    except GhostError as e:
        return json.dumps({"error": str(e)}, indent=2)

async def handle_offer_resource(offer_id: str) -> str:
    """Get an offer as a resource.
    
    Args:
        offer_id: The ID of the offer to retrieve
        
    Returns:
        JSON string containing offer data
    """
    try:
        headers = await get_auth_headers(STAFF_API_KEY)
        data = await make_ghost_request(
            f"offers/{offer_id}/",
            headers,
            is_resource=True
        )
        offer = data["offers"][0]
        return json.dumps(offer, indent=2)
    except GhostError as e:
        return json.dumps({"error": str(e)}, indent=2)

async def handle_newsletter_resource(newsletter_id: str) -> str:
    """Get a newsletter as a resource.
    
    Args:
        newsletter_id: The ID of the newsletter to retrieve
        
    Returns:
        JSON string containing newsletter data
    """
    try:
        headers = await get_auth_headers(STAFF_API_KEY)
        data = await make_ghost_request(
            f"newsletters/{newsletter_id}/",
            headers,
            is_resource=True
        )
        newsletter = data["newsletters"][0]
        return json.dumps(newsletter, indent=2)
    except GhostError as e:
        return json.dumps({"error": str(e)}, indent=2)

async def handle_post_resource(post_id: str) -> str:
    """Get a blog post as a resource.
    
    Args:
        post_id: The ID of the post to retrieve
        
    Returns:
        JSON string containing post data
    """
    try:
        headers = await get_auth_headers(STAFF_API_KEY)
        data = await make_ghost_request(
            f"posts/{post_id}/?formats=html",
            headers,
            is_resource=True
        )
        post = data["posts"][0]
        
        return json.dumps({
            "title": post.get('title'),
            "html": post.get('html'),
            "excerpt": post.get('excerpt'),
            "url": post.get('url'),
            "created_at": post.get('created_at')
        }, indent=2)
    except GhostError as e:
        return json.dumps({"error": str(e)}, indent=2)

async def handle_blog_info() -> str:
    """Get general blog information as a resource.
    
    Returns:
        JSON string containing blog information
    """
    try:
        headers = await get_auth_headers(STAFF_API_KEY)
        data = await make_ghost_request("site", headers, is_resource=True)
        site = data["site"]
        
        return json.dumps({
            "title": site.get('title'),
            "description": site.get('description'),
            "url": API_URL,
            "last_updated": datetime.datetime.now(datetime.UTC).isoformat()
        }, indent=2)
    except GhostError as e:
        return json.dumps({"error": str(e)}, indent=2)
