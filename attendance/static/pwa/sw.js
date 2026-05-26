/* ======================================================
   SHAMEL PWA — Service Worker
   Offline-first + Background Sync + SQLite-compatible
   ====================================================== */

const VERSION      = 'shamel-v1.0';
const CACHE_SHELL  = `${VERSION}-shell`;
const CACHE_DATA   = `${VERSION}-data`;
const CACHE_PAGES  = `${VERSION}-pages`;
const SYNC_TAG     = 'shamel-sync';

/* ── Pages & assets cached immediately on install ─────── */
const SHELL_ASSETS = [
  '/',
  '/offline/',
  '/static/pwa/manifest.json',
  'https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800;900&display=swap',
  'https://fonts.googleapis.com/icon?family=Material+Icons',
];

/* ── Runtime-cacheable URL patterns ───────────────────── */
const CACHE_PATTERNS = [
  /\/static\//,
  /\/media\//,
  /fonts\.googleapis\.com/,
  /fonts\.gstatic\.com/,
];

/* ── API endpoints — use network-first, fallback queue ── */
const API_PATTERNS = [
  /\/api\//,
  /\/scan\//,
  /\/check-status\//,
  /\/recent-scans\//,
  /\/live-stats\//,
];

/* ── Navigation pages — cache-first fallback ─────────── */
const NAV_PATTERNS = [
  /\/student\/dashboard\//,
  /\/professor-dashboard\//,
  /\/coordinator\/dashboard\//,
  /\/admin-panel\//,
  /\/reports\//,
  /\/schedule\//,
  /\/notifications\//,
];


/* ══════════════════════════════════════════════════════
   INSTALL — Pre-cache the shell
   ══════════════════════════════════════════════════════ */
self.addEventListener('install', event => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_SHELL).then(cache => {
      return Promise.allSettled(
        SHELL_ASSETS.map(url =>
          cache.add(url).catch(err =>
            console.warn('[SW] Shell asset failed:', url, err)
          )
        )
      );
    })
  );
});


/* ══════════════════════════════════════════════════════
   ACTIVATE — Clean old caches
   ══════════════════════════════════════════════════════ */
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys
          .filter(k => k.startsWith('shamel-') && ![CACHE_SHELL, CACHE_DATA, CACHE_PAGES].includes(k))
          .map(k => caches.delete(k))
      )
    ).then(() => self.clients.claim())
  );
});


/* ══════════════════════════════════════════════════════
   FETCH — Strategy router
   ══════════════════════════════════════════════════════ */
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);

  /* Skip non-GET or cross-origin non-static */
  if (request.method !== 'GET') {
    if (request.method === 'POST') {
      event.respondWith(handlePostOffline(request));
    }
    return;
  }

  /* Static assets — cache first */
  if (CACHE_PATTERNS.some(p => p.test(request.url))) {
    event.respondWith(cacheFirst(request, CACHE_DATA));
    return;
  }

  /* API — network first, queue if offline */
  if (API_PATTERNS.some(p => p.test(url.pathname))) {
    event.respondWith(networkFirstApi(request));
    return;
  }

  /* Navigation pages — stale-while-revalidate */
  if (request.mode === 'navigate' || NAV_PATTERNS.some(p => p.test(url.pathname))) {
    event.respondWith(staleWhileRevalidate(request));
    return;
  }

  /* Default — network first */
  event.respondWith(networkFirst(request));
});


/* ══════════════════════════════════════════════════════
   FETCH STRATEGIES
   ══════════════════════════════════════════════════════ */

async function cacheFirst(request, cacheName) {
  const cache = await caches.open(cacheName);
  const cached = await cache.match(request);
  if (cached) return cached;
  try {
    const response = await fetch(request);
    if (response.ok) cache.put(request, response.clone());
    return response;
  } catch {
    return offlineFallback(request);
  }
}

async function networkFirst(request) {
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(CACHE_PAGES);
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    const cached = await caches.match(request);
    return cached || offlineFallback(request);
  }
}

async function networkFirstApi(request) {
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(CACHE_DATA);
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    const cached = await caches.match(request);
    if (cached) return cached;
    return new Response(
      JSON.stringify({ offline: true, error: 'لا يوجد اتصال بالإنترنت' }),
      { status: 503, headers: { 'Content-Type': 'application/json' } }
    );
  }
}

async function staleWhileRevalidate(request) {
  const cache = await caches.open(CACHE_PAGES);
  const cached = await cache.match(request);

  const networkPromise = fetch(request)
    .then(response => {
      if (response.ok) cache.put(request, response.clone());
      return response;
    })
    .catch(() => null);

  return cached || await networkPromise || offlineFallback(request);
}

async function offlineFallback(request) {
  if (request.mode === 'navigate') {
    return caches.match('/offline/');
  }
  return new Response('Offline', { status: 503 });
}


/* ══════════════════════════════════════════════════════
   POST OFFLINE QUEUE  (Background Sync)
   ══════════════════════════════════════════════════════ */
const QUEUE_STORE = 'shamel-sync-queue';

async function handlePostOffline(request) {
  try {
    const response = await fetch(request.clone());
    return response;
  } catch {
    /* Store request in IndexedDB queue */
    await enqueueRequest(request);
    /* Register background sync if supported */
    if ('serviceWorker' in self && 'SyncManager' in self) {
      await self.registration.sync.register(SYNC_TAG);
    }
    return new Response(
      JSON.stringify({ queued: true, message: 'تم حفظ الطلب وسيُرسل عند عودة الاتصال' }),
      { status: 202, headers: { 'Content-Type': 'application/json' } }
    );
  }
}

async function enqueueRequest(request) {
  const body = await request.text().catch(() => '');
  const entry = {
    id: Date.now() + Math.random(),
    url: request.url,
    method: request.method,
    headers: Object.fromEntries(request.headers.entries()),
    body,
    timestamp: new Date().toISOString(),
  };

  const db = await openSyncDB();
  const tx = db.transaction(QUEUE_STORE, 'readwrite');
  tx.objectStore(QUEUE_STORE).add(entry);
  await tx.complete;
}

async function flushQueue() {
  const db = await openSyncDB();
  const tx = db.transaction(QUEUE_STORE, 'readwrite');
  const store = tx.objectStore(QUEUE_STORE);
  const all = await storeGetAll(store);

  for (const entry of all) {
    try {
      await fetch(entry.url, {
        method: entry.method,
        headers: entry.headers,
        body: entry.body || undefined,
      });
      store.delete(entry.id);
      console.log('[SW Sync] Flushed:', entry.url);
    } catch (err) {
      console.warn('[SW Sync] Still offline for:', entry.url);
    }
  }
}


/* ══════════════════════════════════════════════════════
   BACKGROUND SYNC
   ══════════════════════════════════════════════════════ */
self.addEventListener('sync', event => {
  if (event.tag === SYNC_TAG) {
    event.waitUntil(flushQueue());
  }
});

/* Periodic sync (if browser supports it) */
self.addEventListener('periodicsync', event => {
  if (event.tag === 'shamel-periodic') {
    event.waitUntil(flushQueue());
  }
});


/* ══════════════════════════════════════════════════════
   PUSH NOTIFICATIONS
   ══════════════════════════════════════════════════════ */
self.addEventListener('push', event => {
  if (!event.data) return;
  const data = event.data.json();
  event.waitUntil(
    self.registration.showNotification(data.title || 'SHAMEL', {
      body: data.body || '',
      icon: '/static/pwa/icons/icon-192.png',
      badge: '/static/pwa/icons/icon-96.png',
      dir: 'rtl',
      lang: 'ar',
      vibrate: [200, 100, 200],
      data: { url: data.url || '/' },
      actions: [
        { action: 'open',    title: 'فتح' },
        { action: 'dismiss', title: 'إغلاق' },
      ],
    })
  );
});

self.addEventListener('notificationclick', event => {
  event.notification.close();
  if (event.action === 'dismiss') return;
  const url = event.notification.data?.url || '/';
  event.waitUntil(
    clients.matchAll({ type: 'window' }).then(cs => {
      const existing = cs.find(c => c.url.includes(url));
      if (existing) return existing.focus();
      return clients.openWindow(url);
    })
  );
});


/* ══════════════════════════════════════════════════════
   MESSAGE — from client
   ══════════════════════════════════════════════════════ */
self.addEventListener('message', event => {
  if (event.data?.type === 'SKIP_WAITING') self.skipWaiting();
  if (event.data?.type === 'SYNC_NOW') flushQueue();
  if (event.data?.type === 'GET_VERSION') {
    event.source?.postMessage({ type: 'VERSION', version: VERSION });
  }
});


/* ══════════════════════════════════════════════════════
   IndexedDB helpers
   ══════════════════════════════════════════════════════ */
function openSyncDB() {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open('shamel-sync-db', 1);
    req.onupgradeneeded = e => {
      const db = e.target.result;
      if (!db.objectStoreNames.contains(QUEUE_STORE)) {
        db.createObjectStore(QUEUE_STORE, { keyPath: 'id' });
      }
    };
    req.onsuccess = e => resolve(e.target.result);
    req.onerror = e => reject(e.target.error);
  });
}

function storeGetAll(store) {
  return new Promise((resolve, reject) => {
    const req = store.getAll();
    req.onsuccess = e => resolve(e.target.result);
    req.onerror = e => reject(e.target.error);
  });
}
