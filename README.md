# Ghost MCP Server

[![smithery badge](https://smithery.ai/badge/@MFYDev/ghost-mcp)](https://smithery.ai/server/@MFYDev/ghost-mcp)

<a href="https://glama.ai/mcp/servers/vor63xn7ky"><img width="380" height="200" src="https://glama.ai/mcp/servers/vor63xn7ky/badge" alt="Ghost Server MCP server" /></a>

A Model Context Protocol (MCP) server for interacting with Ghost CMS through LLM interfaces like Claude. This server provides secure and comprehensive access to your Ghost blog, leveraging JWT authentication and a rich set of MCP tools for managing posts, users, members, tiers, offers, and newsletters.

![demo](./assets/ghost-mcp-demo.gif)

## Features

- Secure JWT Authentication for Ghost Admin API requests
- Comprehensive entity access including posts, users, members, tiers, offers, and newsletters
- Advanced search functionality with both fuzzy and exact matching options
- Detailed, human-readable output for Ghost entities
- Robust error handling using custom `GhostError` exceptions
- Integrated logging support via MCP context for enhanced troubleshooting

## Installation

### Installing via Smithery

To install Ghost MCP Server for Claude Desktop automatically via [Smithery](https://smithery.ai/server/@MFYDev/ghost-mcp):

```bash
npx -y @smithery/cli install @MFYDev/ghost-mcp --client claude
```

### Manual Installation
```bash
# Clone repository
git clone git@github.com/mfydev/ghost-mcp.git
cd ghost-mcp

# Create virtual environment and install
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

## Requirements

- Python ≥ 3.12
- Running Ghost instance with Admin API access (v5.x+ recommended)
- Node.js (for testing with MCP Inspector)

## Usage

### Environment Variables

```bash
GHOST_API_URL=https://yourblog.com  # Your Ghost Admin API URL
GHOST_STAFF_API_KEY=your_staff_api_key                 # Your Ghost Staff API key
```

### Usage with MCP Clients
To use this with MCP clients, for instance, Claude Desktop, add the following to your `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "ghost": {
      "command": "/Users/username/.local/bin/uv",
      "args": [
        "--directory",
        "/path/to/ghost-mcp",
        "run",
        "src/main.py"
      ],
      "env": {
        "GHOST_API_URL": "your_ghost_api_url",
        "GHOST_STAFF_API_KEY": "your_staff_api_key"
      }
    }
  }
}
```

### Testing with MCP Inspector

```bash
GHOST_API_URL=your_ghost_api_url GHOST_STAFF_API_KEY=your_staff_api_key npx @modelcontextprotocol/inspector uv --directory /path/to/ghost-mcp run src/main.py
```

## Available Tools

Ghost MCP now provides a single unified tool that provides access to all Ghost CMS functionality:

### Main Tool
- `ghost`: Central tool for accessing all Ghost CMS functionality

### Using the Ghost Tool

The ghost tool accepts two main parameters:
1. `action`: The specific Ghost operation to perform
2. `params`: A dictionary of parameters for the specified action

Example usage:
```python
# List posts
ghost(action="list_posts", params={"format": "text", "page": 1, "limit": 15})

# Search posts by title
ghost(action="search_posts_by_title", params={"query": "Welcome", "exact": False})

# Create a post
ghost(action="create_post", params={
    "post_data": {
        "title": "New Post via MCP",
        "status": "draft",
        "lexical": "{\"root\":{\"children\":[{\"children\":[{\"detail\":0,\"format\":0,\"mode\":\"normal\",\"style\":\"\",\"text\":\"Hello World\",\"type\":\"text\",\"version\":1}],\"direction\":\"ltr\",\"format\":\"\",\"indent\":0,\"type\":\"paragraph\",\"version\":1}],\"direction\":\"ltr\",\"format\":\"\",\"indent\":0,\"type\":\"root\",\"version\":1}}"
    }
})
```

### Available Actions

The ghost tool supports all the same actions as before, but now through a unified interface:

#### Posts Actions
- `list_posts`: List blog posts with pagination
- `search_posts_by_title`: Search for posts by title
- `read_post`: Retrieve full content of a specific post
- `create_post`: Create a new post
- `update_post`: Update a specific post
- `delete_post`: Delete a specific post
- `batchly_update_posts`: Update multiple posts in a single request

#### Tags Actions
- `browse_tags`: List all tags
- `read_tag`: Retrieve specific tag information
- `create_tag`: Create a new tag
- `update_tag`: Update an existing tag
- `delete_tag`: Delete a specific tag

#### Users Actions
- `list_roles`: List all available roles
- `create_invite`: Create a new user invitation
- `list_users`: List all users
- `read_user`: Get details of a specific user
- `delete_user`: Delete a specific user

#### Members Actions
- `list_members`: List members
- `read_member`: Retrieve specific member information
- `create_member`: Create a new member
- `update_member`: Update an existing member

#### Tiers Actions
- `list_tiers`: List all membership tiers
- `read_tier`: Retrieve specific tier information
- `create_tier`: Create a new tier
- `update_tier`: Update an existing tier

#### Offers Actions
- `list_offers`: List promotional offers
- `read_offer`: Get specific offer information
- `create_offer`: Create a new offer
- `update_offer`: Update an existing offer

#### Newsletters Actions
- `list_newsletters`: List all newsletters
- `read_newsletter`: Retrieve specific newsletter information
- `create_newsletter`: Create a new newsletter
- `update_newsletter`: Update an existing newsletter

#### Webhooks Actions
- `create_webhook`: Create a new webhook
- `update_webhook`: Update an existing webhook
- `delete_webhook`: Delete a specific webhook

## Available Resources

All resources follow the URI pattern: `[type]://[id]`

- `user://{user_id}`: User profiles and roles
- `member://{member_id}`: Member details and subscriptions
- `tier://{tier_id}`: Tier configurations
- `offer://{offer_id}`: Offer details
- `newsletter://{newsletter_id}`: Newsletter settings
- `post://{post_id}`: Post content and metadata
- `blog://info`: General blog information

## Error Handling

Ghost MCP Server employs a custom `GhostError` exception to handle API communication errors and processing issues. This ensures clear and descriptive error messages to assist with troubleshooting.

## Contributing

1. Fork repository
2. Create feature branch
3. Commit changes
4. Create pull request

## License

MIT
