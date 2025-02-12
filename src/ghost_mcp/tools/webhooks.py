"""Webhook-related MCP tools for Ghost API."""

import json
from typing import Optional
from mcp.server.fastmcp import Context

from ..api import make_ghost_request, get_auth_headers
from ..config import STAFF_API_KEY
from ..exceptions import GhostError

async def create_webhook(
    event: str,
    target_url: str,
    integration_id: Optional[str] = None,
    name: Optional[str] = None,
    secret: Optional[str] = None,
    api_version: Optional[str] = None,
    ctx: Context = None
) -> str:
    """Create a new webhook in Ghost.
    
    Args:
        event: Event to trigger the webhook (required)
        target_url: URL to send the webhook to (required)
        integration_id: ID of the integration (optional - only needed for user authentication)
        name: Name of the webhook (optional)
        secret: Secret for the webhook (optional)
        api_version: API version for the webhook (optional)
        ctx: Optional context for logging
    
    Returns:
        String representation of the created webhook

    Raises:
        GhostError: If the Ghost API request fails
        ValueError: If required parameters are missing or invalid
    """
    # List of valid webhook events from Ghost documentation
    valid_events = [
        'site.changed',
        'post.added',
        'post.deleted',
        'post.edited',
        'post.published',
        'post.published.edited',
        'post.unpublished',
        'post.scheduled',
        'post.unscheduled',
        'post.rescheduled',
        'page.added',
        'page.deleted',
        'page.edited',
        'page.published',
        'page.published.edited',
        'page.unpublished',
        'page.scheduled',
        'page.unscheduled',
        'page.rescheduled',
        'tag.added',
        'tag.edited',
        'tag.deleted',
        'post.tag.attached',
        'post.tag.detached',
        'page.tag.attached',
        'page.tag.detached',
        'member.added',
        'member.edited',
        'member.deleted'
    ]

    if not all([event, target_url]):
        raise ValueError("event and target_url are required")
        
    if event not in valid_events:
        raise ValueError(
            f"Invalid event. Must be one of: {', '.join(valid_events)}\n"
            "See Ghost documentation for event descriptions."
        )

    # Ensure target_url has a trailing slash and is a valid URL
    if not target_url.endswith('/'):
        target_url = f"{target_url}/"

    try:
        # Validate URL format
        from urllib.parse import urlparse
        parsed = urlparse(target_url)
        if not all([parsed.scheme, parsed.netloc]):
            raise ValueError
    except ValueError:
        raise ValueError(
            "target_url must be a valid URL in the format 'https://example.com/hook/'"
        )

    if ctx:
        ctx.info(f"Creating webhook for event: {event} targeting: {target_url}")

    # Construct webhook data
    webhook_data = {
        "webhooks": [{
            "event": event,
            "target_url": target_url
        }]
    }

    # Add optional fields if provided
    webhook = webhook_data["webhooks"][0]
    if integration_id:
        webhook["integration_id"] = integration_id
    if name:
        webhook["name"] = name
    if secret:
        webhook["secret"] = secret
    if api_version:
        webhook["api_version"] = api_version

    try:
        if ctx:
            ctx.debug("Getting auth headers")
        headers = await get_auth_headers(STAFF_API_KEY)
        
        if ctx:
            ctx.debug("Making API request to create webhook")
        response = await make_ghost_request(
            "webhooks/",
            headers,
            ctx,
            http_method="POST",
            json_data=webhook_data
        )
        
        if ctx:
            ctx.debug("Processing created webhook response")
        
        webhook = response.get("webhooks", [{}])[0]
        
        return f"""
Webhook created successfully:
Event: {webhook.get('event')}
Target URL: {webhook.get('target_url')}
Name: {webhook.get('name', 'None')}
API Version: {webhook.get('api_version', 'v5')}
Status: {webhook.get('status', 'available')}
Integration ID: {webhook.get('integration_id', 'None')}
Created: {webhook.get('created_at', 'Unknown')}
Last Triggered: {webhook.get('last_triggered_at', 'Never')}
Last Status: {webhook.get('last_triggered_status', 'N/A')}
Last Error: {webhook.get('last_triggered_error', 'None')}
ID: {webhook.get('id')}
"""
    except Exception as e:
        if ctx:
            ctx.error(f"Failed to create webhook: {str(e)}")
        raise

async def delete_webhook(
    webhook_id: str,
    ctx: Context = None
) -> str:
    """Delete a webhook from Ghost.
    
    Args:
        webhook_id: ID of the webhook to delete (required)
        ctx: Optional context for logging
    
    Returns:
        Success message if deletion was successful

    Raises:
        GhostError: If the Ghost API request fails
        ValueError: If webhook_id is not provided
    """
    if not webhook_id:
        raise ValueError("webhook_id is required")

    if ctx:
        ctx.info(f"Attempting to delete webhook with ID: {webhook_id}")

    try:
        if ctx:
            ctx.debug("Getting auth headers")
        headers = await get_auth_headers(STAFF_API_KEY)
        
        if ctx:
            ctx.debug(f"Making API request to delete webhook {webhook_id}")
        response = await make_ghost_request(
            f"webhooks/{webhook_id}/",
            headers,
            ctx,
            http_method="DELETE"
        )
        
        # Check for 204 status code
        if response == {}:
            return f"Webhook with ID {webhook_id} has been successfully deleted."
        else:
            raise GhostError("Unexpected response from Ghost API")
        
    except Exception as e:
        if ctx:
            ctx.error(f"Failed to delete webhook: {str(e)}")
        raise

async def update_webhook(
    webhook_id: str,
    event: Optional[str] = None,
    target_url: Optional[str] = None,
    name: Optional[str] = None,
    api_version: Optional[str] = None,
    ctx: Context = None
) -> str:
    """Update an existing webhook in Ghost.
    
    Args:
        webhook_id: ID of the webhook to update (required)
        event: New event to trigger the webhook (optional)
        target_url: New URL to send the webhook to (optional)
        name: New name of the webhook (optional)
        api_version: New API version for the webhook (optional)
        ctx: Optional context for logging
    
    Returns:
        String representation of the updated webhook

    Raises:
        GhostError: If the Ghost API request fails
        ValueError: If no fields to update are provided or if the event is invalid
    """
    # List of valid webhook events from Ghost documentation
    valid_events = [
        'site.changed',
        'post.added',
        'post.deleted',
        'post.edited',
        'post.published',
        'post.published.edited',
        'post.unpublished',
        'post.scheduled',
        'post.unscheduled',
        'post.rescheduled',
        'page.added',
        'page.deleted',
        'page.edited',
        'page.published',
        'page.published.edited',
        'page.unpublished',
        'page.scheduled',
        'page.unscheduled',
        'page.rescheduled',
        'tag.added',
        'tag.edited',
        'tag.deleted',
        'post.tag.attached',
        'post.tag.detached',
        'page.tag.attached',
        'page.tag.detached',
        'member.added',
        'member.edited',
        'member.deleted'
    ]

    if not any([event, target_url, name, api_version]):
        raise ValueError("At least one field must be provided to update")

    if event and event not in valid_events:
        raise ValueError(
            f"Invalid event. Must be one of: {', '.join(valid_events)}\n"
            "See Ghost documentation for event descriptions."
        )

    if target_url:
        # Ensure target_url has a trailing slash and is a valid URL
        if not target_url.endswith('/'):
            target_url = f"{target_url}/"

        try:
            # Validate URL format
            from urllib.parse import urlparse
            parsed = urlparse(target_url)
            if not all([parsed.scheme, parsed.netloc]):
                raise ValueError
        except ValueError:
            raise ValueError(
                "target_url must be a valid URL in the format 'https://example.com/hook/'"
            )

    if ctx:
        ctx.info(f"Updating webhook with ID: {webhook_id}")

    # Construct webhook data
    webhook_data = {
        "webhooks": [{}]
    }
    webhook = webhook_data["webhooks"][0]

    # Add fields to update
    if event:
        webhook["event"] = event
    if target_url:
        webhook["target_url"] = target_url
    if name:
        webhook["name"] = name
    if api_version:
        webhook["api_version"] = api_version

    try:
        if ctx:
            ctx.debug("Getting auth headers")
        headers = await get_auth_headers(STAFF_API_KEY)
        
        if ctx:
            ctx.debug(f"Making API request to update webhook {webhook_id}")
        response = await make_ghost_request(
            f"webhooks/{webhook_id}/",
            headers,
            ctx,
            http_method="PUT",
            json_data=webhook_data
        )
        
        if ctx:
            ctx.debug("Processing updated webhook response")
        
        webhook = response.get("webhooks", [{}])[0]
        
        return f"""
Webhook updated successfully:
ID: {webhook.get('id')}
Event: {webhook.get('event')}
Target URL: {webhook.get('target_url')}
Name: {webhook.get('name', 'None')}
API Version: {webhook.get('api_version', 'v5')}
Status: {webhook.get('status', 'available')}
Integration ID: {webhook.get('integration_id', 'None')}
Created: {webhook.get('created_at', 'Unknown')}
Updated: {webhook.get('updated_at', 'Unknown')}
Last Triggered: {webhook.get('last_triggered_at', 'Never')}
Last Status: {webhook.get('last_triggered_status', 'N/A')}
Last Error: {webhook.get('last_triggered_error', 'None')}
"""
    except Exception as e:
        if ctx:
            ctx.error(f"Failed to update webhook: {str(e)}")
        raise
