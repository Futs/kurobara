"use client"

import { useState, useCallback } from "react"
import { MangaService } from "@/services/manga-service"
import type { Manga, MangaFilters, MangaFormData } from "@/types/manga"
import { ApiError } from "@/services/api"

export function useManga() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchManga = useCallback(async (filters?: MangaFilters) => {
    setLoading(true)
    setError(null)
    try {
      const result = await MangaService.getAll(filters)
      setLoading(false)
      return result
    } catch (err) {
      setLoading(false)
      if (err instanceof ApiError) {
        setError(err.message)
      } else {
        setError("An unexpected error occurred")
      }
      throw err
    }
  }, [])

  const fetchMangaById = useCallback(async (id: number) => {
    setLoading(true)
    setError(null)
    try {
      const result = await MangaService.getById(id)
      setLoading(false)
      return result
    } catch (err) {
      setLoading(false)
      if (err instanceof ApiError) {
        setError(err.message)
      } else {
        setError("An unexpected error occurred")
      }
      throw err
    }
  }, [])

  const createManga = useCallback(async (data: MangaFormData) => {
    setLoading(true)
    setError(null)
    try {
      const result = await MangaService.create(data)
      setLoading(false)
      return result
    } catch (err) {
      setLoading(false)
      if (err instanceof ApiError) {
        setError(err.message)
      } else {
        setError("An unexpected error occurred")
      }
      throw err
    }
  }, [])

  const updateManga = useCallback(async (id: number, data: Partial<Manga>) => {
    setLoading(true)
    setError(null)
    try {
      const result = await MangaService.update(id, data)
      setLoading(false)
      return result
    } catch (err) {
      setLoading(false)
      if (err instanceof ApiError) {
        setError(err.message)
      } else {
        setError("An unexpected error occurred")
      }
      throw err
    }
  }, [])

  const deleteManga = useCallback(async (id: number) => {
    setLoading(true)
    setError(null)
    try {
      await MangaService.delete(id)
      setLoading(false)
    } catch (err) {
      setLoading(false)
      if (err instanceof ApiError) {
        setError(err.message)
      } else {
        setError("An unexpected error occurred")
      }
      throw err
    }
  }, [])

  const toggleFavorite = useCallback(async (id: number) => {
    setError(null)
    try {
      const result = await MangaService.toggleFavorite(id)
      return result
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message)
      } else {
        setError("An unexpected error occurred")
      }
      throw err
    }
  }, [])

  const updateProgress = useCallback(async (id: number, progress: number) => {
    setError(null)
    try {
      const result = await MangaService.updateProgress(id, progress)
      return result
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message)
      } else {
        setError("An unexpected error occurred")
      }
      throw err
    }
  }, [])

  return {
    loading,
    error,
    fetchManga,
    fetchMangaById,
    createManga,
    updateManga,
    deleteManga,
    toggleFavorite,
    updateProgress,
  }
}
