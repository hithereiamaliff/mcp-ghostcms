# Ghost MCP Server

[![smithery badge](https://smithery.ai/badge/@hithereiamaliff/mcp-ghostcms)](https://smithery.ai/server/@hithereiamaliff/mcp-ghostcms)
> This is a fork of [MFYDev/ghost-mcp](https://github.com/MFYDev/ghost-mcp), now maintained and improved by [@hithereiamaliff](https://github.com/hithereiamaliff/mcp-ghostcms).

This Model Context Protocol (MCP) server provides a powerful and flexible way to manage your Ghost CMS instance using Large Language Model (LLM) interfaces. It offers comprehensive and secure access to your blog's administrative functions, allowing you to automate and streamline your content management workflows.

## Features

- **Robust API Integration**: Utilizes direct, authenticated `axios` calls for all Admin API operations, ensuring a stable and reliable connection that is not dependent on external libraries.
- **Comprehensive Entity Access**: Manages posts, users, members, tiers, offers, and newsletters.
- **Enhanced Error Handling**: Provides detailed status codes and response bodies.
- **Modern Transport**: Exclusively uses the Streamable HTTP transport, with all deprecated STDIO logic removed.
- **Diagnostic Tools**: Includes tools for troubleshooting API connectivity and configuration.

## Installation & Usage

This MCP server is available through two deployment methods:

### Method 1: NPM Package (Recommended for MCP Clients)

Install directly from npm:

```bash
npm install -g mcp-ghostcms
```

Or use with npx (no installation required):

```bash
npx mcp-ghostcms
```

#### Using with Claude Desktop

To use with MCP clients like Claude Desktop, add the following to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
      "mcp-ghostcms": {
        "command": "npx",
        "args": ["-y", "mcp-ghostcms"],
        "env": {
            "GHOST_API_URL": "https://yourghostbloginstance.com",
            "GHOST_ADMIN_API_KEY": "your_admin_api_key",
            "GHOST_API_VERSION": "v6.0"
        }
      }
    }
}
```

### Method 2: Smithery Cloud Platform

Deploy and run on Smithery's cloud platform:

[![smithery badge](https://smithery.ai/badge/@hithereiamaliff/mcp-ghostcms)](https://smithery.ai/server/@hithereiamaliff/mcp-ghostcms)

Or for local development with Smithery:

```bash
git clone <this-repo>
cd ghost-mcp
npm install
npm run dev
```

This will start the server on port 8080 and open the Smithery Playground in your browser.

### Configuration

This MCP server requires the following configuration:

- **GHOST_API_URL**: Your Ghost site URL (domain only, no path), e.g., `https://yourghostbloginstance.com`
- **GHOST_ADMIN_API_KEY**: Your Ghost Admin API key in `id:secret` format (from Ghost Admin → Settings → Integrations).
- **GHOST_API_VERSION**: Ghost API version (`v5.0` for Ghost 5.x, `v6.0` for Ghost 6.x).
- **GHOST_CONTENT_API_KEY** (optional): Your Ghost Content API key for read-only operations.

## Available Resources

The following Ghost CMS resources are available through this MCP server:

- **Posts**: Articles and content published on your Ghost site.
- **Members**: Registered users and subscribers of your site.
- **Newsletters**: Email newsletters managed and sent via Ghost.
- **Offers**: Promotional offers and discounts for members.
- **Invites**: Invitations for new users or staff to join your Ghost site.
- **Roles**: User roles and permissions within the Ghost admin.
- **Tags**: Organizational tags for posts and content.
- **Tiers**: Subscription tiers and plans for members.
- **Users**: Admin users and staff accounts.
- **Webhooks**: Automated event notifications to external services.

## Available Tools

This MCP server provides a wide array of tools to manage your Ghost CMS. These tools are exposed via the Model Context Protocol and allow for a full range of CRUD (Create, Read, Update, Delete) operations on your blog's resources. Below is an overview of the available toolset:

### Posts
- **Browse Posts**: List posts with optional filters, pagination, and ordering.
- **Read Post**: Retrieve a post by ID or slug.
- **Add Post**: Create a new post with title, content, and status.
- **Edit Post**: Update an existing post by ID.
- **Delete Post**: Remove a post by ID.

### Members
- **Browse Members**: List members with filters and pagination.
- **Read Member**: Retrieve a member by ID or email.
- **Add Member**: Create a new member.
- **Edit Member**: Update member details.
- **Delete Member**: Remove a member.

### Newsletters
- **Browse Newsletters**: List newsletters.
- **Read Newsletter**: Retrieve a newsletter by ID.
- **Add Newsletter**: Create a new newsletter.
- **Edit Newsletter**: Update newsletter details.
- **Delete Newsletter**: Remove a newsletter.

### Offers
- **Browse Offers**: List offers.
- **Read Offer**: Retrieve an offer by ID.
- **Add Offer**: Create a new offer.
- **Edit Offer**: Update offer details.
- **Delete Offer**: Remove an offer.

### Invites
- **Browse Invites**: List invites.
- **Add Invite**: Create a new invite.
- **Delete Invite**: Remove an invite.

### Roles
- **Browse Roles**: List roles.
- **Read Role**: Retrieve a role by ID.

### Tags
- **Browse Tags**: List tags.
- **Read Tag**: Retrieve a tag by ID or slug.
- **Add Tag**: Create a new tag.
- **Edit Tag**: Update tag details.
- **Delete Tag**: Remove a tag.

### Tiers
- **Browse Tiers**: List tiers.
- **Read Tier**: Retrieve a tier by ID.
- **Add Tier**: Create a new tier.
- **Edit Tier**: Update tier details.
- **Delete Tier**: Remove a tier.

### Users
- **Browse Users**: List users.
- **Read User**: Retrieve a user by ID or slug.
- **Edit User**: Update user details.
- **Delete User**: Remove a user.

### Webhooks
- **Browse Webhooks**: List webhooks.
- **Add Webhook**: Create a new webhook.
- **Delete Webhook**: Remove a webhook.

> Each tool is accessible via the MCP protocol and can be invoked from compatible clients. For detailed parameter schemas and usage, see the source code in `src/tools/`.

## Error Handling & Diagnostics

This fork includes enhanced error handling that provides detailed information about API failures:

- HTTP status codes are captured and reported
- Full response bodies are included in error messages
- Runtime configuration is logged at startup
- Diagnostic tools are available to troubleshoot connectivity issues:
  - `admin_site_ping`: Tests if the Ghost Admin API endpoint is reachable
  - `config_echo`: Shows the current Ghost API configuration (with masked key)

These improvements make it much easier to diagnose common issues like:
- Incorrect API URL format
- Missing or malformed Admin API keys
- API version mismatches
- Network/proxy configuration problems

## Development

### Setup

1. Clone the repository
2. Install dependencies: `npm install`
3. Create a `.env` file with your Ghost configuration:
   ```
   GHOST_API_URL=https://yourghostbloginstance.com
   GHOST_ADMIN_API_KEY=your_admin_api_key
   GHOST_API_VERSION=v6.0
   ```
4. Build the project: `npm run build`
5. Start the dev server: `npm run dev`

### Troubleshooting

If you encounter authentication or "Resource not found" errors:

1.  Verify your Ghost Admin API key is in the correct `id:secret` format.
2.  Ensure your `GHOST_API_URL` is the correct domain for your Ghost instance.
3.  Use the `admin_site_ping` tool to verify that the Admin API endpoint is reachable.
4.  Check the server logs for the actual configuration being used.

## Contributing

1. Fork repository
2. Create feature branch
3. Commit changes
4. Create pull request

## License

[MIT](./LICENSE)