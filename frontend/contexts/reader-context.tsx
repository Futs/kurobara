"use client"

import type React from "react"
import { createContext, useContext, useState, useEffect } from "react"
import type { ReaderSettings, ReaderState, PageInfo } from "@/types/reader"

interface ReaderContextType extends ReaderState {
  nextPage: () => void
  prevPage: () => void
  goToPage: (pageNumber: number) => void
  toggleFullscreen: () => void
  toggleControls: () => void
  updateSettings: (settings: Partial<ReaderSettings>) => void
  resetSettings: () => void
}

const defaultSettings: ReaderSettings = {
  direction: "rtl", // Manga is typically read right-to-left
  viewMode: "single",
  zoomLevel: 100,
  fitToWidth: true,
  showPageNumbers: true,
  backgroundColor: "#ffffff",
}

const defaultState: ReaderState = {
  ...defaultSettings,
  pageNumber: 1,
  totalPages: 0,
  chapterNumber: 0,
  mangaId: 0,
  chapterId: "",
  isLoading: false,
  isFullscreen: false,
  isControlsVisible: true,
  error: null,
}

const ReaderContext = createContext<ReaderContextType | undefined>(undefined)

export function ReaderProvider({
  children,
  initialPageInfo,
}: { children: React.ReactNode; initialPageInfo?: Partial<PageInfo> }) {
  // Load saved settings from localStorage
  const loadSavedSettings = (): ReaderSettings => {
    if (typeof window === "undefined") return defaultSettings

    const savedSettings = localStorage.getItem("reader_settings")
    if (savedSettings) {
      try {
        return { ...defaultSettings, ...JSON.parse(savedSettings) }
      } catch (e) {
        console.error("Failed to parse saved reader settings:", e)
      }
    }
    return defaultSettings
  }

  const [state, setState] = useState<ReaderState>({
    ...defaultState,
    ...loadSavedSettings(),
    ...(initialPageInfo || {}),
  })

  // Save settings to localStorage when they change
  useEffect(() => {
    const settingsToSave: ReaderSettings = {
      direction: state.direction,
      viewMode: state.viewMode,
      zoomLevel: state.zoomLevel,
      fitToWidth: state.fitToWidth,
      showPageNumbers: state.showPageNumbers,
      backgroundColor: state.backgroundColor,
    }
    localStorage.setItem("reader_settings", JSON.stringify(settingsToSave))
  }, [state.direction, state.viewMode, state.zoomLevel, state.fitToWidth, state.showPageNumbers, state.backgroundColor])

  // Handle fullscreen changes
  useEffect(() => {
    const handleFullscreenChange = () => {
      setState((prev) => ({
        ...prev,
        isFullscreen: !!document.fullscreenElement,
      }))
    }

    document.addEventListener("fullscreenchange", handleFullscreenChange)
    return () => {
      document.removeEventListener("fullscreenchange", handleFullscreenChange)
    }
  }, [])

  // Handle keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Don't handle keyboard events if user is typing in an input
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
        return
      }

      switch (e.key) {
        case "ArrowRight":
          state.direction === "ltr" ? nextPage() : prevPage()
          break
        case "ArrowLeft":
          state.direction === "ltr" ? prevPage() : nextPage()
          break
        case "f":
          toggleFullscreen()
          break
        case " ": // Space bar
          toggleControls()
          e.preventDefault() // Prevent page scrolling
          break
      }
    }

    window.addEventListener("keydown", handleKeyDown)
    return () => {
      window.removeEventListener("keydown", handleKeyDown)
    }
  }, [state.direction])

  const nextPage = () => {
    setState((prev) => {
      if (prev.pageNumber < prev.totalPages) {
        return { ...prev, pageNumber: prev.pageNumber + 1 }
      }
      return prev
    })
  }

  const prevPage = () => {
    setState((prev) => {
      if (prev.pageNumber > 1) {
        return { ...prev, pageNumber: prev.pageNumber - 1 }
      }
      return prev
    })
  }

  const goToPage = (pageNumber: number) => {
    setState((prev) => {
      if (pageNumber >= 1 && pageNumber <= prev.totalPages) {
        return { ...prev, pageNumber }
      }
      return prev
    })
  }

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen().catch((err) => {
        console.error(`Error attempting to enable fullscreen: ${err.message}`)
      })
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen()
      }
    }
  }

  const toggleControls = () => {
    setState((prev) => ({ ...prev, isControlsVisible: !prev.isControlsVisible }))
  }

  const updateSettings = (settings: Partial<ReaderSettings>) => {
    setState((prev) => ({ ...prev, ...settings }))
  }

  const resetSettings = () => {
    setState((prev) => ({ ...prev, ...defaultSettings }))
  }

  const value = {
    ...state,
    nextPage,
    prevPage,
    goToPage,
    toggleFullscreen,
    toggleControls,
    updateSettings,
    resetSettings,
  }

  return <ReaderContext.Provider value={value}>{children}</ReaderContext.Provider>
}

export function useReader() {
  const context = useContext(ReaderContext)
  if (context === undefined) {
    throw new Error("useReader must be used within a ReaderProvider")
  }
  return context
}
