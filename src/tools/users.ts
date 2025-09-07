// src/tools/users.ts
import { z } from "zod";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { ghostContentApiClient } from "../ghostContentApi.js";
import { ghostApiClient } from "../ghostApi.js";

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
  slug: z.string().optional(),
};
const editParams = {
  id: z.string(),
  name: z.string().optional(),
  email: z.string().optional(),
  slug: z.string().optional(),
  bio: z.string().optional(),
  website: z.string().optional(),
  location: z.string().optional(),
  facebook: z.string().optional(),
  twitter: z.string().optional(),
  // Add more fields as needed
};
const deleteParams = {
  id: z.string(),
};

export function registerUserTools(server: McpServer) {
  // Browse users
  server.tool(
    "users_browse",
    browseParams,
    async (args, _extra) => {
      try {
        const users = await ghostContentApiClient.authors.browse(args);
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(users, null, 2),
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
              text: `users_browse failed. status=${status}\n${bodyText}`,
            },
          ],
        };
      }
    }
  );

  // Read user
  server.tool(
    "users_read",
    readParams,
    async (args, _extra) => {
      const user = await ghostApiClient.users.read(args);
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(user, null, 2),
          },
        ],
      };
    }
  );

  // Edit user
  server.tool(
    "users_edit",
    editParams,
    async (args, _extra) => {
      const user = await ghostApiClient.users.edit(args);
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(user, null, 2),
          },
        ],
      };
    }
  );

  // Delete user
  server.tool(
    "users_delete",
    deleteParams,
    async (args, _extra) => {
      await ghostApiClient.users.delete(args);
      return {
        content: [
          {
            type: "text",
            text: `User with id ${args.id} deleted.`,
          },
        ],
      };
    }
  );
}