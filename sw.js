// FlamesChallenge service worker
// Strategy: NETWORK-FIRST. Always fetch the latest from the network when online,
// so new deploys show up on a normal reload (no cache-clearing needed).
// Falls back to cache only when offline. Only caches the app's own files —
// Supabase API calls and CDN scripts pass straight through.

const CACHE = 'flames-cache-v1';

self.addEventListener('install', () => {
  // Activate this new worker immediately instead of waiting
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return; // never touch POST/PATCH/etc.

  const url = new URL(req.url);
  const sameOrigin = url.origin === self.location.origin;

  event.respondWith(
    fetch(req)
      .then(resp => {
        // Cache a copy of our own files for offline fallback only
        if (sameOrigin) {
          const copy = resp.clone();
          caches.open(CACHE).then(c => c.put(req, copy)).catch(() => {});
        }
        return resp;
      })
      .catch(() => caches.match(req)) // offline → serve last cached copy if we have it
  );
});
