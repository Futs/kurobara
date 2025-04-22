"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Download, Trash2, Loader2 } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import {
  saveMangaOffline,
  saveChapterOffline,
  removeMangaFromOffline,
  isMangaAvailableOffline,
} from "@/services/offline-storage"
import { ChapterService } from "@/services/chapter-service"
import type { Manga } from "@/types/manga"

interface DownloadMangaButtonProps {
  manga: Manga
  variant?: "default" | "outline" | "secondary" | "ghost" | "link" | "destructive"
  size?: "default" | "sm" | "lg" | "icon"
  className?: string
}

export function DownloadMangaButton({
  manga,
  variant = "outline",
  size = "default",
  className,
}: DownloadMangaButtonProps) {
  const [isAvailableOffline, setIsAvailableOffline] = useState(false)
  const [isDownloading, setIsDownloading] = useState(false)
  const [downloadProgress, setDownloadProgress] = useState(0)
  const { toast } = useToast()

  useEffect(() => {
    const checkOfflineStatus = async () => {
      const available = await isMangaAvailableOffline(manga.id)
      setIsAvailableOffline(available)
    }

    checkOfflineStatus()
  }, [manga.id])

  const handleDownload = async () => {
    if (isDownloading) return

    setIsDownloading(true)
    setDownloadProgress(0)

    try {
      // Save manga data
      await saveMangaOffline(manga)
      setDownloadProgress(10)

      // Get chapters
      const chaptersResponse = await ChapterService.getByMangaId(manga.id)
      const chapters = chaptersResponse.data
      setDownloadProgress(20)

      // Calculate progress increment per chapter
      const progressIncrement = 80 / chapters.length

      // Download each chapter
      for (let i = 0; i < chapters.length; i++) {
        const chapter = chapters[i]

        // Get chapter pages
        const pagesResponse = await ChapterService.getChapterPages(manga.id, chapter.id)

        // Save chapter with pages
        await saveChapterOffline(chapter, pagesResponse.pages)

        // Update progress
        setDownloadProgress(20 + (i + 1) * progressIncrement)
      }

      setIsAvailableOffline(true)
      toast({
        title: "Download Complete",
        description: `${manga.title} is now available offline`,
      })
    } catch (error) {
      console.error("Failed to download manga:", error)
      toast({
        title: "Download Failed",
        description: "There was an error downloading the manga",
        variant: "destructive",
      })
    } finally {
      setIsDownloading(false)
      setDownloadProgress(0)
    }
  }

  const handleRemove = async () => {
    if (isDownloading) return

    setIsDownloading(true)

    try {
      await removeMangaFromOffline(manga.id)
      setIsAvailableOffline(false)
      toast({
        title: "Removed from Offline Storage",
        description: `${manga.title} is no longer available offline`,
      })
    } catch (error) {
      console.error("Failed to remove manga from offline storage:", error)
      toast({
        title: "Removal Failed",
        description: "There was an error removing the manga from offline storage",
        variant: "destructive",
      })
    } finally {
      setIsDownloading(false)
    }
  }

  if (isAvailableOffline) {
    return (
      <Button variant="outline" size={size} className={className} onClick={handleRemove} disabled={isDownloading}>
        {isDownloading ? (
          <Loader2 className="h-4 w-4 animate-spin" />
        ) : (
          <>
            <Trash2 className="h-4 w-4 mr-2" />
            Remove Offline
          </>
        )}
      </Button>
    )
  }

  return (
    <Button variant={variant} size={size} className={className} onClick={handleDownload} disabled={isDownloading}>
      {isDownloading ? (
        <>
          <Loader2 className="h-4 w-4 animate-spin mr-2" />
          {downloadProgress > 0 ? `${Math.round(downloadProgress)}%` : "Downloading..."}
        </>
      ) : (
        <>
          <Download className="h-4 w-4 mr-2" />
          Download for Offline
        </>
      )}
    </Button>
  )
}
