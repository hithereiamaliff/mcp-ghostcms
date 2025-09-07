// src/tools/members.ts
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
  email: z.string().optional(),
};
const addParams = {
  email: z.string(),
  name: z.string().optional(),
  note: z.string().optional(),
  labels: z.array(z.object({ name: z.string(), slug: z.string().optional() })).optional(),
  newsletters: z.array(z.object({ id: z.string() })).optional(),
};
const editParams = {
  id: z.string(),
  email: z.string().optional(),
  name: z.string().optional(),
  note: z.string().optional(),
  labels: z.array(z.object({ name: z.string(), slug: z.string().optional() })).optional(),
  newsletters: z.array(z.object({ id: z.string() })).optional(),
};
const deleteParams = {
  id: z.string(),
};

export function registerMemberTools(server: McpServer) {
  // Browse members
  server.tool(
    "members_browse",
    browseParams,
    async (args, _extra) => {
        const config = getGhostApiConfig();
        if (!config) {
            return { isError: true, content: [{ type: "text", text: "Ghost API not configured" }] };
        }
        try {
            const token = generateGhostAdminToken(config.key);
            const url = `${config.url}/ghost/api/admin/members/`;
            const headers = {
                'Authorization': `Ghost ${token}`
            };
            const response = await axios.get(url, { params: args, headers });
            return {
                content: [
                    {
                        type: "text",
                        text: JSON.stringify(response.data.members, null, 2),
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
                        text: `members_browse failed. status=${status}\n${bodyText}`,
                    },
                ],
            };
        }
    }
  );

  // Read member
  server.tool(
    "members_read",
    readParams,
    async (args, _extra) => {
        const config = getGhostApiConfig();
        if (!config) {
            return { isError: true, content: [{ type: "text", text: "Ghost API not configured" }] };
        }
        try {
            const token = generateGhostAdminToken(config.key);
            const url = `${config.url}/ghost/api/admin/members/${args.id || `email/${args.email}`}/`;
            const headers = {
                'Authorization': `Ghost ${token}`
            };
            const response = await axios.get(url, { headers });
            return {
                content: [
                    {
                        type: "text",
                        text: JSON.stringify(response.data.members[0], null, 2),
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
                        text: `members_read failed. status=${status}\n${bodyText}`,
                    },
                ],
            };
        }
    }
  );

  // Add member
  server.tool(
    "members_add",
    addParams,
    async (args, _extra) => {
        const config = getGhostApiConfig();
        if (!config) {
            return { isError: true, content: [{ type: "text", text: "Ghost API not configured" }] };
        }
        try {
            const token = generateGhostAdminToken(config.key);
            const url = `${config.url}/ghost/api/admin/members/`;
            const headers = {
                'Authorization': `Ghost ${token}`
            };
            const response = await axios.post(url, { members: [args] }, { headers });
            return {
                content: [
                    {
                        type: "text",
                        text: JSON.stringify(response.data.members[0], null, 2),
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
                        text: `members_add failed. status=${status}\n${bodyText}`,
                    },
                ],
            };
        }
    }
  );

  // Edit member
  server.tool(
    "members_edit",
    editParams,
    async (args, _extra) => {
        const config = getGhostApiConfig();
        if (!config) {
            return { isError: true, content: [{ type: "text", text: "Ghost API not configured" }] };
        }
        try {
            const token = generateGhostAdminToken(config.key);
            const url = `${config.url}/ghost/api/admin/members/${args.id}/`;
            const headers = {
                'Authorization': `Ghost ${token}`
            };
            const response = await axios.put(url, { members: [args] }, { headers });
            return {
                content: [
                    {
                        type: "text",
                        text: JSON.stringify(response.data.members[0], null, 2),
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
                        text: `members_edit failed. status=${status}\n${bodyText}`,
                    },
                ],
            };
        }
    }
  );

  // Delete member
  server.tool(
    "members_delete",
    deleteParams,
    async (args, _extra) => {
        const config = getGhostApiConfig();
        if (!config) {
            return { isError: true, content: [{ type: "text", text: "Ghost API not configured" }] };
        }
        try {
            const token = generateGhostAdminToken(config.key);
            const url = `${config.url}/ghost/api/admin/members/${args.id}/`;
            const headers = {
                'Authorization': `Ghost ${token}`
            };
            await axios.delete(url, { headers });
            return {
                content: [
                    {
                        type: "text",
                        text: `Member with id ${args.id} deleted.`,
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
                        text: `members_delete failed. status=${status}\n${bodyText}`,
                    },
                ],
            };
        }
    }
  );
}