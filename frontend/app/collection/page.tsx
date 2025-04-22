"use client"

import type React from "react"
import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { MangaGrid } from "@/components/manga-grid"
import { BookPlus, Search, Upload } from "lucide-react"
import Link from "next/link"
import { useManga } from "@/hooks/use-manga"
import type { Manga, MangaFilters } from "@/types/manga"
import { useDebounce } from "@/hooks/use-debounce"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Skeleton } from "@/components/ui/skeleton"
import { ProtectedRoute } from "@/components/protected-route"
import { OfflineIndicator } from "@/components/offline/offline-indicator"

export default function CollectionPage() {
  const [manga, setManga] = useState<Manga[]>([])
  const [total, setTotal] = useState(0)
  const [filters, setFilters] = useState<MangaFilters>({
    status: "all",
    sort: "title-asc",
    page: 1,
    limit: 24,
  })
  const [searchQuery, setSearchQuery] = useState("")
  const debouncedSearch = useDebounce(searchQuery, 500)

  const { fetchManga, loading, error } = useManga()

  useEffect(() => {
    const updatedFilters = { ...filters, search: debouncedSearch }
    loadManga(updatedFilters)
  }, [debouncedSearch, filters.status, filters.sort, filters.page, filters])

  const loadManga = async (currentFilters: MangaFilters) => {
    try {
      const result = await fetchManga(currentFilters)
      setManga(result.data)
      setTotal(result.total)
    } catch (err) {
      console.error("Failed to load manga:", err)
    }
  }

  const handleStatusChange = (value: string) => {
    setFilters((prev) => ({ ...prev, status: value, page: 1 }))
  }

  const handleSortChange = (value: string) => {
    setFilters((prev) => ({ ...prev, sort: value, page: 1 }))
  }

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value)
  }

  return (
    <ProtectedRoute>
      <div className="container py-10">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Your Collection</h1>
            <p className="text-muted-foreground">Manage and browse your manga collection</p>
          </div>
          <div className="flex flex-col sm:flex-row gap-2">
            <Button asChild>
              <Link href="/manga/add">
                <BookPlus className="mr-2 h-4 w-4" />
                Add New Manga
              </Link>
            </Button>
            <Button asChild variant="outline">
              <Link href="/collection/import">
                <Upload className="mr-2 h-4 w-4" />
                Import CBR/CBZ
              </Link>
            </Button>
          </div>
        </div>

        <div className="flex items-center gap-2 mb-4">
          <OfflineIndicator />
        </div>

        <div className="flex flex-col gap-4 md:flex-row mb-8">
          <div className="relative flex-1">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              type="search"
              placeholder="Search your collection..."
              className="pl-8"
              value={searchQuery}
              onChange={handleSearchChange}
            />
          </div>
          <Select defaultValue={filters.status} onValueChange={handleStatusChange}>
            <SelectTrigger className="w-full md:w-[180px]">
              <SelectValue placeholder="Status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Status</SelectItem>
              <SelectItem value="reading">Reading</SelectItem>
              <SelectItem value="completed">Completed</SelectItem>
              <SelectItem value="on-hold">On Hold</SelectItem>
              <SelectItem value="dropped">Dropped</SelectItem>
              <SelectItem value="plan-to-read">Plan to Read</SelectItem>
            </SelectContent>
          </Select>
          <Select defaultValue={filters.sort} onValueChange={handleSortChange}>
            <SelectTrigger className="w-full md:w-[180px]">
              <SelectValue placeholder="Sort By" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="title-asc">Title (A-Z)</SelectItem>
              <SelectItem value="title-desc">Title (Z-A)</SelectItem>
              <SelectItem value="added-new">Recently Added</SelectItem>
              <SelectItem value="added-old">Oldest Added</SelectItem>
              <SelectItem value="rating-high">Rating (High-Low)</SelectItem>
              <SelectItem value="rating-low">Rating (Low-High)</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {loading ? (
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6">
            {Array.from({ length: 12 }).map((_, index) => (
              <div key={index} className="space-y-3">
                <Skeleton className="aspect-[2/3] w-full rounded-xl" />
                <Skeleton className="h-4 w-3/4" />
                <Skeleton className="h-3 w-1/2" />
              </div>
            ))}
          </div>
        ) : manga.length > 0 ? (
          <MangaGrid manga={manga} />
        ) : (
          <div className="text-center py-12">
            <h3 className="text-lg font-medium">No manga found</h3>
            <p className="text-muted-foreground mt-1">
              {searchQuery ? "Try a different search term" : "Add some manga to your collection"}
            </p>
            {!searchQuery && (
              <div className="flex flex-col sm:flex-row justify-center gap-2 mt-4">
                <Button asChild>
                  <Link href="/manga/add">
                    <BookPlus className="mr-2 h-4 w-4" />
                    Add New Manga
                  </Link>
                </Button>
                <Button asChild variant="outline">
                  <Link href="/collection/import">
                    <Upload className="mr-2 h-4 w-4" />
                    Import CBR/CBZ
                  </Link>
                </Button>
              </div>
            )}
          </div>
        )}
      </div>
    </ProtectedRoute>
  )
}
