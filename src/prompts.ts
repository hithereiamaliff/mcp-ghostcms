// src/prompts.ts
import { z } from "zod";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { ghostApiClient } from "./ghostApi";

// Example prompt: summarize-post
export function registerPrompts(server: McpServer) {
  server.prompt(
    "summarize-post",
    { postId: z.string() },
    async ({ postId }) => {
      // Fetch the post by ID
      const post = await ghostApiClient.posts.read({ id: postId });
      const title = post.title || "";
      const excerpt = post.excerpt || "";
      const html = post.html || "";

      // Compose a summary message
      const summary = `Title: ${title}\nExcerpt: ${excerpt}\n\nContent Preview:\n${html.slice(0, 300)}...`;

      return {
        messages: [
          {
            role: "user",
            content: {
              type: "text",
              text: `Summarize the following Ghost post:\n\n${summary}`,
            },
          },
        ],
      };
    }
  );
}