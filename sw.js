// FlamesChallenge service worker — controlled shell cache + web push (v1099)

const FC_CACHE_PREFIX = 'fc-shell-';
const FC_CACHE_NAME = 'fc-shell-v1099';
const FC_LEGACY_CACHES = new Set(['fc-v1']);
const FC_NETWORK_TIMEOUT_MS = 8000;

function withNetworkTimeout(request) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), FC_NETWORK_TIMEOUT_MS);
  return fetch(request, { signal: controller.signal })
    .finally(() => clearTimeout(timer));
}

function isApprovedShellRequest(request) {
  if (request.method !== 'GET') return false;
  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return false;
  if (!/^https?:$/.test(url.protocol)) return false;

  if (request.mode === 'navigate') return true;

  return new Set([
    'document',
    'script',
    'style',
    'manifest',
    'font',
    'image'
  ]).has(request.destination);
}

function cacheKeyFor(request) {
  if (request.mode === 'navigate') {
    return new Request(
      new URL('/index.html', self.location.origin).href,
      { method: 'GET' }
    );
  }
  return request;
}

async function networkFirst(request, finishLifecycle) {
  const cacheKey = cacheKeyFor(request);
  let cache;

  try {
    cache = await caches.open(FC_CACHE_NAME);
    const response = await withNetworkTimeout(request);

    if (response && response.ok && response.type === 'basic') {
      cache.put(cacheKey, response.clone())
        .catch(() => {})
        .finally(finishLifecycle);
    } else {
      finishLifecycle();
    }

    return response;
  } catch (error) {
    try {
      cache = cache || await caches.open(FC_CACHE_NAME);
      const cached = await cache.match(cacheKey);
      finishLifecycle();
      if (cached) return cached;
    } catch (cacheError) {
      finishLifecycle();
    }

    throw error;
  }
}

self.addEventListener('install', () => {
  // Do not force activation over an open page. The app explicitly activates a
  // waiting worker after the user accepts an available update.
});

self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

self.addEventListener('activate', (event) => {
  event.waitUntil((async () => {
    const keys = await caches.keys();

    await Promise.all(
      keys
        .filter(
          key =>
            (
              FC_LEGACY_CACHES.has(key) ||
              key.startsWith(FC_CACHE_PREFIX)
            ) &&
            key !== FC_CACHE_NAME
        )
        .map(key => caches.delete(key))
    );

    await self.clients.claim();
  })());
});

self.addEventListener('fetch', (event) => {
  if (!isApprovedShellRequest(event.request)) return;

  let finished = false;
  let resolveLifecycle;

  const lifecycle = new Promise(resolve => {
    resolveLifecycle = resolve;
  });

  const finishLifecycle = () => {
    if (finished) return;
    finished = true;
    resolveLifecycle();
  };

  // Register the cache-write lifetime synchronously. The response can return as
  // soon as the network succeeds while Safari keeps the worker alive to finish
  // the approved shell-cache write.
  event.waitUntil(lifecycle);
  event.respondWith(
    networkFirst(event.request, finishLifecycle)
  );
});

// Web Push
self.addEventListener('push', (event) => {
  let data = {};

  try {
    data = event.data ? event.data.json() : {};
  } catch (e) {}

  const title = data.title || 'FlamesChallenge';

  const options = {
    body: data.body || '',
    data: {
      url: data.url || '/'
    },
    tag: data.tag || undefined,
  };

  event.waitUntil(
    self.registration.showNotification(title, options)
  );
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();

  const requested =
    (event.notification.data && event.notification.data.url) ||
    '/';

  const target = new URL(
    requested,
    self.location.origin
  );

  const safeTarget =
    target.origin === self.location.origin
      ? target.href
      : self.location.origin + '/';

  event.waitUntil((async () => {
    const list = await clients.matchAll({
      type: 'window',
      includeUncontrolled: true
    });

    for (const client of list) {
      if ('navigate' in client) {
        try {
          await client.navigate(safeTarget);
        } catch (e) {}
      }

      if ('focus' in client) {
        await client.focus();
        return;
      }
    }

    if (clients.openWindow) {
      await clients.openWindow(safeTarget);
    }
  })());
});
