"""Tag-related MCP tools for Ghost API."""

import json
from mcp.server.fastmcp import Context

from ..api import make_ghost_request, get_auth_headers
from ..config import STAFF_API_KEY
from ..exceptions import GhostError

async def browse_tags(
    format: str = "text",
    page: int = 1,
    limit: int = 15,
    ctx: Context = None
) -> str:
    """Get the list of tags from your Ghost blog.
    
    Args:
        format: Output format - either "text" or "json" (default: "text")
        page: Page number for pagination (default: 1)
        limit: Number of tags per page (default: 15)
        ctx: Optional context for logging
    
    Returns:
        Formatted string containing tag information
        
    Raises:
        GhostError: If there is an error accessing the Ghost API
    """
    if ctx:
        ctx.info(f"Listing tags (page {page}, limit {limit}, format {format})")
    
    try:
        if ctx:
            ctx.debug("Getting auth headers")
        headers = await get_auth_headers(STAFF_API_KEY)
        
        if ctx:
            ctx.debug("Making API request to /tags/ with pagination")
        data = await make_ghost_request(
            f"tags/?page={page}&limit={limit}",
            headers,
            ctx
        )
        
        if ctx:
            ctx.debug("Processing tags list response")
        
        tags = data.get("tags", [])
        if not tags:
            if ctx:
                ctx.info("No tags found in response")
            return "No tags found."

        if format.lower() == "json":
            if ctx:
                ctx.debug("Formatting tags in JSON format")
            formatted_tags = [{
                "id": tag.get('id', 'Unknown'),
                "name": tag.get('name', 'Unknown'),
                "slug": tag.get('slug', 'Unknown'),
                "description": tag.get('description', None),
                "feature_image": tag.get('feature_image', None),
                "visibility": tag.get('visibility', 'public'),
                "og_image": tag.get('og_image', None),
                "og_title": tag.get('og_title', None),
                "og_description": tag.get('og_description', None),
                "twitter_image": tag.get('twitter_image', None),
                "twitter_title": tag.get('twitter_title', None),
                "twitter_description": tag.get('twitter_description', None),
                "meta_title": tag.get('meta_title', None),
                "meta_description": tag.get('meta_description', None),
                "codeinjection_head": tag.get('codeinjection_head', None),
                "codeinjection_foot": tag.get('codeinjection_foot', None),
                "canonical_url": tag.get('canonical_url', None),
                "accent_color": tag.get('accent_color', None),
                "url": tag.get('url', 'No URL'),
                "created_at": tag.get('created_at', 'Unknown'),
                "updated_at": tag.get('updated_at', 'Unknown')
            } for tag in tags]
            return json.dumps(formatted_tags, indent=2)
        
        formatted_tags = []
        for tag in tags:
            formatted_tag = f"""
ID: {tag.get('id', 'Unknown')}
Name: {tag.get('name', 'Unknown')}
Slug: {tag.get('slug', 'Unknown')}
Description: {tag.get('description', 'None')}
Feature Image: {tag.get('feature_image', 'None')}
Visibility: {tag.get('visibility', 'public')}
URL: {tag.get('url', 'No URL')}
Accent Color: {tag.get('accent_color', 'None')}

Meta Information:
Meta Title: {tag.get('meta_title', 'None')}
Meta Description: {tag.get('meta_description', 'None')}
Canonical URL: {tag.get('canonical_url', 'None')}

Open Graph:
OG Image: {tag.get('og_image', 'None')}
OG Title: {tag.get('og_title', 'None')}
OG Description: {tag.get('og_description', 'None')}

Twitter Card:
Twitter Image: {tag.get('twitter_image', 'None')}
Twitter Title: {tag.get('twitter_title', 'None')}
Twitter Description: {tag.get('twitter_description', 'None')}

Code Injection:
Header Code: {tag.get('codeinjection_head', 'None')}
Footer Code: {tag.get('codeinjection_foot', 'None')}

Timestamps:
Created: {tag.get('created_at', 'Unknown')}
Updated: {tag.get('updated_at', 'Unknown')}
"""
            formatted_tags.append(formatted_tag)
        return "\n---\n".join(formatted_tags)
        
    except GhostError as e:
        if ctx:
            ctx.error(f"Failed to list tags: {str(e)}")
        return str(e)

async def read_tag(tag_id: str, ctx: Context = None) -> str:
    """Get the full metadata of a specific tag.
    
    Args:
        tag_id: The ID of the tag to retrieve
        ctx: Optional context for logging
        
    Returns:
        Formatted string containing all tag details
        
    Raises:
        GhostError: If there is an error accessing the Ghost API
    """
    if ctx:
        ctx.info(f"Reading tag content for ID: {tag_id}")
    
    try:
        if ctx:
            ctx.debug("Getting auth headers")
        headers = await get_auth_headers(STAFF_API_KEY)
        
        if ctx:
            ctx.debug(f"Making API request to /tags/{tag_id}/")
        data = await make_ghost_request(
            f"tags/{tag_id}/",
            headers,
            ctx
        )
        
        if ctx:
            ctx.debug("Processing tag response data")
        
        tag = data["tags"][0]
        
        return f"""
ID: {tag.get('id', 'Unknown')}
Name: {tag.get('name', 'Unknown')}
Slug: {tag.get('slug', 'Unknown')}
Description: {tag.get('description', 'None')}
Feature Image: {tag.get('feature_image', 'None')}
Visibility: {tag.get('visibility', 'public')}
URL: {tag.get('url', 'No URL')}
Accent Color: {tag.get('accent_color', 'None')}

Meta Information:
Meta Title: {tag.get('meta_title', 'None')}
Meta Description: {tag.get('meta_description', 'None')}
Canonical URL: {tag.get('canonical_url', 'None')}

Open Graph:
OG Image: {tag.get('og_image', 'None')}
OG Title: {tag.get('og_title', 'None')}
OG Description: {tag.get('og_description', 'None')}

Twitter Card:
Twitter Image: {tag.get('twitter_image', 'None')}
Twitter Title: {tag.get('twitter_title', 'None')}
Twitter Description: {tag.get('twitter_description', 'None')}

Code Injection:
Header Code: {tag.get('codeinjection_head', 'None')}
Footer Code: {tag.get('codeinjection_foot', 'None')}

Timestamps:
Created: {tag.get('created_at', 'Unknown')}
Updated: {tag.get('updated_at', 'Unknown')}
"""
    except GhostError as e:
        if ctx:
            ctx.error(f"Failed to read tag: {str(e)}")
        return str(e)

async def create_tag(tag_data: dict, ctx: Context = None) -> str:
    """Create a new tag.
    
    Args:
        tag_data: Dictionary containing tag data with required fields:
            - name: The name of the tag
            Additional optional fields:
            - slug: URL slug for the tag
            - description: Description of the tag
            - feature_image: URL to the tag's feature image
            - visibility: Tag visibility ('public' or 'internal')
            - accent_color: CSS color hex value for the tag
            - meta_title: Meta title for SEO
            - meta_description: Meta description for SEO
            - canonical_url: The canonical URL
            - og_image: Open Graph image URL
            - og_title: Open Graph title
            - og_description: Open Graph description
            - twitter_image: Twitter card image URL
            - twitter_title: Twitter card title
            - twitter_description: Twitter card description
            - codeinjection_head: Code to inject in header
            - codeinjection_foot: Code to inject in footer
            
            Example:
            {
                "name": "Technology",
                "description": "Posts about technology",
                "visibility": "public"
            }
            
        ctx: Optional context for logging

    Returns:
        Formatted string containing the created tag details

    Raises:
        GhostError: If there is an error accessing the Ghost API or invalid tag data
    """
    if ctx:
        ctx.info(f"Creating tag with data: {tag_data}")

    if not isinstance(tag_data, dict):
        error_msg = "tag_data must be a dictionary"
        if ctx:
            ctx.error(error_msg)
        return error_msg

    if 'name' not in tag_data:
        error_msg = "tag_data must contain 'name'"
        if ctx:
            ctx.error(error_msg)
        return error_msg

    try:
        if ctx:
            ctx.debug("Getting auth headers")
            
        headers = await get_auth_headers(STAFF_API_KEY)
        
        # Prepare tag creation payload
        request_data = {
            "tags": [tag_data]
        }
        
        if ctx:
            ctx.debug(f"Creating tag with data: {json.dumps(request_data)}")

        data = await make_ghost_request(
            "tags/",
            headers,
            ctx,
            http_method="POST",
            json_data=request_data
        )

        if ctx:
            ctx.debug("Tag created successfully")

        tag = data["tags"][0]

        return f"""
Tag Created Successfully:
ID: {tag.get('id', 'Unknown')}
Name: {tag.get('name', 'Unknown')}
Slug: {tag.get('slug', 'Unknown')}
Description: {tag.get('description', 'None')}
Feature Image: {tag.get('feature_image', 'None')}
Visibility: {tag.get('visibility', 'public')}
URL: {tag.get('url', 'No URL')}
Accent Color: {tag.get('accent_color', 'None')}

Meta Information:
Meta Title: {tag.get('meta_title', 'None')}
Meta Description: {tag.get('meta_description', 'None')}
Canonical URL: {tag.get('canonical_url', 'None')}

Open Graph:
OG Image: {tag.get('og_image', 'None')}
OG Title: {tag.get('og_title', 'None')}
OG Description: {tag.get('og_description', 'None')}

Twitter Card:
Twitter Image: {tag.get('twitter_image', 'None')}
Twitter Title: {tag.get('twitter_title', 'None')}
Twitter Description: {tag.get('twitter_description', 'None')}

Code Injection:
Header Code: {tag.get('codeinjection_head', 'None')}
Footer Code: {tag.get('codeinjection_foot', 'None')}

Timestamps:
Created: {tag.get('created_at', 'Unknown')}
Updated: {tag.get('updated_at', 'Unknown')}
"""
    except GhostError as e:
        if ctx:
            ctx.error(f"Failed to create tag: {str(e)}")
        return str(e)

async def update_tag(tag_id: str, update_data: dict, ctx: Context = None) -> str:
    """Update a tag with new data.
    
    Args:
        tag_id: The ID of the tag to update
        update_data: Dictionary containing the updated data. Fields that can be updated:
            - name: The name of the tag
            - slug: URL slug for the tag
            - description: Description of the tag
            - feature_image: URL to the tag's feature image
            - visibility: Tag visibility ('public' or 'internal')
            - accent_color: CSS color hex value for the tag
            - meta_title: Meta title for SEO
            - meta_description: Meta description for SEO
            - canonical_url: The canonical URL
            - og_image: Open Graph image URL
            - og_title: Open Graph title
            - og_description: Open Graph description
            - twitter_image: Twitter card image URL
            - twitter_title: Twitter card title
            - twitter_description: Twitter card description
            - codeinjection_head: Code to inject in header
            - codeinjection_foot: Code to inject in footer
            
            Example:
            {
                "name": "Updated Name",
                "description": "Updated description"
            }
            
        ctx: Optional context for logging
        
    Returns:
        Formatted string containing the updated tag details
        
    Raises:
        GhostError: If there is an error accessing the Ghost API
    """
    if ctx:
        ctx.info(f"Updating tag with ID: {tag_id}")
    
    try:
        # First, get the current tag data to obtain the correct updated_at
        if ctx:
            ctx.debug("Getting current tag data")
        headers = await get_auth_headers(STAFF_API_KEY)
        current_tag = await make_ghost_request(f"tags/{tag_id}/", headers, ctx)
        current_updated_at = current_tag["tags"][0]["updated_at"]
        
        # Prepare update payload
        tag_update = {
            "tags": [{
                "id": tag_id,
                "updated_at": current_updated_at
            }]
        }
        
        # Copy all update fields
        for key, value in update_data.items():
            if key != "updated_at":  # Skip updated_at from input
                tag_update["tags"][0][key] = value
        
        if ctx:
            ctx.debug(f"Update payload: {json.dumps(tag_update, indent=2)}")
        
        # Make the update request
        data = await make_ghost_request(
            f"tags/{tag_id}/",
            headers,
            ctx,
            http_method="PUT",
            json_data=tag_update
        )
        
        tag = data["tags"][0]
        
        return f"""
Tag Updated Successfully:
ID: {tag.get('id', 'Unknown')}
Name: {tag.get('name', 'Unknown')}
Slug: {tag.get('slug', 'Unknown')}
Description: {tag.get('description', 'None')}
Feature Image: {tag.get('feature_image', 'None')}
Visibility: {tag.get('visibility', 'public')}
URL: {tag.get('url', 'No URL')}
Accent Color: {tag.get('accent_color', 'None')}

Meta Information:
Meta Title: {tag.get('meta_title', 'None')}
Meta Description: {tag.get('meta_description', 'None')}
Canonical URL: {tag.get('canonical_url', 'None')}

Open Graph:
OG Image: {tag.get('og_image', 'None')}
OG Title: {tag.get('og_title', 'None')}
OG Description: {tag.get('og_description', 'None')}

Twitter Card:
Twitter Image: {tag.get('twitter_image', 'None')}
Twitter Title: {tag.get('twitter_title', 'None')}
Twitter Description: {tag.get('twitter_description', 'None')}

Code Injection:
Header Code: {tag.get('codeinjection_head', 'None')}
Footer Code: {tag.get('codeinjection_foot', 'None')}

Timestamps:
Created: {tag.get('created_at', 'Unknown')}
Updated: {tag.get('updated_at', 'Unknown')}
"""
    except GhostError as e:
        if ctx:
            ctx.error(f"Failed to update tag: {str(e)}")
        return str(e)

async def delete_tag(tag_id: str, ctx: Context = None) -> str:
    """Delete a tag.
    
    Args:
        tag_id: The ID of the tag to delete
        ctx: Optional context for logging
        
    Returns:
        Success message if tag was deleted
        
    Raises:
        GhostError: If there is an error accessing the Ghost API or the tag doesn't exist
    """
    if ctx:
        ctx.info(f"Deleting tag with ID: {tag_id}")
    
    try:
        if ctx:
            ctx.debug("Getting auth headers")
        headers = await get_auth_headers(STAFF_API_KEY)
        
        # First verify the tag exists
        if ctx:
            ctx.debug(f"Verifying tag exists: {tag_id}")
        try:
            await make_ghost_request(f"tags/{tag_id}/", headers, ctx)
        except GhostError as e:
            if "404" in str(e):
                error_msg = f"Tag with ID {tag_id} not found"
                if ctx:
                    ctx.error(error_msg)
                return error_msg
            raise
            
        # Make the delete request
        if ctx:
            ctx.debug(f"Deleting tag: {tag_id}")
        await make_ghost_request(
            f"tags/{tag_id}/",
            headers,
            ctx,
            http_method="DELETE"
        )
        
        return f"Successfully deleted tag with ID: {tag_id}"
        
    except GhostError as e:
        if ctx:
            ctx.error(f"Failed to delete tag: {str(e)}")
        return str(e)
