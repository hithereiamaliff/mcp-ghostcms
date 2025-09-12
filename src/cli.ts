#!/usr/bin/env node

import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { McpServer, ResourceTemplate } from "@modelcontextprotocol/sdk/server/mcp.js";
import { initGhostApi } from './ghostApi.js';
import { initGhostContentApi } from './ghostContentApi.js';
import {
    handleUserResource,
    handleMemberResource,
    handleTierResource,
    handleOfferResource,
    handleNewsletterResource,
    handlePostResource,
    handleBlogInfoResource
} from './resources.js';
import { registerPostTools } from "./tools/posts.js";
import { registerMemberTools } from "./tools/members.js";
import { registerUserTools } from "./tools/users.js";
import { registerTagTools } from "./tools/tags.js";
import { registerTierTools } from "./tools/tiers.js";
import { registerOfferTools } from "./tools/offers.js";
import { registerNewsletterTools } from "./tools/newsletters.js";
import { registerInviteTools } from "./tools/invites.js";
import { registerRoleTools } from "./tools/roles.js";
import { registerWebhookTools } from "./tools/webhooks.js";
import { registerPrompts } from "./prompts.js";
import { registerDebugTools } from "./tools/debug.js";

/**
 * Standalone MCP server for npm users using stdio transport
 */
async function main() {
    // Read configuration from environment variables
    const config = {
        GHOST_API_URL: process.env.GHOST_API_URL,
        GHOST_ADMIN_API_KEY: process.env.GHOST_ADMIN_API_KEY,
        GHOST_CONTENT_API_KEY: process.env.GHOST_CONTENT_API_KEY,
        GHOST_API_VERSION: process.env.GHOST_API_VERSION || 'v6.0'
    };

    // Validate required configuration
    if (!config.GHOST_API_URL || !config.GHOST_ADMIN_API_KEY) {
        console.error('Error: Required environment variables are missing.');
        console.error('Please set GHOST_API_URL and GHOST_ADMIN_API_KEY');
        console.error('Optionally set GHOST_CONTENT_API_KEY and GHOST_API_VERSION');
        process.exit(1);
    }

    // Initialize Ghost API clients
    initGhostApi({
        url: config.GHOST_API_URL,
        key: config.GHOST_ADMIN_API_KEY,
        version: config.GHOST_API_VERSION,
    });
    
    if (config.GHOST_CONTENT_API_KEY) {
        initGhostContentApi({
            url: config.GHOST_API_URL,
            key: config.GHOST_CONTENT_API_KEY,
            version: config.GHOST_API_VERSION,
        });
    }

    // Create MCP server instance
    const server = new McpServer({
        name: "ghost-mcp-ts",
        version: "0.1.0",
        capabilities: {
            resources: {},
            tools: {},
            prompts: {},
            logging: {}
        }
    });

    // Register resources
    server.resource("user", new ResourceTemplate("user://{user_id}", { list: undefined }), handleUserResource);
    server.resource("member", new ResourceTemplate("member://{member_id}", { list: undefined }), handleMemberResource);
    server.resource("tier", new ResourceTemplate("tier://{tier_id}", { list: undefined }), handleTierResource);
    server.resource("offer", new ResourceTemplate("offer://{offer_id}", { list: undefined }), handleOfferResource);
    server.resource("newsletter", new ResourceTemplate("newsletter://{newsletter_id}", { list: undefined }), handleNewsletterResource);
    server.resource("post", new ResourceTemplate("post://{post_id}", { list: undefined }), handlePostResource);
    server.resource("blog-info", new ResourceTemplate("blog-info://{blog_id}", { list: undefined }), handleBlogInfoResource);

    // Register tools
    registerPostTools(server);
    registerMemberTools(server);
    registerUserTools(server);
    registerTagTools(server);
    registerTierTools(server);
    registerOfferTools(server);
    registerNewsletterTools(server);
    registerInviteTools(server);
    registerRoleTools(server);
    registerWebhookTools(server);
    registerPrompts(server);
    registerDebugTools(server);

    // Create stdio transport and connect the server
    const transport = new StdioServerTransport();
    await server.connect(transport);
}

// Handle process termination gracefully
process.on('SIGINT', () => {
    process.exit(0);
});

process.on('SIGTERM', () => {
    process.exit(0);
});

// Start the server
main().catch((error) => {
    console.error('Failed to start Ghost MCP server:', error);
    process.exit(1);
});