"""Main Ghost meta-tool that provides access to all Ghost functionality."""

import inspect
from mcp.server.fastmcp import Context
from typing import Any, Dict, Optional, List

from .. import tools
from ..exceptions import GhostError

async def ghost(
    action: str,
    params: Optional[Dict[str, Any]] = None,
    ctx: Optional[Context] = None
) -> str:
    """Central Ghost tool that provides access to all Ghost CMS functionality.
    
    Args:
        action: The specific Ghost action to perform.
            Available actions:
            - Posts: list_posts, search_posts_by_title, read_post, create_post, update_post, delete_post, batchly_update_posts
            - Users: list_users, read_user, delete_user, list_roles
            - Members: list_members, read_member, create_member, update_member
            - Tags: browse_tags, read_tag, create_tag, update_tag, delete_tag
            - Tiers: list_tiers, read_tier, create_tier, update_tier
            - Offers: list_offers, read_offer, create_offer, update_offer
            - Newsletters: list_newsletters, read_newsletter, create_newsletter, update_newsletter
            - Webhooks: create_webhook, update_webhook, delete_webhook
            - Invites: create_invite
            
        params: Dictionary of parameters specific to the chosen action.
            Required parameters vary by action.
        ctx: Optional context for logging
        
    Returns:
        Response from the specified Ghost action
        
    Raises:
        GhostError: If there is an error processing the request
    """
    if ctx:
        ctx.info(f"Ghost tool called with action: {action}, params: {params}")
    
    # Validate action
    if action not in tools._all_tools:
        valid_actions = ", ".join(tools._all_tools)
        return f"Invalid action '{action}'. Valid actions are: {valid_actions}"
    
    # Get the function for the specified action
    tool_func = getattr(tools, action)
    if not inspect.isfunction(tool_func):
        return f"Invalid action '{action}'. This is not a valid function."
    
    # Prepare parameters for the function call
    if params is None:
        params = {}
    
    # Add context to params if the function expects it
    sig = inspect.signature(tool_func)
    call_params = params.copy()
    if 'ctx' in sig.parameters:
        call_params['ctx'] = ctx
    
    try:
        # Call the function with the appropriate parameters
        result = await tool_func(**call_params)
        return result
    except GhostError as e:
        if ctx:
            ctx.error(f"Ghost tool error for action '{action}': {str(e)}")
        return f"Error executing '{action}': {str(e)}"
    except TypeError as e:
        # This usually happens when the wrong parameters are provided
        if ctx:
            ctx.error(f"Parameter error for action '{action}': {str(e)}")
        
        # Get the function parameters to provide better error messages
        params_info = []
        for name, param in sig.parameters.items():
            if name == 'ctx':
                continue
            
            param_type = param.annotation.__name__ if param.annotation != inspect.Parameter.empty else "any"
            default = f"(default: {param.default})" if param.default != inspect.Parameter.empty else "(required)"
            params_info.append(f"- {name}: {param_type} {default}")
        
        params_help = "\n".join(params_info)
        return f"Error: {str(e)}\n\nExpected parameters for '{action}':\n{params_help}"
    except Exception as e:
        if ctx:
            ctx.error(f"Unexpected error for action '{action}': {str(e)}")
        return f"Unexpected error executing '{action}': {str(e)}"
