/**
 * TheSevenRPG — Service Worker
 * 오프라인 에셋 캐싱, 네트워크 우선 전략
 */

const CACHE_NAME = 'theseven-v1';

/** 프리캐시 대상: 앱 셸 (HTML, CSS, JS) */
const PRECACHE_URLS = [
    '/',
    '/index.html',
    '/css/variables.css',
    '/css/common.css',
    '/css/components/login.css',
    '/css/components/town.css',
    '/css/components/inventory.css',
    '/css/components/stage-select.css',
    '/css/components/idle-farm.css',
    '/css/components/cards.css',
    '/css/components/battle.css',
    '/js/app.js',
    '/js/api.js',
    '/js/store.js',
    '/js/session.js',
    '/js/utils.js',
    '/js/meta-data.js',
    '/js/screens/login.js',
    '/js/screens/town.js',
    '/js/screens/inventory.js',
    '/js/screens/stage-select.js',
    '/js/screens/battle.js',
    '/js/screens/idle-farm.js',
    '/js/screens/cards.js',
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
                // 성공 응답만 캐시 갱신
                if (response.ok) {
                    const clone = response.clone();
                    caches.open(CACHE_NAME).then((cache) => cache.put(request, clone));
                }
                return response;
            })
            .catch(() => caches.match(request))
    );
});
