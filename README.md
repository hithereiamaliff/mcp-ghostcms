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
- **Multi-Tenant Support**: Uses `mcp-key-service` so public/shared deployments never expose raw Ghost credentials in MCP URLs.
- **Firebase Analytics**: Cloud-based analytics storage with Firebase Realtime Database and local file backup.
- **VPS Deployment Ready**: Docker, Nginx, and GitHub Actions auto-deployment support.

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

### Method 3: Self-Hosted VPS with MCP Key Service

For public/shared deployments, this MCP server can be self-hosted on a VPS and resolves Ghost credentials through `mcp-key-service`. Users register their Ghost site URL and admin key once, receive a `usr_XXXXXXXX` key, and only that user key appears in the MCP URL.

#### MCP URL Format

```
https://your-domain.com/ghostcms/mcp/usr_YOUR_USER_KEY
```

Alternative query-param form:

```
https://your-domain.com/ghostcms/mcp?api_key=usr_YOUR_USER_KEY
```

#### Example Usage with Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ghost-myblog": {
      "type": "streamable-http",
      "url": "https://mcp.yourdomain.com/ghostcms/mcp/usr_YOUR_USER_KEY"
    }
  }
}
```

#### Live Demo

A public instance is available at:
```
https://mcp.techmavie.digital/ghostcms/mcp/usr_YOUR_USER_KEY
```

> **Note:** Register your Ghost credentials at `mcpkeys.techmavie.digital` to obtain a `usr_` key first.

### Configuration

This MCP server requires the following configuration:

- **GHOST_API_URL**: Your Ghost site URL (domain only, no path), e.g., `https://yourghostbloginstance.com`
- **GHOST_ADMIN_API_KEY**: Your Ghost Admin API key in `id:secret` format (from Ghost Admin → Settings → Integrations).
- **GHOST_API_VERSION**: Ghost API version (`v5.0` for Ghost 5.x, `v6.0` for Ghost 6.x).
- **GHOST_CONTENT_API_KEY** (optional): Your Ghost Content API key for read-only operations.

For hosted HTTP mode, configure `KEY_SERVICE_URL` and `KEY_SERVICE_TOKEN` on the server, and set `MCP_API_KEY` if you want to protect the analytics endpoints with an `X-API-Key` header.

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

#### MCP Streamable HTTP Requirements

This server implements the MCP Streamable HTTP transport with proper session management and Accept header handling. The server automatically injects `text/event-stream` into Accept headers and creates isolated transport instances per request to prevent session conflicts.

**Testing the endpoint with proper MCP initialization:**
```bash
# Test MCP initialization (proper way to test)
curl -s -X POST \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}' \
  "https://mcp.techmavie.digital/ghostcms/mcp/usr_YOUR_USER_KEY"

# Expected response (SSE format):
# event: message
# data: {"result":{"protocolVersion":"2024-11-05","capabilities":{...},"serverInfo":{...}},"jsonrpc":"2.0","id":1}
```

**Note:** Simple GET/POST requests without MCP initialization will return protocol errors like `"Bad Request: Server not initialized"` - this is expected behavior. The endpoint requires proper MCP protocol handshake.

**For MCP Clients (Claude Desktop, Claude iOS, Claude Code):**
- MCP clients automatically handle the initialization protocol and session management
- Ensure your MCP URL is correctly formatted in your client configuration
- For Claude iOS, use the Connectors feature with the full MCP URL using your `usr_` key
- For Claude Code, add the server to your MCP settings with type `streamable-http`

**Session Management:**
- The server creates a new transport instance for each HTTP request (stateless pattern)
- Each client connection gets a unique session ID automatically
- Multiple clients can connect simultaneously without session conflicts
- Sessions are automatically cleaned up after responses are sent

**Common Errors and Solutions:**

| Error | Cause | Solution |
|-------|-------|----------|
| `"Not Acceptable: Client must accept text/event-stream"` | Old server version | Update to latest version - this is fixed |
| `"Bad Request: Server not initialized"` | Testing without MCP protocol | Use proper MCP initialization (see example above) |
| `"Mcp-Session-Id header is required"` | Old server version with session conflicts | Update to latest version - this is fixed |
| `"Server already initialized"` | Old server version reusing transports | Update to latest version - this is fixed |

## VPS Deployment

This MCP server includes full support for self-hosted VPS deployment with Docker, Nginx, and GitHub Actions auto-deployment.

### Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Claude/MCP     │────▶│  Nginx Proxy    │────▶│  Docker         │
│  Client         │     │  /ghostcms/     │     │  Container      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                        │
                                                        ▼
                                                ┌─────────────────┐
                                                │  Ghost CMS      │
                                                │  Admin API      │
                                                └─────────────────┘
```

### Deployment Files

The repository includes:

- **`Dockerfile`** - Container configuration with Node.js 20-alpine
- **`docker-compose.yml`** - Docker orchestration with volumes for analytics and Firebase credentials
- **`deploy/nginx-mcp.conf`** - Nginx reverse proxy configuration
- **`.github/workflows/deploy-vps.yml`** - GitHub Actions auto-deployment workflow

### Quick Deploy

```bash
# On your VPS
cd /opt/mcp-servers
git clone https://github.com/hithereiamaliff/mcp-ghostcms.git ghostcms
cd ghostcms

# Build and start
docker compose up -d --build

# Check logs
docker compose logs -f
```

### Endpoints

| Endpoint | Description |
|----------|-------------|
| `/health` | Health check |
| `/mcp/:userKey` | MCP endpoint (hosted key-service) |
| `/analytics` | Analytics JSON data |
| `/analytics/dashboard` | Visual analytics dashboard |
| `/analytics/tools` | Tool usage statistics |

## Firebase Analytics

This MCP server uses Firebase Realtime Database for cloud-based analytics storage with local file backup as fallback.

### Features

- **Dual Storage**: Firebase (primary) + local file (backup)
- **Persistent**: Data survives container rebuilds and deployments
- **Real-time**: Updates every 60 seconds
- **Dashboard**: Visual analytics at `/analytics/dashboard`

### Data Tracked

- Total requests and tool calls
- Requests by method (GET, POST, etc.)
- Requests by endpoint
- Tool usage statistics
- Client IPs and user agents
- Hourly request trends
- Recent tool call activity

### Firebase Setup

1. Create a Firebase project at [Firebase Console](https://console.firebase.google.com/)
2. Enable Realtime Database
3. Generate service account credentials (Project Settings → Service Accounts)
4. Copy credentials to your VPS:

```bash
# On VPS
mkdir -p /opt/mcp-servers/ghostcms/.credentials
# Copy firebase-service-account.json to this directory

# Create Docker volume
docker volume create ghostcms_firebase-credentials

# Copy to volume with correct permissions
docker run --rm \
  -v ghostcms_firebase-credentials:/credentials \
  -v /opt/mcp-servers/ghostcms/.credentials:/source:ro \
  alpine sh -c "cp /source/firebase-service-account.json /credentials/ && chown -R 1001:1001 /credentials/"

# Restart container
docker compose down
docker compose up -d
```

### Firebase Data Structure

```
mcp-analytics/
  └── mcp-ghostcms/
      ├── serverStartTime
      ├── totalRequests
      ├── totalToolCalls
      ├── requestsByMethod
      ├── requestsByEndpoint
      ├── toolCalls
      ├── recentToolCalls
      ├── clientsByIp
      ├── clientsByUserAgent
      ├── hourlyRequests
      └── lastUpdated
```

For detailed Firebase setup instructions, see [FIREBASE_SETUP.md](./FIREBASE_SETUP.md).

## Contributing

1. Fork repository
2. Create feature branch
3. Commit changes
4. Create pull request

## License

[MIT](./LICENSE)
