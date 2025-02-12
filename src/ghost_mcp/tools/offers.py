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
Status: {offer.get('status', 'Unknown')} d
Redemption Count: {offer.get('redemption_count', 0)}
Tier: {offer.get('tier', {}).get('name', 'Unknown')}
ID: {offer.get('id', 'Unknown')}
"""
            formatted_offers.append(formatted_offer)
        return "\n---\n".join(formatted_offers)
        
    except GhostError as e:
        if ctx:
            ctx.error(f"Failed to list offers: {str(e)}")
        return str(e)

async def update_offer(
    offer_id: str,
    name: str = None,
    code: str = None,
    display_title: str = None,
    display_description: str = None,
    ctx: Context = None
) -> str:
    """Update an existing offer in Ghost.
    
    Args:
        offer_id: ID of the offer to update (required)
        name: New internal name for the offer (optional)
        code: New shortcode for the offer (optional)
        display_title: New name displayed in the offer window (optional)
        display_description: New text displayed in the offer window (optional)
        ctx: Optional context for logging
    
    Returns:
        String representation of the updated offer

    Raises:
        GhostError: If the Ghost API request fails
        ValueError: If no fields to update are provided
    """
    # Check if at least one editable field is provided
    if not any([name, code, display_title, display_description]):
        raise ValueError("At least one of name, code, display_title, or display_description must be provided")

    if ctx:
        ctx.info(f"Updating offer with ID: {offer_id}")

    # Construct update data with only provided fields
    update_data = {"offers": [{}]}
    offer_updates = update_data["offers"][0]

    if name is not None:
        offer_updates["name"] = name
    if code is not None:
        offer_updates["code"] = code
    if display_title is not None:
        offer_updates["display_title"] = display_title
    if display_description is not None:
        offer_updates["display_description"] = display_description

    try:
        if ctx:
            ctx.debug("Getting auth headers")
        headers = await get_auth_headers(STAFF_API_KEY)
        
        if ctx:
            ctx.debug(f"Making API request to update offer {offer_id}")
        response = await make_ghost_request(
            f"offers/{offer_id}/",
            headers,
            ctx,
            http_method="PUT",
            json_data=update_data
        )
        
        if ctx:
            ctx.debug("Processing updated offer response")
        
        offer = response.get("offers", [{}])[0]
        
        return f"""
Offer updated successfully:
Name: {offer.get('name')}
Code: {offer.get('code')}
Display Title: {offer.get('display_title', 'No display title')}
Display Description: {offer.get('display_description', 'No description')}
Type: {offer.get('type')}
Status: {offer.get('status', 'active')}
Cadence: {offer.get('cadence')}
Amount: {offer.get('amount')}
Duration: {offer.get('duration')}
Duration in Months: {offer.get('duration_in_months', 'N/A')}
Currency: {offer.get('currency', 'N/A')}
Tier: {offer.get('tier', {}).get('name', 'Unknown')}
ID: {offer.get('id')}
"""
    except Exception as e:
        if ctx:
            ctx.error(f"Failed to update offer: {str(e)}")
        raise

async def create_offer(
    name: str,
    code: str,
    type: str,
    cadence: str,
    amount: int,
    tier_id: str,
    duration: str,
    display_title: str = None,
    display_description: str = None,
    currency: str = None,
    duration_in_months: int = None,
    ctx: Context = None
) -> str:
    """Create a new offer in Ghost.
    
    Args:
        name: Internal name for the offer (required)
        code: Shortcode for the offer (required)
        type: Either 'percent' or 'fixed' (required)
        cadence: Either 'month' or 'year' (required)
        amount: Discount amount - percentage or fixed value (required)
        tier_id: ID of the tier to apply offer to (required)
        duration: Either 'once', 'forever' or 'repeating' (required)
        display_title: Name displayed in the offer window (optional)
        display_description: Text displayed in the offer window (optional) 
        currency: Required when type is 'fixed', must match tier's currency (optional)
        duration_in_months: Required when duration is 'repeating' (optional)
        ctx: Optional context for logging
    
    Returns:
        String representation of the created offer

    Raises:
        GhostError: If the Ghost API request fails
        ValueError: If required parameters are missing or invalid
    """
    if not all([name, code, type, cadence, amount, tier_id, duration]):
        raise ValueError("Missing required parameters")

    if type not in ['percent', 'fixed']:
        raise ValueError("Type must be either 'percent' or 'fixed'")
        
    if cadence not in ['month', 'year']:
        raise ValueError("Cadence must be either 'month' or 'year'")
        
    if duration not in ['once', 'forever', 'repeating']:
        raise ValueError("Duration must be one of: 'once', 'forever', 'repeating'")
        
    if duration == 'repeating' and not duration_in_months:
        raise ValueError("duration_in_months is required when duration is 'repeating'")
        
    if type == 'fixed' and not currency:
        raise ValueError("Currency is required when type is 'fixed'")

    if ctx:
        ctx.info(f"Creating new offer: {name}")

    # Construct offer data
    offer_data = {
        "offers": [{
            "name": name,
            "code": code,
            "type": type,
            "cadence": cadence,
            "amount": amount,
            "duration": duration,
            "tier": {
                "id": tier_id
            }
        }]
    }

    # Add optional fields if provided
    if display_title:
        offer_data["offers"][0]["display_title"] = display_title
    if display_description:
        offer_data["offers"][0]["display_description"] = display_description
    if currency:
        offer_data["offers"][0]["currency"] = currency
    if duration_in_months:
        offer_data["offers"][0]["duration_in_months"] = duration_in_months

    try:
        if ctx:
            ctx.debug("Getting auth headers")
        headers = await get_auth_headers(STAFF_API_KEY)
        
        if ctx:
            ctx.debug("Making API request to create offer")
        response = await make_ghost_request(
            "offers/",
            headers,
            ctx,
            http_method="POST",
            json_data=offer_data
        )
        
        if ctx:
            ctx.debug("Processing created offer response")
        
        offer = response.get("offers", [{}])[0]
        
        return f"""
Offer created successfully:
Name: {offer.get('name')}
Code: {offer.get('code')}
Display Title: {offer.get('display_title', 'No display title')}
Display Description: {offer.get('display_description', 'No description')}
Type: {offer.get('type')}
Status: {offer.get('status', 'active')}
Cadence: {offer.get('cadence')}
Amount: {offer.get('amount')}
Duration: {offer.get('duration')}
Duration in Months: {offer.get('duration_in_months', 'N/A')}
Currency: {offer.get('currency', 'N/A')}
Tier: {offer.get('tier', {}).get('name', 'Unknown')}
ID: {offer.get('id')}
"""
    except Exception as e:
        if ctx:
            ctx.error(f"Failed to create offer: {str(e)}")
        raise

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
