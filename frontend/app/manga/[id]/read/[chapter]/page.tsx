"use client"

import { useEffect, useState } from "react"
import { useParams } from "next/navigation"
import { ChapterService } from "@/services/chapter-service"
import { ReaderProvider } from "@/contexts/reader-context"
import { ReaderView } from "@/components/reader/reader-view"
import { ProtectedRoute } from "@/components/protected-route"
import type { Chapter } from "@/types/manga"

export default function ReadChapterPage() {
  const params = useParams()
  const mangaId = Number(params.id)
  const chapterNumber = Number(params.chapter)

  const [pages, setPages] = useState<string[]>([])
  const [chapterInfo, setChapterInfo] = useState<Chapter | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadChapterPages = async () => {
      setIsLoading(true)
      setError(null)
      try {
        // First, get the chapter ID from the chapter number
        const chaptersResponse = await ChapterService.getByMangaId(mangaId)
        const chapter = chaptersResponse.data.find((c) => c.number === chapterNumber)

        if (!chapter) {
          setError("Chapter not found")
          setIsLoading(false)
          return
        }

        // Then, get the chapter pages
        const response = await ChapterService.getChapterPages(mangaId, chapter.id)
        setPages(response.pages)
        setChapterInfo(response.chapterInfo)

        // Mark the chapter as read
        await ChapterService.markAsRead(mangaId, chapter.id)
      } catch (err: any) {
        setError(err.message || "Failed to load chapter pages")
      } finally {
        setIsLoading(false)
      }
    }

    loadChapterPages()
  }, [mangaId, chapterNumber])

  return (
    <ProtectedRoute>
      <ReaderProvider
        initialPageInfo={{
          mangaId,
          chapterNumber,
          totalPages: pages.length,
          chapterId: chapterInfo?.id || "",
        }}
      >
        <ReaderView pages={pages} isLoading={isLoading} error={error} />
      </ReaderProvider>
    </ProtectedRoute>
  )
}
