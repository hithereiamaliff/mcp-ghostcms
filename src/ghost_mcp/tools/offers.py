"""Offer-related MCP tools for Ghost API."""

import json
from mcp.server.fastmcp import Context

from ..api import make_ghost_request, get_auth_headers
from ..config import STAFF_API_KEY
from ..exceptions import GhostError

async def list_offers(
    format: str = "text",
    page: int = 1,
    limit: int = 15,
    ctx: Context = None
) -> str:
    """Get the list of offers from your Ghost blog.
    
    Args:
        format: Output format - either "text" or "json" (default: "text")
        page: Page number for pagination (default: 1)
        limit: Number of offers per page (default: 15)
        ctx: Optional context for logging
    
    Returns:
        Formatted string containing offer information
    """
    if ctx:
        ctx.info(f"Listing offers (page {page}, limit {limit}, format {format})")
    
    try:
        if ctx:
            ctx.debug("Getting auth headers")
        headers = await get_auth_headers(STAFF_API_KEY)
        
        if ctx:
            ctx.debug("Making API request to /offers/ with pagination")
        data = await make_ghost_request(
            f"offers/?page={page}&limit={limit}",
            headers,
            ctx
        )
        
        if ctx:
            ctx.debug("Processing offers list response")
        
        offers = data.get("offers", [])
        if not offers:
            if ctx:
                ctx.info("No offers found in response")
            return "No offers found."

        if format.lower() == "json":
            if ctx:
                ctx.debug("Returning JSON format")
            return json.dumps(offers, indent=2)
        
        formatted_offers = []
        for offer in offers:
            formatted_offer = f"""
Name: {offer.get('name', 'Unknown')}
Code: {offer.get('code', 'Unknown')}
Display Title: {offer.get('display_title', 'No display title')}
Type: {offer.get('type', 'Unknown')}
Amount: {offer.get('amount', 'Unknown')}
Duration: {offer.get('duration', 'Unknown')}
Status: {offer.get('status', 'Unknown')}
Tier: {offer.get('tier', {}).get('name', 'Unknown')}
ID: {offer.get('id', 'Unknown')}
"""
            formatted_offers.append(formatted_offer)
        return "\n---\n".join(formatted_offers)
        
    except GhostError as e:
        if ctx:
            ctx.error(f"Failed to list offers: {str(e)}")
        return str(e)

async def read_offer(offer_id: str, ctx: Context = None) -> str:
    """Get the details of a specific offer.
  
    Args:
        offer_id: The ID of the offer to retrieve
        ctx: Optional context for logging
      
    Returns:
        Formatted string containing the offer details
    """
    if ctx:
        ctx.info(f"Reading offer details for ID: {offer_id}")
    
    try:
        if ctx:
            ctx.debug("Getting auth headers")
        headers = await get_auth_headers(STAFF_API_KEY)
        
        if ctx:
            ctx.debug(f"Making API request to /offers/{offer_id}/")
        data = await make_ghost_request(
            f"offers/{offer_id}/",
            headers,
            ctx
        )
        
        if ctx:
            ctx.debug("Processing offer response data")
      
        offer = data["offers"][0]
      
        return f"""
Name: {offer.get('name', 'Unknown')}
Code: {offer.get('code', 'Unknown')}
Display Title: {offer.get('display_title', 'No display title')}
Display Description: {offer.get('display_description', 'No description')}
Type: {offer.get('type', 'Unknown')}
Status: {offer.get('status', 'Unknown')}
Cadence: {offer.get('cadence', 'Unknown')}
Amount: {offer.get('amount', 'Unknown')}
Duration: {offer.get('duration', 'Unknown')}
Currency: {offer.get('currency', 'N/A')}
Tier: {offer.get('tier', {}).get('name', 'Unknown')}
Redemption Count: {offer.get('redemption_count', 0)}
Created: {offer.get('created_at', 'Unknown')}
"""
    except GhostError as e:
        if ctx:
            ctx.error(f"Failed to read offer: {str(e)}")
        return str(e)
