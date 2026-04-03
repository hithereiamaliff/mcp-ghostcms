/**
 * MCP Key Service client for credential resolution.
 *
 * When KEY_SERVICE_URL and KEY_SERVICE_TOKEN are configured, user API keys
 * (usr_XXXXXXXX) are resolved via the external key service which returns
 * the user's Ghost CMS credentials.
 */

export interface ResolvedGhostCredentials {
  ghostUrl: string;
  ghostAdminKey: string;
}

export type ResolveResult =
  | { ok: true; credentials: ResolvedGhostCredentials }
  | { ok: false; reason: 'invalid_key' | 'service_unavailable' | 'malformed_response' };

const KEY_SERVICE_URL = process.env.KEY_SERVICE_URL || '';
const KEY_SERVICE_TOKEN = process.env.KEY_SERVICE_TOKEN || '';
const KEY_SERVICE_SERVER_ID = 'ghost-cms';

const CACHE_TTL_MS = 60_000; // 60 seconds
const CLEANUP_INTERVAL_MS = 5 * 60_000; // 5 minutes
const REQUEST_TIMEOUT_MS = 5_000; // 5 seconds

// Cache: only successful resolutions are cached
interface CacheEntry {
  credentials: ResolvedGhostCredentials;
  expiresAt: number;
}

const cache = new Map<string, CacheEntry>();

// In-flight promise deduplication
const pending = new Map<string, Promise<ResolveResult>>();

// Periodic cache cleanup to prevent unbounded growth
const cleanupInterval = setInterval(() => {
  const now = Date.now();
  for (const [key, entry] of cache) {
    if (now >= entry.expiresAt) {
      cache.delete(key);
    }
  }
}, CLEANUP_INTERVAL_MS);
cleanupInterval.unref?.();

/**
 * Returns true if the key service is configured and should be used.
 */
export function isKeyServiceEnabled(): boolean {
  return Boolean(KEY_SERVICE_URL && KEY_SERVICE_TOKEN);
}

/**
 * Resolve a user API key via the MCP Key Service.
 *
 * Returns typed result so the caller can distinguish between
 * "invalid key" (403) and "service down" (503).
 */
export async function resolveKeyCredentials(apiKey: string): Promise<ResolveResult> {
  // Check cache first
  const cached = cache.get(apiKey);
  if (cached && Date.now() < cached.expiresAt) {
    return { ok: true, credentials: cached.credentials };
  }

  // Deduplicate concurrent requests for the same key
  const inflight = pending.get(apiKey);
  if (inflight) {
    return inflight;
  }

  const promise = doResolve(apiKey);
  pending.set(apiKey, promise);

  try {
    return await promise;
  } finally {
    pending.delete(apiKey);
  }
}

async function doResolve(apiKey: string): Promise<ResolveResult> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
  timeout.unref?.();
  const shortKey = apiKey.substring(0, 12);

  try {
    const res = await fetch(KEY_SERVICE_URL, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${KEY_SERVICE_TOKEN}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ key: apiKey, server_id: KEY_SERVICE_SERVER_ID }),
      signal: controller.signal,
    });

    const contentType = res.headers.get('content-type') || '';
    const isJson = contentType.includes('application/json');

    if (!res.ok) {
      let bodySnippet = '';
      let parsedBody: { valid?: boolean; error?: string; message?: string } | undefined;

      if (isJson) {
        try {
          parsedBody = await res.json() as { valid?: boolean; error?: string; message?: string };
          bodySnippet = JSON.stringify(parsedBody).slice(0, 200);
        } catch {
          bodySnippet = '';
        }
      } else {
        try {
          bodySnippet = (await res.text()).replace(/\s+/g, ' ').trim().slice(0, 200);
        } catch {
          bodySnippet = '';
        }
      }

      const errorMessage = `${parsedBody?.error || ''} ${parsedBody?.message || ''}`.trim();
      const looksLikeInvalidUserKey = /invalid|expired|revoked|suspended/i.test(errorMessage);
      const looksLikeServerAuthIssue = /unauthorized|server_id does not match|authenticated internal caller/i.test(errorMessage);

      if (
        res.status === 401 ||
        res.status === 404 ||
        (res.status === 403 && parsedBody?.valid === false && looksLikeInvalidUserKey && !looksLikeServerAuthIssue)
      ) {
        return { ok: false, reason: 'invalid_key' };
      }

      console.error(
        `Key service returned unexpected ${res.status} (${contentType || 'unknown content-type'}) for key ${shortKey}...` +
        (bodySnippet ? ` Body: ${bodySnippet}` : '')
      );
      return { ok: false, reason: 'service_unavailable' };
    }

    if (!isJson) {
      const bodySnippet = (await res.text()).replace(/\s+/g, ' ').trim().slice(0, 200);
      console.error(
        `Key service returned non-JSON success response (${contentType || 'unknown content-type'}) for key ${shortKey}...` +
        (bodySnippet ? ` Body: ${bodySnippet}` : '')
      );
      return { ok: false, reason: 'malformed_response' };
    }

    const data = await res.json() as {
      valid?: boolean;
      credentials?: Record<string, string>;
    };

    if (data.valid === false) {
      return { ok: false, reason: 'invalid_key' };
    }
    if (data.valid !== true) {
      console.error(`Key service success response missing valid=true for key ${shortKey}...`);
      return { ok: false, reason: 'malformed_response' };
    }

    const creds = data.credentials;
    if (!creds?.ghost_url || !creds?.ghost_admin_key) {
      console.error(`Key service returned incomplete credentials for key ${shortKey}...`);
      return { ok: false, reason: 'malformed_response' };
    }

    const credentials: ResolvedGhostCredentials = {
      ghostUrl: creds.ghost_url,
      ghostAdminKey: creds.ghost_admin_key,
    };

    // Cache successful resolution
    cache.set(apiKey, {
      credentials,
      expiresAt: Date.now() + CACHE_TTL_MS,
    });

    return { ok: true, credentials };
  } catch (error: unknown) {
    if (error instanceof Error && error.name === 'AbortError') {
      console.error(`Key service request timed out for key ${shortKey}...`);
    } else {
      console.error(`Key service request failed for key ${shortKey}...:`, error);
    }
    return { ok: false, reason: 'service_unavailable' };
  } finally {
    clearTimeout(timeout);
  }
}
