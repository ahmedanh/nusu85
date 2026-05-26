/* ======================================================
   SHAMEL PWA — Client Init
   • Service Worker registration
   • Install prompt (A2HS)
   • Offline status banner
   • SQLite-compatible sync queue
   • Update notification
   ====================================================== */

(function () {
  'use strict';

  /* ── Register Service Worker ─────────────────────────── */
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js', { scope: '/' })
      .then(reg => {
        console.log('[PWA] SW registered, scope:', reg.scope);

        /* Listen for SW updates */
        reg.addEventListener('updatefound', () => {
          const newSW = reg.installing;
          newSW.addEventListener('statechange', () => {
            if (newSW.state === 'installed' && navigator.serviceWorker.controller) {
              showUpdateBanner(newSW);
            }
          });
        });

        /* Register periodic sync if available */
        if ('periodicSync' in reg) {
          reg.periodicSync.register('shamel-periodic', {
            minInterval: 60 * 60 * 1000 /* 1 hour */
          }).catch(() => {/* permission denied or unsupported */});
        }
      })
      .catch(err => console.warn('[PWA] SW registration failed:', err));

    /* Reload when new SW takes control */
    let refreshing = false;
    navigator.serviceWorker.addEventListener('controllerchange', () => {
      if (!refreshing) { refreshing = true; window.location.reload(); }
    });
  }


  /* ── Offline / Online banner ─────────────────────────── */
  const offlineBanner = createBanner();
  document.addEventListener('DOMContentLoaded', () => {
    document.body.appendChild(offlineBanner);
    updateOnlineState();
  });

  window.addEventListener('online',  updateOnlineState);
  window.addEventListener('offline', updateOnlineState);

  function updateOnlineState() {
    if (navigator.onLine) {
      offlineBanner.classList.remove('show');
      updateCornerIndicator(true);
      if (navigator.serviceWorker?.controller) {
        navigator.serviceWorker.controller.postMessage({ type: 'SYNC_NOW' });
      }
      syncFromIndexedDB();
    } else {
      offlineBanner.classList.add('show');
      updateCornerIndicator(false);
    }
  }

  /* ── Corner online/offline indicator (all pages, all roles) ── */
  function createCornerIndicator() {
    const wrap = document.createElement('div');
    wrap.id = 'shamel-net-indicator';
    wrap.title = 'حالة الاتصال';
    wrap.innerHTML = `
      <span id="shamel-net-dot"></span>
      <span id="shamel-net-label"></span>
    `;
    const style = document.createElement('style');
    style.textContent = `
      #shamel-net-indicator {
        position: fixed;
        bottom: 1.25rem;
        left: 1.25rem;
        z-index: 9990;
        display: flex;
        align-items: center;
        gap: .45rem;
        background: rgba(15,23,42,.85);
        backdrop-filter: blur(6px);
        border: 1px solid rgba(255,255,255,.1);
        border-radius: 99px;
        padding: .35rem .75rem .35rem .5rem;
        font-family: 'Tajawal', sans-serif;
        font-size: .75rem;
        font-weight: 700;
        color: #e2e8f0;
        direction: rtl;
        transition: opacity .3s;
        cursor: default;
        user-select: none;
      }
      #shamel-net-indicator:hover { opacity: 1 !important; }
      #shamel-net-dot {
        width: 9px; height: 9px;
        border-radius: 50%;
        flex-shrink: 0;
        transition: background .3s;
      }
      #shamel-net-dot.online  { background: #22c55e; box-shadow: 0 0 6px #22c55e; }
      #shamel-net-dot.offline { background: #ef4444; box-shadow: 0 0 6px #ef4444; animation: blink-red .9s infinite; }
      #shamel-net-dot.checking{ background: #f59e0b; box-shadow: 0 0 6px #f59e0b; animation: blink-red .6s infinite; }
      @keyframes blink-red { 50% { opacity: .3; } }
    `;
    document.head.appendChild(style);
    document.body.appendChild(wrap);
    return wrap;
  }

  const _cornerWrap = createCornerIndicator();

  function updateCornerIndicator(online) {
    const dot   = document.getElementById('shamel-net-dot');
    const label = document.getElementById('shamel-net-label');
    if (!dot) return;
    if (online) {
      dot.className   = 'online';
      label.textContent = 'متصل';
      _cornerWrap.style.opacity = '.55';
      setTimeout(() => { _cornerWrap.style.opacity = '.35'; }, 3000);
    } else {
      dot.className   = 'offline';
      label.textContent = 'غير متصل';
      _cornerWrap.style.opacity = '1';
    }
  }

  /* ── Intercept SW queued responses → show toast instead of raw JSON ── */
  (function interceptQueuedResponses() {
    const _origFetch = window.fetch;
    window.fetch = async function(...args) {
      const res = await _origFetch(...args);
      if (res.status === 202) {
        try {
          const clone = res.clone();
          const data  = await clone.json();
          if (data.queued) {
            showQueuedToast(data.message || 'تم حفظ الطلب وسيُرسل عند عودة الاتصال');
          }
        } catch {}
      }
      return res;
    };
  })();

  function showQueuedToast(msg) {
    const t = document.createElement('div');
    t.className = 'shamel-queued-toast';
    t.innerHTML = `<span style="font-size:1.1rem">📥</span><span>${msg}</span>`;
    const style = document.getElementById('shamel-toast-style');
    if (!style) {
      const s = document.createElement('style');
      s.id = 'shamel-toast-style';
      s.textContent = `
        .shamel-queued-toast {
          position:fixed; bottom:5rem; left:50%; transform:translateX(-50%);
          z-index:99999; background:#1e3a5f; color:#e2e8f0;
          border:1px solid #c9a84c; border-radius:.875rem;
          padding:.7rem 1.25rem; display:flex; align-items:center; gap:.6rem;
          font-family:'Tajawal',sans-serif; font-size:.9rem; font-weight:700;
          direction:rtl; box-shadow:0 8px 24px rgba(0,0,0,.4);
          animation: fadeUp .3s ease;
        }
        @keyframes fadeUp { from{opacity:0;transform:translate(-50%,10px)} to{opacity:1;transform:translate(-50%,0)} }
      `;
      document.head.appendChild(s);
    }
    document.body.appendChild(t);
    setTimeout(() => t.remove(), 4000);
  }

  function createBanner() {
    const el = document.createElement('div');
    el.id = 'shamel-offline-banner';
    el.innerHTML = `
      <span style="font-size:1.1rem">📡</span>
      <span>وضع عدم الاتصال — سيتم مزامنة بياناتك تلقائياً</span>
      <span id="shamel-queue-badge" style="
        background:#ef4444;color:white;border-radius:99px;
        font-size:.7rem;font-weight:700;padding:.1rem .5rem;
        display:none;margin-right:.5rem;
      "></span>
    `;
    const style = document.createElement('style');
    style.textContent = `
      #shamel-offline-banner {
        position: fixed; bottom: 0; left: 0; right: 0; z-index: 9999;
        background: #1e3a5f; color: #e2e8f0;
        display: flex; align-items: center; justify-content: center; gap: .75rem;
        padding: .75rem 1.5rem;
        font-family: 'Tajawal', sans-serif; font-size: .9rem; font-weight: 600;
        transform: translateY(100%); transition: transform .3s ease;
        border-top: 2px solid #c9a84c;
        direction: rtl;
      }
      #shamel-offline-banner.show { transform: translateY(0); }
    `;
    document.head.appendChild(style);
    return el;
  }


  /* ── Install prompt (Add to Home Screen) ─────────────── */
  let deferredPrompt = null;
  let installBtn     = null;

  window.addEventListener('beforeinstallprompt', event => {
    event.preventDefault();
    deferredPrompt = event;
    showInstallButton();
  });

  window.addEventListener('appinstalled', () => {
    deferredPrompt = null;
    if (installBtn) installBtn.remove();
    console.log('[PWA] App installed!');
  });

  function showInstallButton() {
    if (installBtn) return; /* already shown */

    installBtn = document.createElement('button');
    installBtn.id = 'shamel-install-btn';
    installBtn.innerHTML = `
      <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
        <path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/>
      </svg>
      تثبيت التطبيق
    `;

    const style = document.createElement('style');
    style.textContent = `
      #shamel-install-btn {
        position: fixed; top: 1rem; left: 1rem; z-index: 9998;
        background: #c9a84c; color: #0f172a;
        border: none; border-radius: .75rem;
        padding: .6rem 1rem; cursor: pointer;
        font-family: 'Tajawal', sans-serif;
        font-weight: 700; font-size: .85rem;
        display: flex; align-items: center; gap: .5rem;
        box-shadow: 0 4px 12px rgba(0,0,0,.3);
        direction: rtl;
        animation: bounce-in .4s ease;
      }
      #shamel-install-btn:hover { opacity: .9; transform: scale(1.03); }
      @keyframes bounce-in {
        0%   { transform: scale(.8); opacity: 0; }
        100% { transform: scale(1);  opacity: 1; }
      }
    `;
    document.head.appendChild(style);

    installBtn.addEventListener('click', async () => {
      if (!deferredPrompt) return;
      deferredPrompt.prompt();
      const { outcome } = await deferredPrompt.userChoice;
      deferredPrompt = null;
      if (outcome === 'accepted') installBtn.remove();
    });

    document.body.appendChild(installBtn);
  }


  /* ── Update banner ───────────────────────────────────── */
  function showUpdateBanner(newSW) {
    const banner = document.createElement('div');
    banner.innerHTML = `
      <span>🔄 تحديث جديد متاح لـ SHAMEL</span>
      <button onclick="this.closest('#shamel-update-banner').querySelector('button').disabled=true;
                       window.__shamelSW?.postMessage({type:'SKIP_WAITING'})">
        تحديث الآن
      </button>
    `;
    banner.id = 'shamel-update-banner';
    const style = document.createElement('style');
    style.textContent = `
      #shamel-update-banner {
        position: fixed; top: 0; left: 0; right: 0; z-index: 9999;
        background: #1e3a5f; color: white; border-bottom: 2px solid #c9a84c;
        padding: .6rem 1rem; display: flex; align-items: center;
        justify-content: center; gap: 1rem;
        font-family: 'Tajawal',sans-serif; font-size: .9rem; font-weight: 600;
        direction: rtl;
      }
      #shamel-update-banner button {
        background: #c9a84c; color: #0f172a; border: none;
        border-radius: .5rem; padding: .3rem .8rem;
        cursor: pointer; font-weight: 700;
        font-family: 'Tajawal',sans-serif;
      }
    `;
    document.head.appendChild(style);
    document.body.prepend(banner);
    window.__shamelSW = newSW;
  }


  /* ── IndexedDB Sync Queue ────────────────────────────── */
  const DB_NAME    = 'shamel-sync-db';
  const STORE_NAME = 'shamel-sync-queue';

  function openDB() {
    return new Promise((res, rej) => {
      const req = indexedDB.open(DB_NAME, 1);
      req.onupgradeneeded = e => {
        const db = e.target.result;
        if (!db.objectStoreNames.contains(STORE_NAME)) {
          db.createObjectStore(STORE_NAME, { keyPath: 'id' });
        }
      };
      req.onsuccess = e => res(e.target.result);
      req.onerror   = e => rej(e.target.error);
    });
  }

  async function syncFromIndexedDB() {
    if (!navigator.onLine) return;
    try {
      const db    = await openDB();
      const tx    = db.transaction(STORE_NAME, 'readwrite');
      const store = tx.objectStore(STORE_NAME);
      const items = await new Promise((res, rej) => {
        const r = store.getAll();
        r.onsuccess = e => res(e.target.result);
        r.onerror   = e => rej(e.target.error);
      });

      for (const item of items) {
        try {
          await fetch(item.url, {
            method: item.method,
            headers: item.headers,
            body: item.body || undefined,
          });
          store.delete(item.id);
        } catch { /* still offline */ }
      }

      /* Update badge */
      const remaining = await new Promise(res => {
        const r = store.count();
        r.onsuccess = e => res(e.target.result);
        r.onerror   = ()=> res(0);
      });

      updateQueueBadge(remaining);
    } catch (e) {
      console.warn('[PWA] Sync error:', e);
    }
  }

  function updateQueueBadge(count) {
    const badge = document.getElementById('shamel-queue-badge');
    if (!badge) return;
    if (count > 0) {
      badge.style.display = 'inline';
      badge.textContent   = `${count} معلق`;
    } else {
      badge.style.display = 'none';
    }
  }

  /* Expose sync helper globally */
  window.shamelSync = syncFromIndexedDB;


  /* ── Live Reload via WebSocket ───────────────────────── */
  (function initLiveReload() {
    if (!('WebSocket' in window)) return;

    const proto = location.protocol === 'https:' ? 'wss' : 'ws';
    const wsUrl = `${proto}://${location.host}/ws/live-reload/`;
    let ws, retryDelay = 2000, retryTimer;

    function connect() {
      try { ws = new WebSocket(wsUrl); } catch { return; }

      ws.onopen = () => {
        retryDelay = 2000; /* reset backoff on success */
        console.log('[PWA] Live-reload WS connected');
      };

      ws.onmessage = e => {
        try {
          const msg = JSON.parse(e.data);
          if (msg.type === 'reload') {
            console.log('[PWA] Server pushed update v' + msg.version + ' — reloading…');
            showReloadToast(msg.version);
          }
        } catch {}
      };

      ws.onclose = () => {
        /* Reconnect with exponential backoff (max 30s) */
        clearTimeout(retryTimer);
        retryTimer = setTimeout(() => {
          retryDelay = Math.min(retryDelay * 1.5, 30000);
          connect();
        }, retryDelay);
      };

      ws.onerror = () => ws.close();
    }

    function showReloadToast(version) {
      /* Remove any existing toast */
      document.getElementById('shamel-reload-toast')?.remove();

      const toast = document.createElement('div');
      toast.id = 'shamel-reload-toast';
      toast.innerHTML = `
        <span style="font-size:1.1rem">🚀</span>
        <span>تحديث جديد جاهز</span>
        <button onclick="location.reload(true)" style="
          background:#c9a84c;color:#0f172a;border:none;border-radius:.5rem;
          padding:.3rem .8rem;cursor:pointer;font-weight:700;
          font-family:'Tajawal',sans-serif;font-size:.85rem;white-space:nowrap;
        ">تحديث الآن</button>
        <button onclick="this.closest('#shamel-reload-toast').remove()" style="
          background:transparent;border:none;color:#94a3b8;
          cursor:pointer;font-size:1.1rem;padding:0 .2rem;
        ">✕</button>
      `;
      Object.assign(toast.style, {
        position: 'fixed', top: '1rem', right: '1rem', zIndex: '99999',
        background: '#1e3a5f', color: '#e2e8f0',
        border: '1px solid #c9a84c', borderRadius: '.875rem',
        padding: '.75rem 1rem', display: 'flex',
        alignItems: 'center', gap: '.75rem',
        fontFamily: "'Tajawal',sans-serif", fontSize: '.9rem', fontWeight: '600',
        direction: 'rtl', boxShadow: '0 8px 24px rgba(0,0,0,.4)',
        animation: 'slideIn .3s ease',
      });

      const styleEl = document.createElement('style');
      styleEl.textContent = `@keyframes slideIn{from{transform:translateX(110%)}to{transform:translateX(0)}}`;
      document.head.appendChild(styleEl);
      document.body.appendChild(toast);

      /* Auto-reload after 8 seconds if user doesn't dismiss */
      setTimeout(() => {
        if (document.getElementById('shamel-reload-toast')) {
          location.reload(true);
        }
      }, 8000);
    }

    /* Start connection after page load */
    document.addEventListener('DOMContentLoaded', connect);
  })();

})();
