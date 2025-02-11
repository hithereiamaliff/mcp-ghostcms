#!/usr/bin/env python3
"""Main entry point for Ghost MCP server."""

from ghost_mcp import create_server

def main():
    """Initialize and run the Ghost MCP server."""
    mcp = create_server()
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()
