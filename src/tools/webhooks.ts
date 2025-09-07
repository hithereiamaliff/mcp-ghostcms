// src/tools/webhooks.ts
import { z } from "zod";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { getGhostApiConfig, generateGhostAdminToken } from "../ghostApi.js";
import axios from 'axios';

// Parameter schemas as ZodRawShape (object literals)
const addParams = {
  event: z.string(),
  target_url: z.string(),
  name: z.string().optional(),
  secret: z.string().optional(),
  api_version: z.string().optional(),
  integration_id: z.string().optional(), // Required for user-authenticated requests
};
const editParams = {
  id: z.string(),
  event: z.string().optional(),
  target_url: z.string().optional(),
  name: z.string().optional(),
  api_version: z.string().optional(),
};
const deleteParams = {
  id: z.string(),
};

export function registerWebhookTools(server: McpServer) {
  // Add webhook
  server.tool(
    "webhooks_add",
    addParams,
    async (args, _extra) => {
        const config = getGhostApiConfig();
        if (!config) {
            return { isError: true, content: [{ type: "text", text: "Ghost API not configured" }] };
        }
        try {
            const token = generateGhostAdminToken(config.key);
            const url = `${config.url}/ghost/api/admin/webhooks/`;
            const headers = {
                'Authorization': `Ghost ${token}`
            };
            const response = await axios.post(url, { webhooks: [args] }, { headers });
            return {
                content: [
                    {
                        type: "text",
                        text: JSON.stringify(response.data.webhooks[0], null, 2),
                    },
                ],
            };
        } catch (error: any) {
            const status = error?.response?.status ?? error?.status ?? "unknown";
            const body = error?.response?.data ?? error?.data ?? error?.message ?? String(error);
            const bodyText = typeof body === "string" ? body : JSON.stringify(body, null, 2);
            return {
                isError: true,
                content: [
                    {
                        type: "text",
                        text: `webhooks_add failed. status=${status}\n${bodyText}`,
                    },
                ],
            };
        }
    }
  );

  // Edit webhook
  server.tool(
    "webhooks_edit",
    editParams,
    async (args, _extra) => {
        const config = getGhostApiConfig();
        if (!config) {
            return { isError: true, content: [{ type: "text", text: "Ghost API not configured" }] };
        }
        try {
            const token = generateGhostAdminToken(config.key);
            const url = `${config.url}/ghost/api/admin/webhooks/${args.id}/`;
            const headers = {
                'Authorization': `Ghost ${token}`
            };
            const response = await axios.put(url, { webhooks: [args] }, { headers });
            return {
                content: [
                    {
                        type: "text",
                        text: JSON.stringify(response.data.webhooks[0], null, 2),
                    },
                ],
            };
        } catch (error: any) {
            const status = error?.response?.status ?? error?.status ?? "unknown";
            const body = error?.response?.data ?? error?.data ?? error?.message ?? String(error);
            const bodyText = typeof body === "string" ? body : JSON.stringify(body, null, 2);
            return {
                isError: true,
                content: [
                    {
                        type: "text",
                        text: `webhooks_edit failed. status=${status}\n${bodyText}`,
                    },
                ],
            };
        }
    }
  );

  // Delete webhook
  server.tool(
    "webhooks_delete",
    deleteParams,
    async (args, _extra) => {
        const config = getGhostApiConfig();
        if (!config) {
            return { isError: true, content: [{ type: "text", text: "Ghost API not configured" }] };
        }
        try {
            const token = generateGhostAdminToken(config.key);
            const url = `${config.url}/ghost/api/admin/webhooks/${args.id}/`;
            const headers = {
                'Authorization': `Ghost ${token}`
            };
            await axios.delete(url, { headers });
            return {
                content: [
                    {
                        type: "text",
                        text: `Webhook with id ${args.id} deleted.`,
                    },
                ],
            };
        } catch (error: any) {
            const status = error?.response?.status ?? error?.status ?? "unknown";
            const body = error?.response?.data ?? error?.data ?? error?.message ?? String(error);
            const bodyText = typeof body === "string" ? body : JSON.stringify(body, null, 2);
            return {
                isError: true,
                content: [
                    {
                        type: "text",
                        text: `webhooks_delete failed. status=${status}\n${bodyText}`,
                    },
                ],
            };
        }
    }
  );
}