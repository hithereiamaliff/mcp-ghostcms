#!/usr/bin/env node

// Use ESM imports for MCP SDK subpaths (package exports only expose subpaths)
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
import { configSchema, ConfigType } from './configSchema.js';
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

// Export the configuration schema for Smithery
export { configSchema };

/**
 * Create and configure the MCP server with HTTP transport
 * This is the main entry point for Smithery
 */
export default function createServer({ config }: { config: ConfigType }) {
    // Initialize Ghost API client with Smithery-provided runtime config
    initGhostApi({
        url: config.GHOST_API_URL,
        key: config.GHOST_ADMIN_API_KEY,
        version: config.GHOST_API_VERSION,
    });
    initGhostContentApi({
        url: config.GHOST_API_URL,
        key: config.GHOST_CONTENT_API_KEY,
        version: config.GHOST_API_VERSION,
    });
    // Create an MCP server instance
    const server = new McpServer({
        name: "ghost-mcp-ts",
        version: "0.1.0",
        capabilities: {
            resources: {}, // Capabilities will be enabled as handlers are registered
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

    // Return the server instance for Smithery to handle
    // Smithery will create the HTTP transport and connect it

    return server.server;
}