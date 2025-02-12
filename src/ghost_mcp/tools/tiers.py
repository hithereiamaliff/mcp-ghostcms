"""Tier-related MCP tools for Ghost API."""

import json
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
