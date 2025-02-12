"""Tier-related MCP tools for Ghost API."""

import json
from typing import Optional, List
from mcp.server.fastmcp import Context

from ..api import make_ghost_request, get_auth_headers
from ..config import STAFF_API_KEY
from mcp.server.fastmcp import Context

from ..api import make_ghost_request, get_auth_headers
from ..config import STAFF_API_KEY
from ..exceptions import GhostError

async def list_tiers(
    format: str = "text",
    page: int = 1,
    limit: int = 15,
    ctx: Context = None
) -> str:
    """Get the list of tiers from your Ghost blog.
    
    Args:
        format: Output format - either "text" or "json" (default: "text")
        page: Page number for pagination (default: 1)
        limit: Number of tiers per page (default: 15)
        ctx: Optional context for logging
    
    Returns:
        Formatted string containing tier information
    """
    if ctx:
        ctx.info(f"Listing tiers (page {page}, limit {limit}, format {format})")
    
    try:
        if ctx:
            ctx.debug("Getting auth headers")
        headers = await get_auth_headers(STAFF_API_KEY)
        
        if ctx:
            ctx.debug("Making API request to /tiers/ with pagination")
        data = await make_ghost_request(
            f"tiers/?page={page}&limit={limit}&include=monthly_price,yearly_price,benefits",
            headers,
            ctx
        )
        
        if ctx:
            ctx.debug("Processing tiers list response")
        
        tiers = data.get("tiers", [])
        if not tiers:
            if ctx:
                ctx.info("No tiers found in response")
            return "No tiers found."

        if format.lower() == "json":
            if ctx:
                ctx.debug("Returning JSON format")
            return json.dumps(tiers, indent=2)
        
        formatted_tiers = []
        for tier in tiers:
            benefits = tier.get('benefits', [])
            formatted_tier = f"""
Name: {tier.get('name', 'Unknown')}
Description: {tier.get('description', 'No description')}
Type: {tier.get('type', 'Unknown')}
Active: {tier.get('active', False)}
Monthly Price: {tier.get('monthly_price', 'N/A')}
Yearly Price: {tier.get('yearly_price', 'N/A')}
Benefits: {', '.join(benefits) if benefits else 'None'}
ID: {tier.get('id', 'Unknown')}
"""
            formatted_tiers.append(formatted_tier)
        return "\n---\n".join(formatted_tiers)
        
    except GhostError as e:
        if ctx:
            ctx.error(f"Failed to list tiers: {str(e)}")
        return str(e)

async def read_tier(tier_id: str, ctx: Context = None) -> str:
    """Get the details of a specific tier.
  
    Args:
        tier_id: The ID of the tier to retrieve
        ctx: Optional context for logging
      
    Returns:
        Formatted string containing the tier details
    """
    if ctx:
        ctx.info(f"Reading tier details for ID: {tier_id}")
    
    try:
        if ctx:
            ctx.debug("Getting auth headers")
        headers = await get_auth_headers(STAFF_API_KEY)
        
        if ctx:
            ctx.debug(f"Making API request to /tiers/{tier_id}/")
        data = await make_ghost_request(
            f"tiers/{tier_id}/?include=monthly_price,yearly_price,benefits",
            headers,
            ctx
        )
        
        if ctx:
            ctx.debug("Processing tier response data")
      
        tier = data["tiers"][0]
        benefits = tier.get('benefits', [])
      
        return f"""
Name: {tier.get('name', 'Unknown')}
Description: {tier.get('description', 'No description')}
Type: {tier.get('type', 'Unknown')}
Active: {tier.get('active', False)}
Welcome Page URL: {tier.get('welcome_page_url', 'None')}
Created: {tier.get('created_at', 'Unknown')}
Updated: {tier.get('updated_at', 'Unknown')}
Monthly Price: {tier.get('monthly_price', 'N/A')}
Yearly Price: {tier.get('yearly_price', 'N/A')}
Currency: {tier.get('currency', 'Unknown')}
Benefits:
{chr(10).join(f'- {benefit}' for benefit in benefits) if benefits else 'No benefits listed'}
"""
    except GhostError as e:
        if ctx:
            ctx.error(f"Failed to read tier: {str(e)}")
        return str(e)

async def create_tier(
    name: str,
    monthly_price: Optional[int] = None,
    yearly_price: Optional[int] = None,
    description: Optional[str] = None,
    benefits: Optional[List[str]] = None,
    welcome_page_url: Optional[str] = None,
    visibility: str = "public",
    currency: str = "usd",
    ctx: Context = None
) -> str:
    """Create a new tier in Ghost.
    
    Args:
        name: Name of the tier (required)
        monthly_price: Optional monthly price in cents (e.g. 500 for $5.00)
        yearly_price: Optional yearly price in cents (e.g. 5000 for $50.00)
        description: Optional description of the tier
        benefits: Optional list of benefits for the tier
        welcome_page_url: Optional URL for the welcome page
        visibility: Visibility of tier, either "public" or "none" (default: "public")
        currency: Currency for prices (default: "usd")
        ctx: Optional context for logging
    
    Returns:
        String representation of the created tier

    Raises:
        GhostError: If the Ghost API request fails
    """
    if not name:
        raise ValueError("Name is required for creating a tier")

    if ctx:
        ctx.info(f"Creating new tier: {name}")

    # Construct tier data
    tier_data = {
        "tiers": [{
            "name": name,
            "description": description,
            "type": "paid" if (monthly_price or yearly_price) else "free",
            "active": True,
            "visibility": visibility,
            "welcome_page_url": welcome_page_url,
            "benefits": benefits or [],
            "currency": currency
        }]
    }

    # Add pricing if provided
    if monthly_price is not None:
        tier_data["tiers"][0]["monthly_price"] = monthly_price
    if yearly_price is not None:
        tier_data["tiers"][0]["yearly_price"] = yearly_price

    try:
        if ctx:
            ctx.debug("Getting auth headers")
        headers = await get_auth_headers(STAFF_API_KEY)
        
        if ctx:
            ctx.debug("Making API request to create tier")
        response = await make_ghost_request(
            "tiers/",
            headers,
            ctx,
            http_method="POST",
            json_data=tier_data
        )
        
        if ctx:
            ctx.debug("Processing created tier response")
        
        tier = response.get("tiers", [{}])[0]
        
        # Format response
        benefits_text = "\n- ".join(tier.get('benefits', [])) if tier.get('benefits') else "None"
        return f"""
Tier created successfully:
Name: {tier.get('name')}
Type: {tier.get('type')}
Description: {tier.get('description', 'No description')}
Active: {tier.get('active', False)}
Visibility: {tier.get('visibility', 'public')}
Monthly Price: {tier.get('monthly_price', 'N/A')} {tier.get('currency', 'usd').upper()}
Yearly Price: {tier.get('yearly_price', 'N/A')} {tier.get('currency', 'usd').upper()}
Currency: {tier.get('currency', 'usd').upper()}
Benefits:
- {benefits_text}
ID: {tier.get('id', 'Unknown')}
"""
    except Exception as e:
        if ctx:
            ctx.error(f"Failed to create tier: {str(e)}")
        raise

async def update_tier(
    tier_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    monthly_price: Optional[int] = None,
    yearly_price: Optional[int] = None,
    benefits: Optional[List[str]] = None,
    welcome_page_url: Optional[str] = None,
    visibility: Optional[str] = None,
    currency: Optional[str] = None,
    active: Optional[bool] = None,
    ctx: Context = None
) -> str:
    """Update an existing tier in Ghost.
    
    Args:
        tier_id: ID of the tier to update (required)
        name: New name for the tier
        description: New description for the tier
        monthly_price: New monthly price in cents (e.g. 500 for $5.00)
        yearly_price: New yearly price in cents (e.g. 5000 for $50.00)
        benefits: New list of benefits for the tier
        welcome_page_url: New URL for the welcome page
        visibility: New visibility setting ("public" or "none")
        currency: New currency for prices
        active: New active status
        ctx: Optional context for logging
    
    Returns:
        String representation of the updated tier

    Raises:
        GhostError: If the Ghost API request fails
    """
    if ctx:
        ctx.info(f"Updating tier with ID: {tier_id}")

    # Construct update data with only provided fields
    update_data = {"tiers": [{}]}
    tier_updates = update_data["tiers"][0]

    if name is not None:
        tier_updates["name"] = name
    if description is not None:
        tier_updates["description"] = description
    if monthly_price is not None:
        tier_updates["monthly_price"] = monthly_price
    if yearly_price is not None:
        tier_updates["yearly_price"] = yearly_price
    if benefits is not None:
        tier_updates["benefits"] = benefits
    if welcome_page_url is not None:
        tier_updates["welcome_page_url"] = welcome_page_url
    if visibility is not None:
        tier_updates["visibility"] = visibility
    if currency is not None:
        tier_updates["currency"] = currency
    if active is not None:
        tier_updates["active"] = active

    try:
        if ctx:
            ctx.debug("Getting auth headers")
        headers = await get_auth_headers(STAFF_API_KEY)
        
        if ctx:
            ctx.debug(f"Making API request to update tier {tier_id}")
        response = await make_ghost_request(
            f"tiers/{tier_id}/",
            headers,
            ctx,
            http_method="PUT",
            json_data=update_data
        )
        
        if ctx:
            ctx.debug("Processing updated tier response")
        
        tier = response.get("tiers", [{}])[0]
        
        # Format response
        benefits_text = "\n- ".join(tier.get('benefits', [])) if tier.get('benefits') else "None"
        return f"""
Tier updated successfully:
Name: {tier.get('name')}
Type: {tier.get('type')}
Description: {tier.get('description', 'No description')}
Active: {tier.get('active', False)}
Visibility: {tier.get('visibility', 'public')}
Monthly Price: {tier.get('monthly_price', 'N/A')} {tier.get('currency', 'usd').upper()}
Yearly Price: {tier.get('yearly_price', 'N/A')} {tier.get('currency', 'usd').upper()}
Currency: {tier.get('currency', 'usd').upper()}
Benefits:
- {benefits_text}
ID: {tier.get('id')}
"""
    except Exception as e:
        if ctx:
            ctx.error(f"Failed to update tier: {str(e)}")
        raise