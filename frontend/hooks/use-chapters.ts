"use client"

import { useState, useCallback } from "react"
import { ChapterService } from "@/services/chapter-service"
import { ApiError } from "@/services/api"

export function useChapters() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchChapters = useCallback(async (mangaId: number) => {
    setLoading(true)
    setError(null)
    try {
      const result = await ChapterService.getByMangaId(mangaId)
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

  const fetchChapter = useCallback(async (mangaId: number, chapterId: string) => {
    setLoading(true)
    setError(null)
    try {
      const result = await ChapterService.getById(mangaId, chapterId)
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

  const markAsRead = useCallback(async (mangaId: number, chapterId: string) => {
    setError(null)
    try {
      const result = await ChapterService.markAsRead(mangaId, chapterId)
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

  const markAsUnread = useCallback(async (mangaId: number, chapterId: string) => {
    setError(null)
    try {
      const result = await ChapterService.markAsUnread(mangaId, chapterId)
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

  const markMultipleAsRead = useCallback(async (mangaId: number, chapterIds: string[]) => {
    setError(null)
    try {
      await ChapterService.markMultipleAsRead(mangaId, chapterIds)
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
    fetchChapters,
    fetchChapter,
    markAsRead,
    markAsUnread,
    markMultipleAsRead,
  }
}
