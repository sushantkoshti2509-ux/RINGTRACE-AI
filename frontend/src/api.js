// Central API configuration for RINGTRACE AI Frontend
// Provides high-performance in-memory caching and in-flight deduplication
// so repeated queries and tab switches render with 0ms latency.

export const API_BASE =
  typeof window !== 'undefined' && (window.location.port === '5173' || window.location.port === '3000')
    ? `${window.location.protocol}//${window.location.hostname}:8000`
    : '';

const memoryCache = new Map();
const inFlightRequests = new Map();
const CACHE_TTL_MS = 90000; // 90 seconds in-memory cache

export const apiFetch = async (url, options = {}) => {
  const method = (options.method || 'GET').toUpperCase();
  const fullUrl = url.startsWith('http') ? url : `${API_BASE}${url}`;

  // Only GET requests participate in deduplication and caching
  if (method === 'GET' && !options.noCache) {
    const cached = memoryCache.get(fullUrl);
    const now = Date.now();

    if (cached && (now - cached.timestamp < CACHE_TTL_MS)) {
      return {
        ok: true,
        status: 200,
        headers: new Headers(cached.headers || {}),
        json: async () => JSON.parse(JSON.stringify(cached.data)),
        text: async () => JSON.stringify(cached.data),
        clone: () => ({
          json: async () => JSON.parse(JSON.stringify(cached.data)),
        }),
      };
    }

    if (inFlightRequests.has(fullUrl)) {
      return inFlightRequests.get(fullUrl);
    }

    const fetchPromise = (async () => {
      try {
        const res = await fetch(fullUrl, options);
        if (res.ok) {
          const clone = res.clone();
          try {
            const data = await clone.json();
            memoryCache.set(fullUrl, {
              timestamp: Date.now(),
              data,
              headers: Object.fromEntries(res.headers.entries()),
            });
          } catch (_) {
            // Non-JSON response, ignore caching
          }
        }
        return res;
      } finally {
        inFlightRequests.delete(fullUrl);
      }
    })();

    inFlightRequests.set(fullUrl, fetchPromise);
    return fetchPromise;
  }

  // POST/PUT/DELETE/custom requests always bypass cache
  return fetch(fullUrl, options);
};

export default apiFetch;
