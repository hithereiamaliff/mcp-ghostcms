import { z } from 'zod';

// Define the configuration schema using Zod
export const configSchema = z.object({
  GHOST_API_URL: z.string().describe('Ghost API URL'),
  GHOST_ADMIN_API_KEY: z.string().describe('Ghost Admin API Key'),
  GHOST_CONTENT_API_KEY: z.string().describe('Ghost Content API Key'),
  GHOST_API_VERSION: z.string().default('v6.0').describe('Ghost API Version'),
  port: z.number().default(8080).describe('HTTP server port'),
});

// Export the inferred type
export type ConfigType = z.infer<typeof configSchema>;
