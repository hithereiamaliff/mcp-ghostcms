// src/tools/newsletters.ts
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
  slug: z.string().optional(),
};
const addParams = {
  name: z.string(),
  description: z.string().optional(),
  sender_reply_to: z.string().optional(),
  status: z.string().optional(),
  subscribe_on_signup: z.boolean().optional(),
  show_header_icon: z.boolean().optional(),
  show_header_title: z.boolean().optional(),
  show_header_name: z.boolean().optional(),
  title_font_category: z.string().optional(),
  title_alignment: z.string().optional(),
  show_feature_image: z.boolean().optional(),
  body_font_category: z.string().optional(),
  show_badge: z.boolean().optional(),
  // Add more fields as needed
};
const editParams = {
  id: z.string(),
  name: z.string().optional(),
  description: z.string().optional(),
  sender_name: z.string().optional(),
  sender_email: z.string().optional(),
  sender_reply_to: z.string().optional(),
  status: z.string().optional(),
  subscribe_on_signup: z.boolean().optional(),
  sort_order: z.number().optional(),
  header_image: z.string().optional(),
  show_header_icon: z.boolean().optional(),
  show_header_title: z.boolean().optional(),
  title_font_category: z.string().optional(),
  title_alignment: z.string().optional(),
  show_feature_image: z.boolean().optional(),
  body_font_category: z.string().optional(),
  footer_content: z.string().optional(),
  show_badge: z.boolean().optional(),
  show_header_name: z.boolean().optional(),
  // Add more fields as needed
};
const deleteParams = {
  id: z.string(),
};

export function registerNewsletterTools(server: McpServer) {
  // Browse newsletters
  server.tool(
    "newsletters_browse",
    browseParams,
    async (args, _extra) => {
        const config = getGhostApiConfig();
        if (!config) {
            return { isError: true, content: [{ type: "text", text: "Ghost API not configured" }] };
        }
        try {
            const token = generateGhostAdminToken(config.key);
            const url = `${config.url}/ghost/api/admin/newsletters/`;
            const headers = {
                'Authorization': `Ghost ${token}`
            };
            const response = await axios.get(url, { params: args, headers });
            return {
                content: [
                    {
                        type: "text",
                        text: JSON.stringify(response.data.newsletters, null, 2),
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
                        text: `newsletters_browse failed. status=${status}\n${bodyText}`,
                    },
                ],
            };
        }
    }
  );

  // Read newsletter
  server.tool(
    "newsletters_read",
    readParams,
    async (args, _extra) => {
        const config = getGhostApiConfig();
        if (!config) {
            return { isError: true, content: [{ type: "text", text: "Ghost API not configured" }] };
        }
        try {
            const token = generateGhostAdminToken(config.key);
            const url = `${config.url}/ghost/api/admin/newsletters/${args.id}/`;
            const headers = {
                'Authorization': `Ghost ${token}`
            };
            const response = await axios.get(url, { headers });
            return {
                content: [
                    {
                        type: "text",
                        text: JSON.stringify(response.data.newsletters[0], null, 2),
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
                        text: `newsletters_read failed. status=${status}\n${bodyText}`,
                    },
                ],
            };
        }
    }
  );

  // Add newsletter
  server.tool(
    "newsletters_add",
    addParams,
    async (args, _extra) => {
        const config = getGhostApiConfig();
        if (!config) {
            return { isError: true, content: [{ type: "text", text: "Ghost API not configured" }] };
        }
        try {
            const token = generateGhostAdminToken(config.key);
            const url = `${config.url}/ghost/api/admin/newsletters/`;
            const headers = {
                'Authorization': `Ghost ${token}`
            };
            const response = await axios.post(url, { newsletters: [args] }, { headers });
            return {
                content: [
                    {
                        type: "text",
                        text: JSON.stringify(response.data.newsletters[0], null, 2),
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
                        text: `newsletters_add failed. status=${status}\n${bodyText}`,
                    },
                ],
            };
        }
    }
  );

  // Edit newsletter
  server.tool(
    "newsletters_edit",
    editParams,
    async (args, _extra) => {
        const config = getGhostApiConfig();
        if (!config) {
            return { isError: true, content: [{ type: "text", text: "Ghost API not configured" }] };
        }
        try {
            const token = generateGhostAdminToken(config.key);
            const url = `${config.url}/ghost/api/admin/newsletters/${args.id}/`;
            const headers = {
                'Authorization': `Ghost ${token}`
            };
            const response = await axios.put(url, { newsletters: [args] }, { headers });
            return {
                content: [
                    {
                        type: "text",
                        text: JSON.stringify(response.data.newsletters[0], null, 2),
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
                        text: `newsletters_edit failed. status=${status}\n${bodyText}`,
                    },
                ],
            };
        }
    }
  );

  // Delete newsletter
  server.tool(
    "newsletters_delete",
    deleteParams,
    async (args, _extra) => {
        const config = getGhostApiConfig();
        if (!config) {
            return { isError: true, content: [{ type: "text", text: "Ghost API not configured" }] };
        }
        try {
            const token = generateGhostAdminToken(config.key);
            const url = `${config.url}/ghost/api/admin/newsletters/${args.id}/`;
            const headers = {
                'Authorization': `Ghost ${token}`
            };
            await axios.delete(url, { headers });
            return {
                content: [
                    {
                        type: "text",
                        text: `Newsletter with id ${args.id} deleted.`,
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
                        text: `newsletters_delete failed. status=${status}\n${bodyText}`,
                    },
                ],
            };
        }
    }
  );
}