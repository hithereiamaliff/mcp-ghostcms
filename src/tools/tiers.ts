// src/tools/tiers.ts
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
  include: z.string().optional(),
};
const readParams = {
  id: z.string().optional(),
  slug: z.string().optional(),
  include: z.string().optional(),
};
const addParams = {
  name: z.string(),
  description: z.string().optional(),
  welcome_page_url: z.string().optional(),
  visibility: z.string().optional(),
  monthly_price: z.number().optional(),
  yearly_price: z.number().optional(),
  currency: z.string().optional(),
  benefits: z.array(z.string()).optional(),
  // Add more fields as needed
};
const editParams = {
  id: z.string(),
  name: z.string().optional(),
  description: z.string().optional(),
  welcome_page_url: z.string().optional(),
  visibility: z.string().optional(),
  monthly_price: z.number().optional(),
  yearly_price: z.number().optional(),
  currency: z.string().optional(),
  benefits: z.array(z.string()).optional(),
  // Add more fields as needed
};
const deleteParams = {
  id: z.string(),
};

export function registerTierTools(server: McpServer) {
  // Browse tiers
  server.tool(
    "tiers_browse",
    browseParams,
    async (args, _extra) => {
        const config = getGhostApiConfig();
        if (!config) {
            return { isError: true, content: [{ type: "text", text: "Ghost API not configured" }] };
        }
        try {
            const token = generateGhostAdminToken(config.key);
            const url = `${config.url}/ghost/api/admin/tiers/`;
            const headers = {
                'Authorization': `Ghost ${token}`
            };
            const response = await axios.get(url, { params: args, headers });
            return {
                content: [
                    {
                        type: "text",
                        text: JSON.stringify(response.data.tiers, null, 2),
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
                        text: `tiers_browse failed. status=${status}\n${bodyText}`,
                    },
                ],
            };
        }
    }
  );

  // Read tier
  server.tool(
    "tiers_read",
    readParams,
    async (args, _extra) => {
        const config = getGhostApiConfig();
        if (!config) {
            return { isError: true, content: [{ type: "text", text: "Ghost API not configured" }] };
        }
        try {
            const token = generateGhostAdminToken(config.key);
            const url = `${config.url}/ghost/api/admin/tiers/${args.id}/`;
            const headers = {
                'Authorization': `Ghost ${token}`
            };
            const response = await axios.get(url, { headers });
            return {
                content: [
                    {
                        type: "text",
                        text: JSON.stringify(response.data.tiers[0], null, 2),
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
                        text: `tiers_read failed. status=${status}\n${bodyText}`,
                    },
                ],
            };
        }
    }
  );

  // Add tier
  server.tool(
    "tiers_add",
    addParams,
    async (args, _extra) => {
        const config = getGhostApiConfig();
        if (!config) {
            return { isError: true, content: [{ type: "text", text: "Ghost API not configured" }] };
        }
        try {
            const token = generateGhostAdminToken(config.key);
            const url = `${config.url}/ghost/api/admin/tiers/`;
            const headers = {
                'Authorization': `Ghost ${token}`
            };
            const response = await axios.post(url, { tiers: [args] }, { headers });
            return {
                content: [
                    {
                        type: "text",
                        text: JSON.stringify(response.data.tiers[0], null, 2),
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
                        text: `tiers_add failed. status=${status}\n${bodyText}`,
                    },
                ],
            };
        }
    }
  );

  // Edit tier
  server.tool(
    "tiers_edit",
    editParams,
    async (args, _extra) => {
        const config = getGhostApiConfig();
        if (!config) {
            return { isError: true, content: [{ type: "text", text: "Ghost API not configured" }] };
        }
        try {
            const token = generateGhostAdminToken(config.key);
            const url = `${config.url}/ghost/api/admin/tiers/${args.id}/`;
            const headers = {
                'Authorization': `Ghost ${token}`
            };
            const response = await axios.put(url, { tiers: [args] }, { headers });
            return {
                content: [
                    {
                        type: "text",
                        text: JSON.stringify(response.data.tiers[0], null, 2),
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
                        text: `tiers_edit failed. status=${status}\n${bodyText}`,
                    },
                ],
            };
        }
    }
  );

  // Delete tier
  server.tool(
    "tiers_delete",
    deleteParams,
    async (args, _extra) => {
        const config = getGhostApiConfig();
        if (!config) {
            return { isError: true, content: [{ type: "text", text: "Ghost API not configured" }] };
        }
        try {
            const token = generateGhostAdminToken(config.key);
            const url = `${config.url}/ghost/api/admin/tiers/${args.id}/`;
            const headers = {
                'Authorization': `Ghost ${token}`
            };
            await axios.delete(url, { headers });
            return {
                content: [
                    {
                        type: "text",
                        text: `Tier with id ${args.id} deleted.`,
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
                        text: `tiers_delete failed. status=${status}\n${bodyText}`,
                    },
                ],
            };
        }
    }
  );
}