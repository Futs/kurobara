"use client"

import { useState, useEffect } from "react"
import { setupOnlineStatusListeners, isOnline } from "@/services/offline-storage"

export function useOffline() {
  const [online, setOnline] = useState<boolean>(true)

  useEffect(() => {
    // Set initial state
    setOnline(isOnline())

    // Setup listeners
    const cleanup = setupOnlineStatusListeners(
      () => setOnline(true),
      () => setOnline(false),
    )

    return cleanup
  }, [])

  return {
    online,
    offline: !online,
  }
}
