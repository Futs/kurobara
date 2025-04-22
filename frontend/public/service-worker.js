// Service Worker for Kurobara Manga Reader
const CACHE_NAME = "kurobara-cache-v1"
const OFFLINE_URL = "/offline"

// Resources to cache immediately on install
const PRECACHE_RESOURCES = ["/", "/offline", "/manifest.json", "/favicon.ico", "/logo.png"]

// Install event - precache critical resources
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches
      .open(CACHE_NAME)
      .then((cache) => {
        return cache.addAll(PRECACHE_RESOURCES)
      })
      .then(() => {
        return self.skipWaiting()
      }),
  )
})

// Activate event - clean up old caches
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames
            .filter((cacheName) => {
              return cacheName !== CACHE_NAME
            })
            .map((cacheName) => {
              return caches.delete(cacheName)
            }),
        )
      })
      .then(() => {
        return self.clients.claim()
      }),
  )
})

// Fetch event - network first, then cache, with offline fallback
self.addEventListener("fetch", (event) => {
  // Skip non-GET requests
  if (event.request.method !== "GET") return

  // Skip cross-origin requests
  if (!event.request.url.startsWith(self.location.origin)) return

  // Skip browser extensions
  if (event.request.url.startsWith("chrome-extension://")) return

  // Handle API requests differently - don't cache them by default
  if (event.request.url.includes("/api/")) {
    event.respondWith(
      fetch(event.request).catch(() => {
        // For API requests that fail, check if we have a cached response
        return caches.match(event.request).then((cachedResponse) => {
          if (cachedResponse) {
            return cachedResponse
          }
          // If no cached response, return a generic offline JSON response
          return new Response(
            JSON.stringify({
              error: "You are offline and this data is not available offline.",
            }),
            {
              headers: { "Content-Type": "application/json" },
            },
          )
        })
      }),
    )
    return
  }

  // For non-API requests, use a network-first strategy
  event.respondWith(
    fetch(event.request)
      .then((response) => {
        // Cache the response for future use
        const responseClone = response.clone()
        caches.open(CACHE_NAME).then((cache) => {
          cache.put(event.request, responseClone)
        })
        return response
      })
      .catch(() => {
        // If network fails, try to serve from cache
        return caches.match(event.request).then((cachedResponse) => {
          if (cachedResponse) {
            return cachedResponse
          }
          // If not in cache, serve the offline page
          if (event.request.mode === "navigate") {
            return caches.match(OFFLINE_URL)
          }
          // For other resources, return a simple error response
          return new Response("Not available offline", {
            status: 503,
            statusText: "Service Unavailable",
          })
        })
      }),
  )
})

// Handle background sync for pending operations
self.addEventListener("sync", (event) => {
  if (event.tag === "sync-reading-progress") {
    event.waitUntil(syncReadingProgress())
  }
})

// Function to sync reading progress when back online
async function syncReadingProgress() {
  try {
    // Get pending reading progress updates from IndexedDB
    const db = await openDatabase()
    const pendingUpdates = await getAllPendingUpdates(db)

    // Process each pending update
    for (const update of pendingUpdates) {
      try {
        const response = await fetch(update.url, {
          method: update.method,
          headers: update.headers,
          body: update.body ? JSON.stringify(update.body) : undefined,
        })

        if (response.ok) {
          // If successful, remove from pending updates
          await removePendingUpdate(db, update.id)
        }
      } catch (error) {
        console.error("Failed to sync update:", error)
        // Keep in pending updates to try again later
      }
    }
  } catch (error) {
    console.error("Sync failed:", error)
  }
}

// IndexedDB helper functions
function openDatabase() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open("kurobara-offline-db", 1)

    request.onupgradeneeded = (event) => {
      const db = event.target.result
      if (!db.objectStoreNames.contains("pendingUpdates")) {
        db.createObjectStore("pendingUpdates", { keyPath: "id", autoIncrement: true })
      }
    }

    request.onsuccess = () => resolve(request.result)
    request.onerror = () => reject(request.error)
  })
}

function getAllPendingUpdates(db) {
  return new Promise((resolve, reject) => {
    const transaction = db.transaction("pendingUpdates", "readonly")
    const store = transaction.objectStore("pendingUpdates")
    const request = store.getAll()

    request.onsuccess = () => resolve(request.result)
    request.onerror = () => reject(request.error)
  })
}

function removePendingUpdate(db, id) {
  return new Promise((resolve, reject) => {
    const transaction = db.transaction("pendingUpdates", "readwrite")
    const store = transaction.objectStore("pendingUpdates")
    const request = store.delete(id)

    request.onsuccess = () => resolve()
    request.onerror = () => reject(request.error)
  })
}
