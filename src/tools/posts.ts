// src/tools/posts.ts
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
  slug: z.string().optional(),
};
const addParams = {
  title: z.string(),
  html: z.string().optional(),
  lexical: z.string().optional(),
  status: z.string().optional(),
};
const editParams = {
  id: z.string(),
  title: z.string().optional(),
  html: z.string().optional(),
  lexical: z.string().optional(),
  status: z.string().optional(),
  updated_at: z.string(),
};
const deleteParams = {
  id: z.string(),
};

export function registerPostTools(server: McpServer) {
  // Browse posts
  server.tool(
    "posts_browse",
    browseParams,
    async (args, _extra) => {
      try {
        const posts = await ghostContentApiClient.posts.browse({ include: 'authors', ...args });
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(posts, null, 2),
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
              text: `posts_browse failed. status=${status}\n${bodyText}`,
            },
          ],
        };
      }
    }
  );

  // Read post
  server.tool(
    "posts_read",
    readParams,
    async (args, _extra) => {
      try {
        const post = await ghostApiClient.posts.read(args);
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(post, null, 2),
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
              text: `posts_read failed. status=${status}\n${bodyText}`,
            },
          ],
        };
      }
    }
  );

  // Add post
  server.tool(
    "posts_add",
    addParams,
    async (args, _extra) => {
      try {
        // If html is present, use source: "html" to ensure Ghost uses the html content
        const options = args.html ? { source: "html" } : undefined;
        const post = await ghostApiClient.posts.add(args, options);
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(post, null, 2),
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
              text: `posts_add failed. status=${status}\n${bodyText}`,
            },
          ],
        };
      }
    }
  );

  // Edit post
  server.tool(
    "posts_edit",
    editParams,
    async (args, _extra) => {
      try {
        // If html is present, use source: "html" to ensure Ghost uses the html content for updates
        const options = args.html ? { source: "html" } : undefined;
        const post = await ghostApiClient.posts.edit(args, options);
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(post, null, 2),
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
              text: `posts_edit failed. status=${status}\n${bodyText}`,
            },
          ],
        };
      }
    }
  );

  // Delete post
  server.tool(
    "posts_delete",
    deleteParams,
    async (args, _extra) => {
      try {
        await ghostApiClient.posts.delete(args);
        return {
          content: [
            {
              type: "text",
              text: `Post with id ${args.id} deleted.`,
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
              text: `posts_delete failed. status=${status}\n${bodyText}`,
            },
          ],
        };
      }
    }
  );
}