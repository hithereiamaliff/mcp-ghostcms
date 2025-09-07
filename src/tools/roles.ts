// src/tools/roles.ts
import { z } from "zod";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { getGhostApiConfig, generateGhostAdminToken } from "../ghostApi.js";
import axios from 'axios';

// Parameter schemas as ZodRawShape (object literals)
const browseParams = {
  filter: z.string().optional(),
  limit: z.number().optional(),
  page: z.number().optional(),
  order: z.string().optional(),
};
const readParams = {
  id: z.string().optional(),
  name: z.string().optional(),
};

export function registerRoleTools(server: McpServer) {
  // Browse roles
  server.tool(
    "roles_browse",
    browseParams,
    async (args, _extra) => {
        const config = getGhostApiConfig();
        if (!config) {
            return { isError: true, content: [{ type: "text", text: "Ghost API not configured" }] };
        }
        try {
            const token = generateGhostAdminToken(config.key);
            const url = `${config.url}/ghost/api/admin/roles/`;
            const headers = {
                'Authorization': `Ghost ${token}`
            };
            const response = await axios.get(url, { params: args, headers });
            return {
                content: [
                    {
                        type: "text",
                        text: JSON.stringify(response.data.roles, null, 2),
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
                        text: `roles_browse failed. status=${status}\n${bodyText}`,
                    },
                ],
            };
        }
    }
  );

  // Read role
  server.tool(
    "roles_read",
    readParams,
    async (args, _extra) => {
        const config = getGhostApiConfig();
        if (!config) {
            return { isError: true, content: [{ type: "text", text: "Ghost API not configured" }] };
        }
        try {
            const token = generateGhostAdminToken(config.key);
            const url = `${config.url}/ghost/api/admin/roles/${args.id}/`;
            const headers = {
                'Authorization': `Ghost ${token}`
            };
            const response = await axios.get(url, { headers });
            return {
                content: [
                    {
                        type: "text",
                        text: JSON.stringify(response.data.roles[0], null, 2),
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
                        text: `roles_read failed. status=${status}\n${bodyText}`,
                    },
                ],
            };
        }
    }
  );
}