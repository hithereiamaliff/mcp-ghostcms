"""MCP server setup and initialization."""

from mcp.server.fastmcp import FastMCP, Context
from . import tools, resources
from .config import (
    SERVER_NAME,
    SERVER_DEPENDENCIES,
    SERVER_DESCRIPTION
)
from .exceptions import GhostError

def create_server() -> FastMCP:
    """Create and configure the Ghost MCP server.
    
    Returns:
        Configured FastMCP server instance
    """
    # Initialize FastMCP server
    mcp = FastMCP(
        SERVER_NAME,
        dependencies=SERVER_DEPENDENCIES,
        description=SERVER_DESCRIPTION,
        log_level="WARNING"  # Set log level to reduce verbosity
    )

    # Set up error handler
    async def handle_error(error: Exception) -> None:
        if isinstance(error, GhostError):
            mcp.log.error(f"Ghost API Error: {str(error)}")
        else:
            mcp.log.error(f"Server Error: {str(error)}")
    
    mcp.on_error = handle_error
    
    # Register resource handlers
    mcp.resource("user://{user_id}")(resources.handle_user_resource)
    mcp.resource("member://{member_id}")(resources.handle_member_resource)
    mcp.resource("tier://{tier_id}")(resources.handle_tier_resource)
    mcp.resource("offer://{offer_id}")(resources.handle_offer_resource)
    mcp.resource("newsletter://{newsletter_id}")(resources.handle_newsletter_resource)
    mcp.resource("post://{post_id}")(resources.handle_post_resource)
    mcp.resource("blog://info")(resources.handle_blog_info)
    
    mcp.tool()(tools.search_posts_by_title)
    mcp.tool()(tools.list_posts)
    mcp.tool()(tools.read_post)
    mcp.tool()(tools.create_post)
    mcp.tool()(tools.update_post)
    mcp.tool()(tools.delete_post)
    mcp.tool()(tools.list_users)
    mcp.tool()(tools.read_user)
    mcp.tool()(tools.list_members)
    mcp.tool()(tools.read_member)
    mcp.tool()(tools.list_tiers)
    mcp.tool()(tools.read_tier)
    mcp.tool()(tools.list_offers)
    mcp.tool()(tools.read_offer)
    mcp.tool()(tools.list_newsletters)
    mcp.tool()(tools.read_newsletter)
    
    # Register prompts
    @mcp.prompt()
    def search_blog() -> str:
        """Prompt template for searching blog posts"""
        return """I want to help you search the blog posts. You can:
1. Search by title with: search_posts_by_title("your search term")
2. List all posts with: list_posts()
3. Read a specific post with: read_post("post_id")

What would you like to search for?"""

    @mcp.prompt()
    def create_summary(post_id: str) -> str:
        """Create a prompt to summarize a blog post"""
        return f"""Please read the following blog post and provide a concise summary:

Resource: post://{post_id}

Key points to include:
1. Main topic/theme
2. Key arguments or insights
3. Important conclusions
4. Any actionable takeaways"""

    return mcp
