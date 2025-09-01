// src/tools/debug.ts
import axios from "axios";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { getGhostApiConfig } from "../ghostApi.js";

export function registerDebugTools(server: McpServer) {
  // Ping Admin API path without auth to check routing (expects 401 if path exists)
  server.tool(
    "admin_site_ping",
    {},
    async () => {
      const cfg = getGhostApiConfig();
      const baseUrl = cfg?.url || "";
      const url = `${baseUrl.replace(/\/$/, "")}/ghost/api/admin/site/`;
      try {
        const res = await axios.get(url, { validateStatus: () => true });
        return {
          content: [
            { type: "text", text: `GET ${url}\nstatus=${res.status} statusText=${res.statusText}\nbody=${JSON.stringify(res.data, null, 2)}` },
          ],
        };
      } catch (error: any) {
        const status = error?.response?.status ?? "unknown";
        const body = error?.response?.data ?? error?.message ?? String(error);
        const bodyText = typeof body === "string" ? body : JSON.stringify(body, null, 2);
        return { isError: true, content: [{ type: "text", text: `admin_site_ping failed. status=${status}\n${bodyText}` }] };
      }
    }
  );

  // Echo current Ghost config used at runtime (mask secret)
  server.tool(
    "config_echo",
    {},
    async () => {
      const cfg = getGhostApiConfig();
      if (!cfg) {
        return { isError: true, content: [{ type: "text", text: "No Ghost config initialized" }] };
      }
      const keyId = cfg.key?.split(":")[0] || "unknown";
      return {
        content: [
          { type: "text", text: JSON.stringify({ url: cfg.url, version: cfg.version, keyId }, null, 2) },
        ],
      };
    }
  );
}
