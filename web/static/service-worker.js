const CACHE_NAME =
    "shaunmariaos-static-v2";

const STATIC_ASSETS = [
    "/",
    "/static/app.css",
    "/static/app.js",
    "/static/calendar.js",
    "/static/money.js",
    "/static/tasks.js",
    "/static/us.js",
    "/static/pwa.js",
    "/static/manifest.json",
    "/static/icons/icon-192.png",
    "/static/icons/icon-512.png",
    "/static/icons/apple-touch-icon.png"
];


/* ==========================================================
   Install
   ========================================================== */

self.addEventListener(
    "install",
    event => {
        event.waitUntil(
            caches.open(
                CACHE_NAME
            ).then(
                cache =>
                    cache.addAll(
                        STATIC_ASSETS
                    )
            )
        );

        self.skipWaiting();
    }
);


/* ==========================================================
   Activate
   ========================================================== */

self.addEventListener(
    "activate",
    event => {
        event.waitUntil(
            caches.keys()
                .then(cacheNames => {
                    return Promise.all(
                        cacheNames
                            .filter(
                                name =>
                                    name !==
                                    CACHE_NAME
                            )
                            .map(
                                name =>
                                    caches.delete(
                                        name
                                    )
                            )
                    );
                })
        );

        self.clients.claim();
    }
);


/* ==========================================================
   Fetch
   ========================================================== */

self.addEventListener(
    "fetch",
    event => {
        const request =
            event.request;

        const url =
            new URL(
                request.url
            );

        /*
         * Never cache API data.
         */
        if (
            url.pathname.startsWith(
                "/api/"
            )
        ) {
            return;
        }

        /*
         * Network first.
         *
         * This prevents stale CSS/JS while
         * ShaunMariaOS is still being developed.
         */
        event.respondWith(
            fetch(request)
                .then(response => {

                    const responseCopy =
                        response.clone();

                    caches.open(
                        CACHE_NAME
                    ).then(cache => {
                        cache.put(
                            request,
                            responseCopy
                        );
                    });

                    return response;
                })
                .catch(() => {
                    return caches.match(
                        request
                    );
                })
        );
    }
);