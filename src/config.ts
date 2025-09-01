// Read configuration values directly from process.env
export const GHOST_API_URL: string = process.env.GHOST_API_URL as string;
export const GHOST_ADMIN_API_KEY: string = process.env.GHOST_ADMIN_API_KEY as string;
export const GHOST_API_VERSION: string = (process.env.GHOST_API_VERSION as string) || 'v6.0'; // Default to v6.0

// Note: When running under Smithery, configuration is provided via the runtime
// config object (see src/server.ts) rather than environment variables. Avoid
// exiting the process here so the server can inject config at startup.
if (!GHOST_API_URL) {
    console.warn("Warning: GHOST_API_URL is not set via environment; expecting Smithery config.");
}

if (!GHOST_ADMIN_API_KEY) {
    console.warn("Warning: GHOST_ADMIN_API_KEY is not set via environment; expecting Smithery config.");
}