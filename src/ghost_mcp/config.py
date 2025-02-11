"""Configuration settings for Ghost MCP server."""

import os
from .exceptions import GhostError

# Ghost API Configuration
API_URL = os.getenv("GHOST_API_URL")
if not API_URL:
    raise GhostError("GHOST_API_URL environment variable is required")

STAFF_API_KEY = os.getenv("GHOST_STAFF_API_KEY")
if not STAFF_API_KEY:
    raise GhostError("GHOST_STAFF_API_KEY environment variable is required")

# Server Configuration
SERVER_NAME = "ghost"
SERVER_DESCRIPTION = "Ghost blog integration providing access to posts, users, members, tiers, offers, newsletters and site information"
SERVER_DEPENDENCIES = ["httpx", "pyjwt"]
