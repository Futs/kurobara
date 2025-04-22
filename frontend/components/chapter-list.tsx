"use client"

import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Check, Clock } from "lucide-react"
import Link from "next/link"
import type { Chapter } from "@/types/manga"
import { useChapters } from "@/hooks/use-chapters"
import { useState } from "react"

interface ChapterListProps {
  mangaId: number
  chapters: Chapter[]
}

export function ChapterList({ mangaId, chapters }: ChapterListProps) {
  const [chapterList, setChapterList] = useState<Chapter[]>(chapters)
  const { markAsRead, markAsUnread } = useChapters()

  const handleMarkAsRead = async (chapterId: string) => {
    try {
      const updatedChapter = await markAsRead(mangaId, chapterId)
      setChapterList((prev) => prev.map((chapter) => (chapter.id === chapterId ? updatedChapter : chapter)))
    } catch (err) {
      console.error("Failed to mark chapter as read:", err)
    }
  }

  const handleMarkAsUnread = async (chapterId: string) => {
    try {
      const updatedChapter = await markAsUnread(mangaId, chapterId)
      setChapterList((prev) => prev.map((chapter) => (chapter.id === chapterId ? updatedChapter : chapter)))
    } catch (err) {
      console.error("Failed to mark chapter as unread:", err)
    }
  }

  return (
    <div className="space-y-2">
      {chapterList.map((chapter) => (
        <div
          key={chapter.id}
          className={`flex items-center justify-between p-3 rounded-md border ${
            chapter.current
              ? "bg-accent border-primary/30 dark:bg-gradient-to-r dark:from-primary/10 dark:to-accent/20"
              : chapter.read
                ? "border-green-500/20 dark:border-green-500/30"
                : ""
          }`}
        >
          <div className="flex items-center gap-3">
            {chapter.read ? (
              <Check className="h-4 w-4 text-green-500 dark:text-green-400" />
            ) : chapter.current ? (
              <Clock className="h-4 w-4 text-primary dark:text-primary" />
            ) : (
              <div className="w-4" />
            )}
            <div>
              <p className="font-medium">{chapter.title}</p>
              <p className="text-xs text-muted-foreground">Released: {chapter.releaseDate}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {chapter.current && <Badge variant="secondary">Current</Badge>}
            <Button
              size="sm"
              variant="outline"
              onClick={() => (chapter.read ? handleMarkAsUnread(chapter.id) : handleMarkAsRead(chapter.id))}
            >
              {chapter.read ? "Mark Unread" : "Mark Read"}
            </Button>
            <Button asChild size="sm" variant={chapter.read ? "outline" : "default"}>
              <Link href={`/manga/${mangaId}/read/${chapter.number}`}>{chapter.read ? "Reread" : "Read"}</Link>
            </Button>
          </div>
        </div>
      ))}
    </div>
  )
}
