import type { Manga, Chapter } from "@/types/manga"

const DB_NAME = "kurobara-offline-db"
const DB_VERSION = 1

interface OfflineDB {
  manga: {
    id: number
    data: Manga
    lastUpdated: number
  }[]
  chapters: {
    id: string
    mangaId: number
    data: Chapter
    pages: string[]
    lastUpdated: number
  }[]
  pendingUpdates: {
    id?: number
    url: string
    method: string
    headers: Record<string, string>
    body?: any
    timestamp: number
  }[]
}

// Open the IndexedDB database
async function openDatabase(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION)

    request.onupgradeneeded = (event) => {
      const db = (event.target as IDBOpenDBRequest).result

      // Create object stores if they don't exist
      if (!db.objectStoreNames.contains("manga")) {
        const mangaStore = db.createObjectStore("manga", { keyPath: "id" })
        mangaStore.createIndex("lastUpdated", "lastUpdated", { unique: false })
      }

      if (!db.objectStoreNames.contains("chapters")) {
        const chaptersStore = db.createObjectStore("chapters", { keyPath: "id" })
        chaptersStore.createIndex("mangaId", "mangaId", { unique: false })
        chaptersStore.createIndex("lastUpdated", "lastUpdated", { unique: false })
      }

      if (!db.objectStoreNames.contains("pendingUpdates")) {
        const pendingUpdatesStore = db.createObjectStore("pendingUpdates", { keyPath: "id", autoIncrement: true })
        pendingUpdatesStore.createIndex("timestamp", "timestamp", { unique: false })
      }
    }

    request.onsuccess = () => resolve(request.result)
    request.onerror = () => reject(request.error)
  })
}

// Save manga to offline storage
export async function saveMangaOffline(manga: Manga): Promise<void> {
  try {
    const db = await openDatabase()
    const transaction = db.transaction("manga", "readwrite")
    const store = transaction.objectStore("manga")

    await new Promise<void>((resolve, reject) => {
      const request = store.put({
        id: manga.id,
        data: manga,
        lastUpdated: Date.now(),
      })

      request.onsuccess = () => resolve()
      request.onerror = () => reject(request.error)
    })
  } catch (error) {
    console.error("Failed to save manga offline:", error)
    throw error
  }
}

// Get manga from offline storage
export async function getOfflineManga(id: number): Promise<Manga | null> {
  try {
    const db = await openDatabase()
    const transaction = db.transaction("manga", "readonly")
    const store = transaction.objectStore("manga")

    const result = await new Promise<any>((resolve, reject) => {
      const request = store.get(id)

      request.onsuccess = () => resolve(request.result)
      request.onerror = () => reject(request.error)
    })

    return result ? result.data : null
  } catch (error) {
    console.error("Failed to get manga from offline storage:", error)
    return null
  }
}

// Get all offline manga
export async function getAllOfflineManga(): Promise<Manga[]> {
  try {
    const db = await openDatabase()
    const transaction = db.transaction("manga", "readonly")
    const store = transaction.objectStore("manga")

    const result = await new Promise<any[]>((resolve, reject) => {
      const request = store.getAll()

      request.onsuccess = () => resolve(request.result)
      request.onerror = () => reject(request.error)
    })

    return result.map((item) => item.data)
  } catch (error) {
    console.error("Failed to get all manga from offline storage:", error)
    return []
  }
}

// Save chapter with pages to offline storage
export async function saveChapterOffline(chapter: Chapter, pages: string[]): Promise<void> {
  try {
    const db = await openDatabase()
    const transaction = db.transaction("chapters", "readwrite")
    const store = transaction.objectStore("chapters")

    await new Promise<void>((resolve, reject) => {
      const request = store.put({
        id: chapter.id,
        mangaId: chapter.mangaId,
        data: chapter,
        pages,
        lastUpdated: Date.now(),
      })

      request.onsuccess = () => resolve()
      request.onerror = () => reject(request.error)
    })
  } catch (error) {
    console.error("Failed to save chapter offline:", error)
    throw error
  }
}

// Get chapter with pages from offline storage
export async function getOfflineChapter(id: string): Promise<{ chapter: Chapter; pages: string[] } | null> {
  try {
    const db = await openDatabase()
    const transaction = db.transaction("chapters", "readonly")
    const store = transaction.objectStore("chapters")

    const result = await new Promise<any>((resolve, reject) => {
      const request = store.get(id)

      request.onsuccess = () => resolve(request.result)
      request.onerror = () => reject(request.error)
    })

    return result ? { chapter: result.data, pages: result.pages } : null
  } catch (error) {
    console.error("Failed to get chapter from offline storage:", error)
    return null
  }
}

// Get all chapters for a manga from offline storage
export async function getOfflineChaptersForManga(mangaId: number): Promise<Chapter[]> {
  try {
    const db = await openDatabase()
    const transaction = db.transaction("chapters", "readonly")
    const store = transaction.objectStore("chapters")
    const index = store.index("mangaId")

    const result = await new Promise<any[]>((resolve, reject) => {
      const request = index.getAll(mangaId)

      request.onsuccess = () => resolve(request.result)
      request.onerror = () => reject(request.error)
    })

    return result.map((item) => item.data)
  } catch (error) {
    console.error("Failed to get chapters from offline storage:", error)
    return []
  }
}

// Add a pending update to be processed when online
export async function addPendingUpdate(
  url: string,
  method: string,
  headers: Record<string, string>,
  body?: any,
): Promise<void> {
  try {
    const db = await openDatabase()
    const transaction = db.transaction("pendingUpdates", "readwrite")
    const store = transaction.objectStore("pendingUpdates")

    await new Promise<void>((resolve, reject) => {
      const request = store.add({
        url,
        method,
        headers,
        body,
        timestamp: Date.now(),
      })

      request.onsuccess = () => resolve()
      request.onerror = () => reject(request.error)
    })

    // Try to trigger a sync if the browser supports it
    if ("serviceWorker" in navigator && "SyncManager" in window) {
      const registration = await navigator.serviceWorker.ready
      await registration.sync.register("sync-reading-progress")
    }
  } catch (error) {
    console.error("Failed to add pending update:", error)
    throw error
  }
}

// Remove manga and its chapters from offline storage
export async function removeMangaFromOffline(mangaId: number): Promise<void> {
  try {
    const db = await openDatabase()

    // Remove manga
    const mangaTransaction = db.transaction("manga", "readwrite")
    const mangaStore = mangaTransaction.objectStore("manga")

    await new Promise<void>((resolve, reject) => {
      const request = mangaStore.delete(mangaId)

      request.onsuccess = () => resolve()
      request.onerror = () => reject(request.error)
    })

    // Remove chapters
    const chaptersTransaction = db.transaction("chapters", "readwrite")
    const chaptersStore = chaptersTransaction.objectStore("chapters")
    const chaptersIndex = chaptersStore.index("mangaId")

    const chaptersToDelete = await new Promise<any[]>((resolve, reject) => {
      const request = chaptersIndex.getAll(mangaId)

      request.onsuccess = () => resolve(request.result)
      request.onerror = () => reject(request.error)
    })

    for (const chapter of chaptersToDelete) {
      await new Promise<void>((resolve, reject) => {
        const request = chaptersStore.delete(chapter.id)

        request.onsuccess = () => resolve()
        request.onerror = () => reject(request.error)
      })
    }
  } catch (error) {
    console.error("Failed to remove manga from offline storage:", error)
    throw error
  }
}

// Check if a manga is available offline
export async function isMangaAvailableOffline(mangaId: number): Promise<boolean> {
  try {
    const manga = await getOfflineManga(mangaId)
    return !!manga
  } catch (error) {
    return false
  }
}

// Check if a chapter is available offline
export async function isChapterAvailableOffline(chapterId: string): Promise<boolean> {
  try {
    const chapter = await getOfflineChapter(chapterId)
    return !!chapter
  } catch (error) {
    return false
  }
}

// Get the total size of offline storage in bytes
export async function getOfflineStorageSize(): Promise<number> {
  try {
    if ("storage" in navigator && "estimate" in navigator.storage) {
      const estimate = await navigator.storage.estimate()
      return estimate.usage || 0
    }
    return 0
  } catch (error) {
    console.error("Failed to get storage size:", error)
    return 0
  }
}

// Register the service worker for offline support
export async function registerServiceWorker(): Promise<void> {
  if ("serviceWorker" in navigator) {
    try {
      const registration = await navigator.serviceWorker.register("/service-worker.js")
      console.log("Service Worker registered with scope:", registration.scope)
    } catch (error) {
      console.error("Service Worker registration failed:", error)
    }
  }
}

// Check if the app is online
export function isOnline(): boolean {
  return navigator.onLine
}

// Add event listeners for online/offline status
export function setupOnlineStatusListeners(onOnline: () => void, onOffline: () => void): () => void {
  window.addEventListener("online", onOnline)
  window.addEventListener("offline", onOffline)

  return () => {
    window.removeEventListener("online", onOnline)
    window.removeEventListener("offline", onOffline)
  }
}
