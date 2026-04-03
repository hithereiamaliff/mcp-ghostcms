import GhostAdminAPI from '@tryghost/admin-api';
import { AsyncLocalStorage } from 'node:async_hooks';
import { GHOST_API_URL, GHOST_ADMIN_API_KEY, GHOST_API_VERSION } from './config.js';
import jwt from 'jsonwebtoken';

// Live binding that tools import. Initialized via env fallback or at runtime via initGhostApi().
export type GhostApiConfig = {
    url: string;
    key: string;
    version: string;
};

let currentConfig: GhostApiConfig | null = null;
let defaultGhostApiClient: any;

type GhostRequestContext = {
    config: GhostApiConfig;
    client: any;
};

// Per-request config store for multi-tenant HTTP mode.
// Tool handlers call getGhostApiConfig()/ghostApiClient which check this first,
// falling back to the module-level singleton for CLI/Smithery modes.
const requestConfigStore = new AsyncLocalStorage<GhostRequestContext>();

/**
 * Run an async function with a scoped GhostApiConfig.
 * All calls to getGhostApiConfig()/ghostApiClient within `fn` will resolve
 * against the request-local context instead of the module-level singleton.
 */
export function runWithGhostConfig<T>(config: GhostApiConfig, fn: () => Promise<T>): Promise<T> {
    const client = makeGhostApi(config);
    return requestConfigStore.run({ config, client }, fn);
}

export function makeGhostApi(config: GhostApiConfig) {
    console.log(`[ghost-mcp] Using Ghost Admin API: url=${config.url}, version=${config.version}, keyId=${config.key.substring(0, 4)}...${config.key.substring(config.key.length - 4)}`);
    return new GhostAdminAPI({
        url: config.url,
        key: config.key,
        version: config.version,
    });
}

export function initGhostApi(config: GhostApiConfig) {
    defaultGhostApiClient = makeGhostApi(config);
    currentConfig = { ...config };
}

export function getGhostApiClient(): any {
    const requestClient = requestConfigStore.getStore()?.client;
    if (requestClient) {
        return requestClient;
    }

    if (defaultGhostApiClient) {
        return defaultGhostApiClient;
    }

    throw new Error('Ghost API client not initialized');
}

// Keep the historic export shape, but resolve the client from AsyncLocalStorage
// when running in multi-tenant HTTP mode.
export const ghostApiClient: any = new Proxy({}, {
    get(_target, prop) {
        const client = getGhostApiClient();
        const value = Reflect.get(client, prop);
        return typeof value === 'function' ? value.bind(client) : value;
    },
});

export function getGhostApiConfig(): GhostApiConfig | null {
    return requestConfigStore.getStore()?.config ?? currentConfig;
}

export function generateGhostAdminToken(apiKey: string): string {
    const [id, secret] = apiKey.split(':');
    const token = jwt.sign({}, Buffer.from(secret, 'hex'), {
        keyid: id,
        algorithm: 'HS256',
        expiresIn: '5m',
        audience: `/admin/`
    });
    return token;
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
