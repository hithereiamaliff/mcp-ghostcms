"""Post-related MCP tools for Ghost API."""

import json
from difflib import get_close_matches
from mcp.server.fastmcp import Context

from ..api import make_ghost_request, get_auth_headers
from ..config import STAFF_API_KEY
from ..exceptions import GhostError

async def search_posts_by_title(query: str, exact: bool = False, ctx: Context = None) -> str:
    """Search for posts by title.
    
    Args:
        query: The title or part of the title to search for
        exact: If True, only return exact matches (default: False)
        ctx: Optional context for logging
    
    Returns:
        Formatted string containing matching post information
        
    Raises:
        GhostError: If there is an error accessing the Ghost API
    """
    if ctx:
        ctx.info(f"Searching posts with title query: {query} (exact: {exact})")
    
    try:
        if ctx:
            ctx.debug("Getting auth headers")
        headers = await get_auth_headers(STAFF_API_KEY)
        
        if ctx:
            ctx.debug("Making API request to /posts/")
        data = await make_ghost_request("posts", headers, ctx)
        
        if ctx:
            ctx.debug("Processing search results")
        
        posts = data.get("posts", [])
        matches = []
        
        if ctx:
            ctx.debug(f"Found {len(posts)} total posts to search through")
        
        if exact:
            if ctx:
                ctx.debug("Performing exact title match")
            matches = [post for post in posts if post.get('title', '').lower() == query.lower()]
        else:
            if ctx:
                ctx.debug("Performing fuzzy title match")
            titles = [post.get('title', '') for post in posts]
            matching_titles = get_close_matches(query, titles, n=5, cutoff=0.3)
            matches = [post for post in posts if post.get('title', '') in matching_titles]
        
        if not matches:
            if ctx:
                ctx.info(f"No posts found matching query: {query}")
            return f"No posts found matching '{query}'"
        
        formatted_matches = []
        for post in matches:
            formatted_match = f"""
Title: {post.get('title', 'Untitled')}
Status: {post.get('status', 'Unknown')}
URL: {post.get('url', 'No URL')}
Created: {post.get('created_at', 'Unknown')}
ID: {post.get('id', 'Unknown')}
"""
            formatted_matches.append(formatted_match)
        
        return "\n---\n".join(formatted_matches)
        
    except GhostError as e:
        if ctx:
            ctx.error(f"Failed to search posts: {str(e)}")
        return str(e)

async def list_posts(
    format: str = "text",
    page: int = 1,
    limit: int = 15,
    ctx: Context = None
) -> str:
    """Get the list of posts from your Ghost blog.
    
    Args:
        format: Output format - either "text" or "json" (default: "text")
        page: Page number for pagination (default: 1)
        limit: Number of posts per page (default: 15)
        ctx: Optional context for logging
    
    Returns:
        Formatted string containing post information
        
    Raises:
        GhostError: If there is an error accessing the Ghost API
    """
    if ctx:
        ctx.info(f"Listing posts (page {page}, limit {limit}, format {format})")
    
    try:
        if ctx:
            ctx.debug("Getting auth headers")
        headers = await get_auth_headers(STAFF_API_KEY)
        
        if ctx:
            ctx.debug("Making API request to /posts/ with pagination")
        data = await make_ghost_request(
            f"posts/?page={page}&limit={limit}",
            headers,
            ctx
        )
        
        if ctx:
            ctx.debug("Processing posts list response")
        
        posts = data.get("posts", [])
        if not posts:
            if ctx:
                ctx.info("No posts found in response")
            return "No posts found."

        if format.lower() == "json":
            if ctx:
                ctx.debug("Formatting posts in JSON format")
            formatted_posts = [{
                "id": post.get('id', 'Unknown'),
                "title": post.get('title', 'Untitled'),
                "status": post.get('status', 'Unknown'),
                "url": post.get('url', 'No URL'),
                "created_at": post.get('created_at', 'Unknown')
            } for post in posts]
            return json.dumps(formatted_posts, indent=2)
        
        formatted_posts = []
        for post in posts:
            formatted_post = f"""
Title: {post.get('title', 'Untitled')}
Status: {post.get('status', 'Unknown')}
URL: {post.get('url', 'No URL')}
Created: {post.get('created_at', 'Unknown')}
ID: {post.get('id', 'Unknown')}
"""
            formatted_posts.append(formatted_post)
        return "\n---\n".join(formatted_posts)
        
    except GhostError as e:
        if ctx:
            ctx.error(f"Failed to list posts: {str(e)}")
        return str(e)

async def read_post(post_id: str, ctx: Context = None) -> str:
    """Get the full content and metadata of a specific blog post.
    
    Args:
        post_id: The ID of the post to retrieve
        ctx: Optional context for logging
        
    Returns:
        Formatted string containing all post details including:
        - Basic info (title, slug, status, etc)
        - Content in both HTML and Lexical formats
        - Feature image details
        - Meta fields (SEO, Open Graph, Twitter)
        - Authors and tags
        - Email settings
        - Timestamps
        
    Raises:
        GhostError: If there is an error accessing the Ghost API
    """
    if ctx:
        ctx.info(f"Reading post content for ID: {post_id}")
    
    try:
        if ctx:
            ctx.debug("Getting auth headers")
        headers = await get_auth_headers(STAFF_API_KEY)
        
        if ctx:
            ctx.debug(f"Making API request to /posts/{post_id}/")
        data = await make_ghost_request(
            f"posts/{post_id}/?formats=html,lexical&include=tags,authors",
            headers,
            ctx
        )
        
        if ctx:
            ctx.debug("Processing post response data")
        
        post = data["posts"][0]
        
        # Format tags and authors
        tags = [tag.get('name', 'Unknown') for tag in post.get('tags', [])]
        authors = [author.get('name', 'Unknown') for author in post.get('authors', [])]
        
        # Get content
        html_content = post.get('html', 'No HTML content available')
        lexical_content = post.get('lexical', 'No Lexical content available')
        
        return f"""
Post Details:

Basic Information:
Title: {post.get('title', 'Untitled')}
Slug: {post.get('slug', 'No slug')}
Status: {post.get('status', 'Unknown')}
Visibility: {post.get('visibility', 'Unknown')}
Featured: {post.get('featured', False)}
URL: {post.get('url', 'No URL')}

Content Formats:
HTML Content:
{html_content}

Lexical Content:
{lexical_content}

Images:
Feature Image: {post.get('feature_image', 'None')}
Feature Image Alt: {post.get('feature_image_alt', 'None')}
Feature Image Caption: {post.get('feature_image_caption', 'None')}

Meta Information:
Meta Title: {post.get('meta_title', 'None')}
Meta Description: {post.get('meta_description', 'None')}
Canonical URL: {post.get('canonical_url', 'None')}
Custom Excerpt: {post.get('custom_excerpt', 'None')}

Open Graph:
OG Image: {post.get('og_image', 'None')}
OG Title: {post.get('og_title', 'None')}
OG Description: {post.get('og_description', 'None')}

Twitter Card:
Twitter Image: {post.get('twitter_image', 'None')}
Twitter Title: {post.get('twitter_title', 'None')}
Twitter Description: {post.get('twitter_description', 'None')}

Code Injection:
Header Code: {post.get('codeinjection_head', 'None')}
Footer Code: {post.get('codeinjection_foot', 'None')}

Template:
Custom Template: {post.get('custom_template', 'None')}

Relationships:
Tags: {', '.join(tags) if tags else 'None'}
Authors: {', '.join(authors) if authors else 'None'}

Email Settings:
Email Only: {post.get('email_only', False)}
Email Subject: {post.get('email', {}).get('subject', 'None')}

Timestamps:
Created: {post.get('created_at', 'Unknown')}
Updated: {post.get('updated_at', 'Unknown')}
Published: {post.get('published_at', 'Not published')}

System IDs:
ID: {post.get('id', 'Unknown')}
UUID: {post.get('uuid', 'Unknown')}
"""
    except GhostError as e:
        if ctx:
            ctx.error(f"Failed to read post: {str(e)}")
        return str(e)

async def create_post(post_data: dict, ctx: Context = None) -> str:
    """Create a new blog post.
    
    Args:
        post_data: Dictionary containing post data with required fields:
            - title: The title of the post 
            - lexical: The lexical content as a JSON string
            Additional optional fields:
            - status: Post status ('draft' or 'published', defaults to 'draft')
            - tags: List of tags
            - authors: List of authors
            - feature_image: URL of featured image
            
            Example:
            {
                "title": "My test post",
                "lexical": "{\"root\":{\"children\":[{\"children\":[{\"detail\":0,\"format\":0,\"mode\":\"normal\",\"style\":\"\",\"text\":\"Hello World\",\"type\":\"text\",\"version\":1}],\"direction\":\"ltr\",\"format\":\"\",\"indent\":0,\"type\":\"paragraph\",\"version\":1}],\"direction\":\"ltr\",\"format\":\"\",\"indent\":0,\"type\":\"root\",\"version\":1}}"
                "status": "draft",
            }
            
        ctx: Optional context for logging

    Returns:
        Formatted string containing the created post details

    Raises:
        GhostError: If there is an error accessing the Ghost API or invalid post data
    """
    if ctx:
        ctx.info(f"Creating post with data: {post_data}")

    if not isinstance(post_data, dict):
        error_msg = "post_data must be a dictionary"
        if ctx:
            ctx.error(error_msg)
        return error_msg

    if 'title' not in post_data and 'lexical' not in post_data:
        error_msg = "post_data must contain at least 'title' or 'lexical'"
        if ctx:
            ctx.error(error_msg)
        return error_msg

    try:
        # Create a copy of post_data to avoid modifying the original
        post_payload = post_data.copy()
        
        # Ensure status is 'draft' by default
        if 'status' not in post_payload:
            post_payload['status'] = 'draft'
            if ctx:
                ctx.debug("Setting default status to 'draft'")
        
        if ctx:
            ctx.debug(f"Post status: {post_payload['status']}")
            ctx.debug("Getting auth headers")
            
        headers = await get_auth_headers(STAFF_API_KEY)
        
        # Ensure lexical is a valid JSON string if present
        if 'lexical' in post_payload:
            try:
                if isinstance(post_payload['lexical'], dict):
                    post_payload['lexical'] = json.dumps(post_payload['lexical'])
                else:
                    # Validate the JSON string
                    json.loads(post_payload['lexical'])
            except json.JSONDecodeError as e:
                error_msg = f"Invalid JSON in lexical content: {str(e)}"
                if ctx:
                    ctx.error(error_msg)
                return error_msg

        # Prepare post creation payload
        request_data = {
            "posts": [post_payload]
        }
        
        if ctx:
            ctx.debug(f"Creating post with data: {json.dumps(request_data)}")

        data = await make_ghost_request(
            "posts/",
            headers,
            ctx,
            http_method="POST",
            json_data=request_data
        )

        if ctx:
            ctx.debug("Post created successfully")

        post = data["posts"][0]

        # Format tags and authors for display
        tags = [tag.get('name', 'Unknown') for tag in post.get('tags', [])]
        authors = [author.get('name', 'Unknown') for author in post.get('authors', [])]

        return f"""
Post Created Successfully:
Title: {post.get('title', 'Untitled')}
Slug: {post.get('slug', 'No slug')}
Status: {post.get('status', 'Unknown')}
URL: {post.get('url', 'No URL')}
Tags: {', '.join(tags) if tags else 'None'}
Authors: {', '.join(authors) if authors else 'None'}
Published At: {post.get('published_at', 'Not published')}
ID: {post.get('id', 'Unknown')}
"""
    except GhostError as e:
        if ctx:
            ctx.error(f"Failed to create post: {str(e)}")
        return str(e)

async def update_post(post_id: str, update_data: dict, ctx: Context = None) -> str:
    """Update a blog post with new data.
    
    Args:
        post_id: The ID of the post to update
        update_data: Dictionary containing the updated data and updated_at timestamp.
                     Note: 'updated_at' is required. If 'lexical' is provided, it must be a valid JSON string.
                     The lexical content must be a properly escaped JSON string in this format:
                     {
                       "root": {
                         "children": [
                           {
                             "children": [
                               {
                                 "detail": 0,
                                 "format": 0,
                                 "mode": "normal",
                                 "style": "",
                                 "text": "Your content here",
                                 "type": "text",
                                 "version": 1
                               }
                             ],
                             "direction": "ltr",
                             "format": "",
                             "indent": 0,
                             "type": "paragraph",
                             "version": 1
                           }
                         ],
                         "direction": "ltr",
                         "format": "",
                         "indent": 0,
                         "type": "root",
                         "version": 1
                       }
                     }
                     
                     Example usage:
                     update_data = {
                         "post_id": "67abcffb7f82ac000179d76f",
                         "update_data": {
                            "updated_at": "2025-02-11T22:54:40.000Z",
                             "lexical": "{\"root\":{\"children\":[{\"children\":[{\"detail\":0,\"format\":0,\"mode\":\"normal\",\"style\":\"\",\"text\":\"Hello World\",\"type\":\"text\",\"version\":1}],\"direction\":\"ltr\",\"format\":\"\",\"indent\":0,\"type\":\"paragraph\",\"version\":1}],\"direction\":\"ltr\",\"format\":\"\",\"indent\":0,\"type\":\"root\",\"version\":1}}"
                         }
                     }
                Updatable fields for a blog post:

                - slug: Unique URL slug for the post.
                - id: Identifier of the post.
                - uuid: Universally unique identifier for the post.
                - title: The title of the post.
                - lexical: JSON string representing the post content in lexical format.
                - html: HTML version of the post content.
                - comment_id: Identifier for the comment thread.
                - feature_image: URL to the post's feature image.
                - feature_image_alt: Alternate text for the feature image.
                - feature_image_caption: Caption for the feature image.
                - featured: Boolean flag indicating if the post is featured.
                - status: The publication status (e.g., published, draft).
                - visibility: Visibility setting (e.g., public, private).
                - created_at: Timestamp when the post was created.
                - updated_at: Timestamp when the post was last updated.
                - published_at: Timestamp when the post was published.
                - custom_excerpt: Custom excerpt text for the post.
                - codeinjection_head: Code to be injected into the head section.
                - codeinjection_foot: Code to be injected into the footer section.
                - custom_template: Custom template assigned to the post.
                - canonical_url: The canonical URL for SEO purposes.
                - tags: List of tag objects associated with the post.
                - authors: List of author objects for the post.
                - primary_author: The primary author object.
                - primary_tag: The primary tag object.
                - url: Direct URL link to the post.
                - excerpt: Short excerpt or summary of the post.
                - og_image: Open Graph image URL for social sharing.
                - og_title: Open Graph title for social sharing.
                - og_description: Open Graph description for social sharing.
                - twitter_image: Twitter-specific image URL.
                - twitter_title: Twitter-specific title.
                - twitter_description: Twitter-specific description.
                - meta_title: Meta title for SEO.
                - meta_description: Meta description for SEO.
                - email_only: Boolean flag indicating if the post is for email distribution only.
                - newsletter: Dictionary containing newsletter configuration details.
                - email: Dictionary containing email details related to the post.
        ctx: Optional context for logging
        
    Returns:
        Formatted string containing the updated post details
        
    Raises:
        GhostError: If there is an error accessing the Ghost API or missing required fields
    """
    if ctx:
        ctx.info(f"Updating post with ID: {post_id}")
    
    try:
        # First, get the current post data to obtain the correct updated_at
        if ctx:
            ctx.debug("Getting current post data")
        headers = await get_auth_headers(STAFF_API_KEY)
        current_post = await make_ghost_request(f"posts/{post_id}/", headers, ctx)
        current_updated_at = current_post["posts"][0]["updated_at"]
        
        # Prepare update payload
        post_update = {
            "posts": [{
                "id": post_id,
                "updated_at": current_updated_at  # Use the current updated_at timestamp
            }]
        }
        
        # Copy all update fields
        for key, value in update_data.items():
            if key != "updated_at":  # Skip updated_at from input
                if key == "tags" and isinstance(value, list):
                    post_update["posts"][0]["tags"] = [
                        {"name": tag} if isinstance(tag, str) else tag 
                        for tag in value
                    ]
                else:
                    post_update["posts"][0][key] = value
        
        if ctx:
            ctx.debug(f"Update payload: {json.dumps(post_update, indent=2)}")
        
        # Make the update request
        data = await make_ghost_request(
            f"posts/{post_id}/",
            headers,
            ctx,
            http_method="PUT",
            json_data=post_update
        )
        
        # Process response...
        post = data["posts"][0]
        
        # Format response...
        tags = [tag.get('name', 'Unknown') for tag in post.get('tags', [])]
        authors = [author.get('name', 'Unknown') for author in post.get('authors', [])]
        
        return f"""
Post Updated Successfully:
Title: {post.get('title', 'Untitled')}
Slug: {post.get('slug', 'No slug')}
Status: {post.get('status', 'Unknown')}
Visibility: {post.get('visibility', 'Unknown')}
Featured: {post.get('featured', False)}
URL: {post.get('url', 'No URL')}
Tags: {', '.join(tags) if tags else 'None'}
Authors: {', '.join(authors) if authors else 'None'}
Published At: {post.get('published_at', 'Not published')}
Updated At: {post.get('updated_at', 'Unknown')}
"""
    except GhostError as e:
        if ctx:
            ctx.error(f"Failed to update post: {str(e)}")
        return str(e)

async def delete_post(post_id: str, ctx: Context = None) -> str:
    """Delete a blog post.
    
    Args:
        post_id: The ID of the post to delete
        ctx: Optional context for logging
        
    Returns:
        Success message if post was deleted
        
    Raises:
        GhostError: If there is an error accessing the Ghost API or the post doesn't exist
    """
    if ctx:
        ctx.info(f"Deleting post with ID: {post_id}")
    
    try:
        if ctx:
            ctx.debug("Getting auth headers")
        headers = await get_auth_headers(STAFF_API_KEY)
        
        # First verify the post exists
        if ctx:
            ctx.debug(f"Verifying post exists: {post_id}")
        try:
            await make_ghost_request(f"posts/{post_id}/", headers, ctx)
        except GhostError as e:
            if "404" in str(e):
                error_msg = f"Post with ID {post_id} not found"
                if ctx:
                    ctx.error(error_msg)
                return error_msg
            raise
            
        # Make the delete request
        if ctx:
            ctx.debug(f"Deleting post: {post_id}")
        await make_ghost_request(
            f"posts/{post_id}/",
            headers,
            ctx,
            http_method="DELETE"
        )
        
        return f"Successfully deleted post with ID: {post_id}"
        
    except GhostError as e:
        if ctx:
            ctx.error(f"Failed to delete post: {str(e)}")
        return str(e)
