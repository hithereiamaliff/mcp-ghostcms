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

### Usage with Claude Desktop
To use this with Claude Desktop, add the following to your `claude_desktop_config.json`:
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

### Posts Management
- `list_posts`: List blog posts with pagination (supports both text and JSON formats)
- `search_posts_by_title`: Search for posts by title using exact or fuzzy matching
- `read_post`: Retrieve full content of a specific post in HTML or plaintext formats
- `create_post`: Create a new post with specified content and metadata
- `update_post`: Update a specific post with new content and metadata
- `delete_post`: Delete a specific post
- `batchly_update_posts`: Update multiple posts in a single request

### Tags Management
- `browse_tags`: List all tags associated with the blog
- `read_tag`: Retrieve detailed information about a specific tag
- `create_tag`: Create a new tag with specified details
- `update_tag`: Update an existing tag with new information
- `delete_tag`: Delete a specific tag

### Users Management
- `list_roles`: List all available roles
- `create_invite`: Create a new user invitation email and role_id
- `list_users`: List all users with detailed role information
- `read_user`: Get comprehensive details of a specific user
- `delete_user`: Delete a specific user

### Members Management
- `list_members`: List members with subscription and newsletter details
- `read_member`: Retrieve detailed information for a specific member, including subscriptions
- `create_member`: Create a new member with specified details
- `update_member`: Update an existing member's information

### Tiers Management
- `list_tiers`: List all available membership tiers
- `read_tier`: Retrieve detailed information about a specific tier, including benefits and pricing
- `create_tier`: Create a new membership tier with specified details
- `update_tier`: Update an existing tier with new information

### Offers Management
- `list_offers`: List promotional offers with relevant details
- `read_offer`: Get detailed information on a specific offer
- `create_offer`: Create a new promotional offer with specified details
- `update_offer`: Update an existing offer with new information

### Newsletters Management
- `list_newsletters`: List all newsletters associated with the blog
- `read_newsletter`: Retrieve detailed settings and information for a specific newsletter
- `create_newsletter`: Create a new newsletter with specified details
- `update_newsletter`: Update an existing newsletter with new information

### Webhooks Management
- `create_webhook`: Create a new webhook with specified details
- `update_webhook`: Update an existing webhook with new information
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
