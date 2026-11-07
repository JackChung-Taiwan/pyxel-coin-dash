/* Cache the PWA shell. Pyxel's WebAssembly runtime is provided by kitao.dev,
   so this example intentionally does not promise offline gameplay. */
const CACHE = 'coin-dash-scroll-v2';
const SHELL = [
  './', './index.html', './game.py', './manifest.webmanifest',
  './icons/icon-192.png', './icons/icon-512.png', './icons/icon-maskable-512.png'
];

self.addEventListener('install', (event) => {
  event.waitUntil(caches.open(CACHE).then((cache) => cache.addAll(SHELL)));
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(Promise.all([
    caches.keys().then((keys) => Promise.all(keys.filter((key) => key !== CACHE).map((key) => caches.delete(key)))),
    self.clients.claim()
  ]));
});

self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;
  const url = new URL(event.request.url);
  if (url.origin !== self.location.origin) return;
  const changingFile = event.request.mode === 'navigate' ||
    url.pathname.endsWith('/game.py') || url.pathname.endsWith('/manifest.webmanifest');
  if (changingFile) {
    event.respondWith(
      fetch(event.request).then((response) => {
        if (response.ok) {
          const copy = response.clone();
          caches.open(CACHE).then((cache) => cache.put(event.request, copy));
        }
        return response;
      }).catch(async () => (await caches.match(event.request)) ||
        (event.request.mode === 'navigate' ? caches.match('./index.html') : Response.error()))
    );
    return;
  }
  event.respondWith(caches.match(event.request).then((cached) => cached || fetch(event.request)));
});
