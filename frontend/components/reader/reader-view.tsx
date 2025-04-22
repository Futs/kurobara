"use client"

import { useEffect, useState } from "react"
import { useReader } from "@/hooks/use-reader"
import { ReaderPage } from "@/components/reader/reader-page"
import { ReaderControls } from "@/components/reader/reader-controls"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Loader2 } from "lucide-react"

interface ReaderViewProps {
  pages: string[]
  isLoading?: boolean
  error?: string | null
}

export function ReaderView({ pages, isLoading = false, error = null }: ReaderViewProps) {
  const { pageNumber, direction, viewMode, backgroundColor } = useReader()
  const [visiblePages, setVisiblePages] = useState<string[]>([])

  useEffect(() => {
    if (viewMode === "single") {
      setVisiblePages([pages[pageNumber - 1]])
    } else if (viewMode === "double") {
      // For double page view, show two pages side by side
      // For the first page, show only one page
      if (pageNumber === 1) {
        setVisiblePages([pages[0]])
      } else {
        // For even page numbers, show current and previous page
        // For odd page numbers, show current and next page
        const isEven = pageNumber % 2 === 0
        if (isEven) {
          setVisiblePages([pages[pageNumber - 2], pages[pageNumber - 1]])
        } else {
          if (pageNumber < pages.length) {
            setVisiblePages([pages[pageNumber - 1], pages[pageNumber]])
          } else {
            setVisiblePages([pages[pageNumber - 1]])
          }
        }
      }
    } else if (viewMode === "continuous") {
      // For continuous view, show all pages
      setVisiblePages(pages)
    }
  }, [pageNumber, viewMode, pages])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen" style={{ backgroundColor }}>
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen p-4" style={{ backgroundColor }}>
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </div>
    )
  }

  return (
    <div className="relative h-screen overflow-auto" style={{ backgroundColor }}>
      <div
        className={`h-full ${viewMode === "continuous" ? "overflow-y-auto py-4" : "flex items-center justify-center"}`}
      >
        <div
          className={`flex ${
            viewMode === "continuous" ? "flex-col items-center" : direction === "ltr" ? "flex-row" : "flex-row-reverse"
          } ${viewMode === "double" ? "gap-2" : ""}`}
        >
          {visiblePages.map((page, index) => (
            <ReaderPage
              key={`${pageNumber}-${index}`}
              src={page}
              pageNumber={
                viewMode === "continuous"
                  ? index + 1
                  : viewMode === "double" && visiblePages.length > 1
                    ? direction === "ltr"
                      ? pageNumber - 1 + index
                      : pageNumber + (index === 0 ? 1 : 0)
                    : pageNumber
              }
            />
          ))}
        </div>
      </div>
      <ReaderControls />
    </div>
  )
}
