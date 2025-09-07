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

export function makeGhostApi(config: GhostApiConfig) {
    console.log(`[ghost-mcp] Using Ghost Admin API: url=${config.url}, version=${config.version}, keyId=${config.key.substring(0, 4)}...${config.key.substring(config.key.length - 4)}`);
    return new GhostAdminAPI({
        url: config.url,
        key: config.key,
        version: config.version,
    });
}

export function initGhostApi(config: GhostApiConfig) {
    ghostApiClient = makeGhostApi(config);
    currentConfig = { ...config };
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