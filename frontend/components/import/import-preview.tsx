"use client"

import { useState } from "react"
import Image from "next/image"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { ChevronLeft, ChevronRight } from "lucide-react"
import type { ImportedManga } from "@/types/import"

interface ImportPreviewProps {
  importedManga: ImportedManga
}

export function ImportPreview({ importedManga }: ImportPreviewProps) {
  const [currentPage, setCurrentPage] = useState(0)
  const totalPages = importedManga.pages.length

  const nextPage = () => {
    if (currentPage < totalPages - 1) {
      setCurrentPage(currentPage + 1)
    }
  }

  const prevPage = () => {
    if (currentPage > 0) {
      setCurrentPage(currentPage - 1)
    }
  }

  return (
    <Card>
      <CardContent className="p-4">
        <div className="flex justify-between items-center mb-4">
          <h3 className="font-medium">Preview</h3>
          <span className="text-sm text-muted-foreground">
            Page {currentPage + 1} of {totalPages}
          </span>
        </div>

        <div className="relative aspect-[2/3] bg-muted rounded-md overflow-hidden mb-4">
          <Image
            src={importedManga.pages[currentPage] || "/placeholder.svg"}
            alt={`Page ${currentPage + 1}`}
            fill
            className="object-contain"
          />
        </div>

        <div className="flex justify-between">
          <Button variant="outline" size="sm" onClick={prevPage} disabled={currentPage === 0}>
            <ChevronLeft className="h-4 w-4 mr-1" />
            Previous
          </Button>
          <Button variant="outline" size="sm" onClick={nextPage} disabled={currentPage === totalPages - 1}>
            Next
            <ChevronRight className="h-4 w-4 ml-1" />
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
