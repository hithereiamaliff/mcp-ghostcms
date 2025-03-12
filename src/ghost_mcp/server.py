"""MCP server setup and initialization."""

from mcp.server.fastmcp import FastMCP, Context
import inspect
from . import tools, resources
from .config import (
    SERVER_NAME,
    SERVER_DEPENDENCIES,
    SERVER_DESCRIPTION
)
from .exceptions import GhostError

def register_resources(mcp: FastMCP) -> None:
    """Register all resource handlers."""
    resource_mappings = {
        "user://{user_id}": resources.handle_user_resource,
        "member://{member_id}": resources.handle_member_resource,
        "tier://{tier_id}": resources.handle_tier_resource,
        "offer://{offer_id}": resources.handle_offer_resource,
        "newsletter://{newsletter_id}": resources.handle_newsletter_resource,
        "post://{post_id}": resources.handle_post_resource,
        "blog://info": resources.handle_blog_info
    }
    
    for uri_template, handler in resource_mappings.items():
        mcp.resource(uri_template)(handler)

def register_tools(mcp: FastMCP) -> None:
    """Register only the main ghost tool (which provides access to all functionality)."""
    # Register only the main ghost tool
    mcp.tool()(tools.ghost)

def register_prompts(mcp: FastMCP) -> None:
    """Register all prompt templates."""
    @mcp.prompt()
    def search_blog() -> str:
        """Prompt template for searching blog posts"""
        return """I want to help you search the blog posts. You can:
1. Search by title with: ghost(action="search_posts_by_title", params={"query": "your search term"})
2. List all posts with: ghost(action="list_posts")
3. Read a specific post with: ghost(action="read_post", params={"post_id": "post_id"})

What would you like to search for?"""

    @mcp.prompt()
    def create_summary(post_id: str) -> str:
        """Create a prompt to summarize a blog post"""
        return f"""Please read the following blog post and provide a concise summary:

Resource: post://{post_id}

Alternatively, you can also get the post content with:
ghost(action="read_post", params={{"post_id": "{post_id}"}})

Key points to include in your summary:
1. Main topic/theme
2. Key arguments or insights
3. Important conclusions
4. Any actionable takeaways"""

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
    
    # Register all components
    register_resources(mcp)
    register_tools(mcp)
    register_prompts(mcp)
    
    return mcp
