/**
 * TheSevenRPG — Service Worker
 * 오프라인 에셋 캐싱, 네트워크 우선 전략
 */

const CACHE_NAME = 'theseven-v2';

/** 프리캐시 대상: 앱 셸 (HTML, CSS, JS) */
const PRECACHE_URLS = [
    '/',
    '/index.html',
    '/css/variables.css',
    '/css/common.css',
    '/css/components/login.css',
    '/css/components/top-bar.css',
    '/css/components/left-panel.css',
    '/css/components/tab-stat.css',
    '/css/components/tab-equip.css',
    '/css/components/tab-skill.css',
    '/css/components/tab-collection.css',
    '/css/components/popup.css',
    '/css/components/town-view.css',
    '/css/components/stage-select-view.css',
    '/css/components/battle-view.css',
    '/js/app.js',
    '/js/main.js',
    '/js/popup.js',
    '/js/api.js',
    '/js/store.js',
    '/js/session.js',
    '/js/utils.js',
    '/js/meta-data.js',
    '/js/screens/login.js',
    '/js/main/top-bar.js',
    '/js/main/left-panel.js',
    '/js/main/tabs/stat.js',
    '/js/main/tabs/equip.js',
    '/js/main/tabs/item.js',
    '/js/main/tabs/skill.js',
    '/js/main/tabs/collection.js',
    '/js/main/views/town-view.js',
    '/js/main/views/stage-select-view.js',
    '/js/main/views/battle-view.js',
];

// ── install: 앱 셸 프리캐시 ──
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => cache.addAll(PRECACHE_URLS))
            .then(() => self.skipWaiting())
    );
});

// ── activate: 이전 캐시 삭제 ──
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys()
            .then((keys) => Promise.all(
                keys.filter((key) => key !== CACHE_NAME)
                    .map((key) => caches.delete(key))
            ))
            .then(() => self.clients.claim())
    );
});

// ── fetch: 네트워크 우선, 실패 시 캐시 폴백 ──
self.addEventListener('fetch', (event) => {
    const { request } = event;

    // API 요청은 캐싱하지 않음
    if (request.url.includes('/api')) {
        return;
    }

    event.respondWith(
        fetch(request)
            .then((response) => {
                if (response.ok) {
                    const clone = response.clone();
                    caches.open(CACHE_NAME).then((cache) => cache.put(request, clone));
                }
                return response;
            })
            .catch(() => caches.match(request))
    );
});
