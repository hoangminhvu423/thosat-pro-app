/* Service worker ThợSắt Pro — offline-first.
   Chiến lược: cache sẵn vỏ app; mọi request cùng nguồn dùng
   "cache trước, mạng sau cập nhật" (stale-while-revalidate) để
   thợ ngoài công trường không mạng vẫn tính được, có mạng thì tự cập nhật. */
'use strict';
const TEN_CACHE = 'thosat-pro-v24';
const VO_APP = [
  './', 'index.html', 'engine.js', 'dexe.js', 'catalogue.js', 'phieu-anh.js',
  'minh-hoa.js', 'vat-tu.js', 'catalogue-all.json',
  'manifest.webmanifest', 'icon-192.png', 'icon-512.png',
  '../catalogue/mau/danh-sach.json', '../catalogue/mau/CD-01.json',
  '../catalogue/mau/LC-01.json', '../catalogue/mau/LC-02.json', '../catalogue/mau/LC-03.json', '../catalogue/mau/LC-04.json', '../catalogue/mau/CT-01.json', '../catalogue/mau/CT-02.json', '../catalogue/mau/CT-03.json', '../catalogue/mau/CT-04.json',
  '../catalogue/mau/MT-01.json', '../catalogue/mau/MT-02.json',
  '../catalogue/mau/C-01.json', '../catalogue/mau/LC-05.json', '../catalogue/mau/SH-01.json', '../catalogue/mau/SH-02.json', '../catalogue/mau/BV-01.json', '../catalogue/mau/BV-02.json', '../catalogue/mau/C-02.json', '../catalogue/mau/CG-01.json',
  '../catalogue/mau/MK-01.json'
];

self.addEventListener('install', (e) => {
  // cache:'reload' — BẮT BUỘC lấy thẳng từ mạng, không qua HTTP cache trình duyệt
  // (không có nó, cache phiên bản mới bị đổ đầy bằng file cũ)
  e.waitUntil(caches.open(TEN_CACHE).then((c) =>
    c.addAll(VO_APP.map((u) => new Request(u, { cache: 'reload' })))
  ).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then((ds) => Promise.all(
      ds.filter((t) => t !== TEN_CACHE).map((t) => caches.delete(t))
    )).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (e) => {
  const url = new URL(e.request.url);
  if (e.request.method !== 'GET' || url.origin !== self.location.origin) return;
  e.respondWith(
    caches.match(e.request, { ignoreSearch: true }).then((daCo) => {
      const tuMang = fetch(e.request).then((tra) => {
        if (tra && tra.ok) {
          const ban = tra.clone();
          caches.open(TEN_CACHE).then((c) => c.put(e.request, ban));
        }
        return tra;
      }).catch(() => daCo); // mất mạng → dùng bản cache
      return daCo || tuMang;
    })
  );
});
