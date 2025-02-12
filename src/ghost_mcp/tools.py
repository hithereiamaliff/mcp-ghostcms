"""MCP tool implementations for Ghost API."""

import json
from difflib import get_close_matches
from mcp.server.fastmcp import FastMCP, Context

from .api import make_ghost_request, get_auth_headers
from .config import STAFF_API_KEY
from .exceptions import GhostError

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

async def read_newsletter(newsletter_id: str, ctx: Context = None) -> str:
    """Get the details of a specific newsletter.
  
    Args:
        newsletter_id: The ID of the newsletter to retrieve
        ctx: Optional context for logging
      
    Returns:
        Formatted string containing the newsletter details
    """
    if ctx:
        ctx.info(f"Reading newsletter details for ID: {newsletter_id}")
    
    try:
        if ctx:
            ctx.debug("Getting auth headers")
        headers = await get_auth_headers(STAFF_API_KEY)
        
        if ctx:
            ctx.debug(f"Making API request to /newsletters/{newsletter_id}/")
        data = await make_ghost_request(
            f"newsletters/{newsletter_id}/",
            headers,
            ctx
        )
        
        if ctx:
            ctx.debug("Processing newsletter response data")
      
        newsletter = data["newsletters"][0]
      
        return f"""
Name: {newsletter.get('name', 'Unknown')}
Description: {newsletter.get('description', 'No description')}
Status: {newsletter.get('status', 'Unknown')}
Visibility: {newsletter.get('visibility', 'Unknown')}
Subscribe on Signup: {newsletter.get('subscribe_on_signup', False)}
Sort Order: {newsletter.get('sort_order', 0)}
Sender Email: {newsletter.get('sender_email', 'Not set')}
Sender Reply To: {newsletter.get('sender_reply_to', 'Not set')}
Show Header Icon: {newsletter.get('show_header_icon', True)}
Show Header Title: {newsletter.get('show_header_title', True)}
Show Header Name: {newsletter.get('show_header_name', True)}
Show Feature Image: {newsletter.get('show_feature_image', True)}
Title Font Category: {newsletter.get('title_font_category', 'Unknown')}
Body Font Category: {newsletter.get('body_font_category', 'Unknown')}
Show Badge: {newsletter.get('show_badge', True)}
Created: {newsletter.get('created_at', 'Unknown')}
Updated: {newsletter.get('updated_at', 'Unknown')}
"""
    except GhostError as e:
        if ctx:
            ctx.error(f"Failed to read newsletter: {str(e)}")
        return str(e)

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

async def list_newsletters(
    format: str = "text",
    page: int = 1,
    limit: int = 15,
    ctx: Context = None
) -> str:
    """Get the list of newsletters from your Ghost blog.
    
    Args:
        format: Output format - either "text" or "json" (default: "text")
        page: Page number for pagination (default: 1)
        limit: Number of newsletters per page (default: 15)
        ctx: Optional context for logging
    
    Returns:
        Formatted string containing newsletter information
    """
    if ctx:
        ctx.info(f"Listing newsletters (page {page}, limit {limit}, format {format})")
    
    try:
        if ctx:
            ctx.debug("Getting auth headers")
        headers = await get_auth_headers(STAFF_API_KEY)
        
        if ctx:
            ctx.debug("Making API request to /newsletters/ with pagination")
        data = await make_ghost_request(
            f"newsletters/?page={page}&limit={limit}",
            headers,
            ctx
        )
        
        if ctx:
            ctx.debug("Processing newsletters list response")
        
        newsletters = data.get("newsletters", [])
        if not newsletters:
            if ctx:
                ctx.info("No newsletters found in response")
            return "No newsletters found."

        if format.lower() == "json":
            if ctx:
                ctx.debug("Returning JSON format")
            return json.dumps(newsletters, indent=2)
        
        formatted_newsletters = []
        for newsletter in newsletters:
            formatted_newsletter = f"""
Name: {newsletter.get('name', 'Unknown')}
Description: {newsletter.get('description', 'No description')}
Status: {newsletter.get('status', 'Unknown')}
Visibility: {newsletter.get('visibility', 'Unknown')}
Subscribe on Signup: {newsletter.get('subscribe_on_signup', False)}
ID: {newsletter.get('id', 'Unknown')}
"""
            formatted_newsletters.append(formatted_newsletter)
        return "\n---\n".join(formatted_newsletters)
        
    except GhostError as e:
        if ctx:
            ctx.error(f"Failed to list newsletters: {str(e)}")
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
        post_data: Dictionary containing post data with at least one of these required fields:
            - title: The title of the post 
            - lexical: The lexical content as a JSON string
            - status: Post status ('draft' or 'published', default: 'draft')
            Additional fields like tags, authors, etc. can also be included.
            
            Example:
            {
                "title": "My test post",
                "lexical": "{\"root\":{\"children\":[{\"children\":[{\"detail\":0,\"format\":0,\"mode\":\"normal\",\"style\":\"\",\"text\":\"Hello World\",\"type\":\"text\",\"version\":1}],\"direction\":\"ltr\",\"format\":\"\",\"indent\":0,\"type\":\"paragraph\",\"version\":1}],\"direction\":\"ltr\",\"format\":\"\",\"indent\":0,\"type\":\"root\",\"version\":1}}",
                "status": "published"
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
        if ctx:
            ctx.debug("Getting auth headers")
        headers = await get_auth_headers(STAFF_API_KEY)
        
        # Ensure lexical is a valid JSON string if present
        if 'lexical' in post_data:
            try:
                if isinstance(post_data['lexical'], dict):
                    post_data['lexical'] = json.dumps(post_data['lexical'])
                else:
                    # Validate the JSON string
                    json.loads(post_data['lexical'])
            except json.JSONDecodeError as e:
                error_msg = f"Invalid JSON in lexical content: {str(e)}"
                if ctx:
                    ctx.error(error_msg)
                return error_msg

        # Prepare post creation payload
        request_data = {
            "posts": [post_data]
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
    """Update a blog post using lexical content.
    
    Args:
        post_id: The ID of the post to update
        update_data: Dictionary containing the lexical content and updated_at timestamp.
                     Expected to have at least 'lexical' and 'updated_at' keys.
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
                             "lexical": "{\"root\":{\"children\":[{\"children\":[{\"detail\":0,\"format\":0,\"mode\":\"normal\",\"style\":\"\",\"text\":\"Hello World\",\"type\":\"text\",\"version\":1}],\"direction\":\"ltr\",\"format\":\"\",\"indent\":0,\"type\":\"paragraph\",\"version\":1}],\"direction\":\"ltr\",\"format\":\"\",\"indent\":0,\"type\":\"root\",\"version\":1}}",
                             "updated_at": "2025-02-11T22:54:40.000Z"
                         }
                     }
        ctx: Optional context for logging
        
    Returns:
        Formatted string containing the updated post details
        
    Raises:
        GhostError: If there is an error accessing the Ghost API or missing required fields
    """
    if ctx:
        ctx.info(f"Updating post with ID: {post_id}")
    
    if 'updated_at' not in update_data:
        error_msg = "updated_at field is required for post updates"
        if ctx:
            ctx.error(error_msg)
        return error_msg

    if 'lexical' not in update_data:
        error_msg = "lexical field is required for post updates"
        if ctx:
            ctx.error(error_msg)
        return error_msg
        
    try:
        if ctx:
            ctx.debug("Getting auth headers")
        headers = await get_auth_headers(STAFF_API_KEY)
        
        # Prepare update payload with lexical content
        post_update = {
            "posts": [{
                "id": post_id,
                "updated_at": update_data["updated_at"],
                "lexical": update_data["lexical"]
            }]
        }
        
        # Optionally handle tag updates if provided
        import copy
        update_fields = copy.deepcopy(update_data)
        if "tags" in update_fields:
            tags = update_fields.pop("tags")
            post_update["posts"][0]["tags"] = [{"name": tag} if isinstance(tag, str) else tag for tag in tags]
        
        # Copy any additional fields
        for key, value in update_fields.items():
            if key not in ["updated_at", "lexical"]:
                post_update["posts"][0][key] = value
        
        if ctx:
            ctx.debug(f"Update payload: {json.dumps(post_update, indent=2)}")
        
        if ctx:
            ctx.debug(f"Making PUT request to /posts/{post_id}/")
        data = await make_ghost_request(
            f"posts/{post_id}/?formats=lexical&include=tags,authors",
            headers,
            ctx,
            http_method="PUT",
            json_data=post_update
        )
        
        if ctx:
            ctx.debug(f"API Response: {json.dumps(data, indent=2)}")
        
        post = data["posts"][0]
        
        # Format tags and authors for display
        tags = [tag.get('name', 'Unknown') for tag in post.get('tags', [])]
        authors = [author.get('name', 'Unknown') for author in post.get('authors', [])]
        
        # Get content preview (lexical content)
        lexical_content = post.get('lexical', '')
        content_preview = lexical_content[:200] + "..." if lexical_content else 'No content available'
        excerpt = post.get('excerpt', 'No excerpt available')
        
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
Content Preview: {content_preview}
Excerpt: {excerpt}
"""
    except GhostError as e:
        if ctx:
            ctx.error(f"Failed to update post: {str(e)}")
        return str(e)

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
