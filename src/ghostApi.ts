import GhostAdminAPI from '@tryghost/admin-api';
import { GHOST_API_URL, GHOST_ADMIN_API_KEY, GHOST_API_VERSION } from './config.js';

// Live binding that tools import. Initialized via env fallback or at runtime via initGhostApi().
export let ghostApiClient: any;

export type GhostApiConfig = {
    url: string;
    key: string;
    version: string;
};

let currentConfig: GhostApiConfig | null = null;

export function initGhostApi(config: GhostApiConfig) {
    ghostApiClient = new GhostAdminAPI({
        url: config.url,
        key: config.key,
        version: config.version
    });
    currentConfig = { ...config };
}

// Fallback initialization from environment for local/stdio usage.
if (GHOST_API_URL && GHOST_ADMIN_API_KEY) {
    initGhostApi({ url: GHOST_API_URL, key: GHOST_ADMIN_API_KEY, version: GHOST_API_VERSION });
}

export function getGhostApiConfig(): GhostApiConfig | null {
    return currentConfig;
}

// You can add helper functions here to wrap API calls and handle errors
// For example:
/*
export async function getPostById(postId: string): Promise<any> {
    try {
        const post = await ghostApiClient.posts.read({ id: postId });
        return post;
    } catch (error) {
        console.error(`Error fetching post ${postId}:`, error);
        throw new Error(`Failed to fetch post ${postId}`);
    }
}
*/