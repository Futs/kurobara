"use client"

import { useState } from "react"
import Image from "next/image"
import { useReader } from "@/hooks/use-reader"
import { Skeleton } from "@/components/ui/skeleton"

interface ReaderPageProps {
  src: string
  pageNumber: number
  alt?: string
}

export function ReaderPage({ src, pageNumber, alt }: ReaderPageProps) {
  const { zoomLevel, fitToWidth, showPageNumbers, viewMode } = useReader()
  const [isLoading, setIsLoading] = useState(true)

  const handleImageLoad = () => {
    setIsLoading(false)
  }

  return (
    <div className={`relative flex justify-center items-center ${viewMode === "continuous" ? "mb-4" : "h-full"}`}>
      {isLoading && <Skeleton className="absolute inset-0 z-10" />}
      <div
        className={`relative ${fitToWidth ? "w-full" : ""}`}
        style={{
          maxWidth: fitToWidth ? "100%" : `${zoomLevel}%`,
          transition: "max-width 0.3s ease",
        }}
      >
        <Image
          src={src || "/placeholder.svg"}
          alt={alt || `Page ${pageNumber}`}
          width={800}
          height={1200}
          className="w-full h-auto object-contain"
          priority={true}
          onLoad={handleImageLoad}
          style={{ opacity: isLoading ? 0 : 1, transition: "opacity 0.3s ease" }}
        />
        {showPageNumbers && (
          <div className="absolute bottom-2 right-2 bg-background/80 text-foreground px-2 py-1 rounded text-sm">
            {pageNumber}
          </div>
        )}
      </div>
    </div>
  )
}
