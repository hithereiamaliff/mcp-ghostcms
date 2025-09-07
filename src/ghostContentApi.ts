import GhostContentAPI from '@tryghost/content-api';
import { GHOST_API_URL, GHOST_ADMIN_API_KEY, GHOST_API_VERSION } from './config.js';

// Live binding that tools import.
export let ghostContentApiClient: any;

export type GhostContentApiConfig = {
    url: string;
    key: string;
    version: string;
};

let currentContentConfig: GhostContentApiConfig | null = null;

export function initGhostContentApi(config: GhostContentApiConfig) {
    ghostContentApiClient = new (GhostContentAPI as any)({
        url: config.url,
        key: config.key,
        version: config.version
    });
    currentContentConfig = { ...config };
}

// Fallback initialization from environment for local/stdio usage.
if (GHOST_API_URL && GHOST_ADMIN_API_KEY) {
    initGhostContentApi({ url: GHOST_API_URL, key: GHOST_ADMIN_API_KEY, version: GHOST_API_VERSION });
}

export function getGhostContentApiConfig(): GhostContentApiConfig | null {
    return currentContentConfig;
}