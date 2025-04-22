"use client"

import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { BookOpen, Edit, Heart, Share2, Star } from "lucide-react"
import Image from "next/image"
import Link from "next/link"
import { ChapterList } from "@/components/chapter-list"
import { useManga } from "@/hooks/use-manga"
import { useChapters } from "@/hooks/use-chapters"
import type { Manga, Chapter } from "@/types/manga"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Skeleton } from "@/components/ui/skeleton"
import { ProtectedRoute } from "@/components/protected-route"
import { DownloadMangaButton } from "@/components/offline/download-manga-button"
import { OfflineIndicator } from "@/components/offline/offline-indicator"
import { useOffline } from "@/hooks/use-offline"
import { getOfflineManga, getOfflineChaptersForManga } from "@/services/offline-storage"

export default function MangaDetailPage({ params }: { params: { id: string } }) {
  const [manga, setManga] = useState<Manga | null>(null)
  const [chapters, setChapters] = useState<Chapter[]>([])

  const { fetchMangaById, toggleFavorite, loading: mangaLoading, error: mangaError } = useManga()
  const { fetchChapters, loading: chaptersLoading, error: chaptersError } = useChapters()
  const { offline } = useOffline()

  useEffect(() => {
    const loadManga = async () => {
      try {
        if (offline) {
          // Try to load from offline storage
          const offlineManga = await getOfflineManga(Number(params.id))
          if (offlineManga) {
            setManga(offlineManga)
            return
          }
        }

        // Load from API
        const mangaData = await fetchMangaById(Number(params.id))
        setManga(mangaData)
      } catch (err) {
        console.error("Failed to load manga:", err)
      }
    }

    loadManga()
  }, [fetchMangaById, params.id, offline])

  useEffect(() => {
    const loadChapters = async () => {
      if (!manga) return

      try {
        if (offline) {
          // Try to load from offline storage
          const offlineChapters = await getOfflineChaptersForManga(manga.id)
          if (offlineChapters.length > 0) {
            setChapters(offlineChapters)
            return
          }
        }

        // Load from API
        const result = await fetchChapters(manga.id)
        setChapters(result.data)
      } catch (err) {
        console.error("Failed to load chapters:", err)
      }
    }

    loadChapters()
  }, [fetchChapters, manga, offline])

  const handleToggleFavorite = async () => {
    if (!manga) return

    try {
      const updatedManga = await toggleFavorite(manga.id)
      setManga(updatedManga)
    } catch (err) {
      console.error("Failed to toggle favorite:", err)
    }
  }

  return (
    <ProtectedRoute>
      <div className="container py-10">
        {mangaLoading ? (
          <div className="grid gap-6 lg:grid-cols-3">
            <div className="lg:col-span-1">
              <Skeleton className="aspect-[3/4] w-full rounded-xl" />
            </div>
            <div className="lg:col-span-2">
              <Skeleton className="h-10 w-3/4 mb-2" />
              <Skeleton className="h-4 w-1/2 mb-6" />
              <Skeleton className="h-32 w-full mb-6" />
              <Skeleton className="h-8 w-full" />
            </div>
          </div>
        ) : mangaError ? (
          <Alert variant="destructive">
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>{mangaError}</AlertDescription>
            <Button asChild className="mt-4">
              <Link href="/collection">Back to Collection</Link>
            </Button>
          </Alert>
        ) : !manga ? (
          <Alert>
            <AlertTitle>Not Found</AlertTitle>
            <AlertDescription>The manga you're looking for could not be found.</AlertDescription>
            <Button asChild className="mt-4">
              <Link href="/collection">Back to Collection</Link>
            </Button>
          </Alert>
        ) : (
          <div className="grid gap-6 lg:grid-cols-3">
            <div className="lg:col-span-1">
              <Card>
                <CardContent className="p-4">
                  <div className="flex justify-between items-center mb-4">
                    <Badge variant="outline">{manga.status}</Badge>
                    <OfflineIndicator />
                  </div>
                  <div className="aspect-[3/4] relative rounded-md overflow-hidden mb-4">
                    <Image
                      src={manga.cover || "/placeholder.svg?height=400&width=300"}
                      alt={manga.title}
                      fill
                      className="object-cover"
                    />
                  </div>

                  <div className="flex flex-wrap gap-2 mb-4">
                    {manga.genres.map((genre) => (
                      <Badge key={genre} variant="secondary">
                        {genre}
                      </Badge>
                    ))}
                  </div>

                  <div className="space-y-2 mb-4">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Status</span>
                      <Badge variant="outline">{manga.status}</Badge>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Author</span>
                      <span>{manga.author}</span>
                    </div>
                    {manga.artist && manga.artist !== manga.author && (
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Artist</span>
                        <span>{manga.artist}</span>
                      </div>
                    )}
                    {manga.releaseYear && (
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Release Year</span>
                        <span>{manga.releaseYear}</span>
                      </div>
                    )}
                    {manga.publisher && (
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Publisher</span>
                        <span>{manga.publisher}</span>
                      </div>
                    )}
                    {manga.demographic && (
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Demographic</span>
                        <span>{manga.demographic}</span>
                      </div>
                    )}
                    {manga.rating && (
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Rating</span>
                        <div className="flex items-center">
                          <Star className="h-4 w-4 fill-primary text-primary mr-1" />
                          <span>{manga.rating}/5</span>
                        </div>
                      </div>
                    )}
                  </div>

                  {manga.progress !== undefined && (
                    <div className="space-y-2">
                      <div className="flex justify-between items-center text-sm">
                        <span className="text-muted-foreground">Progress</span>
                        <span>
                          {manga.progress}/{manga.totalChapters}
                        </span>
                      </div>
                      <Progress value={manga.progressPercentage} className="h-2" />
                      {manga.lastRead && (
                        <p className="text-xs text-muted-foreground text-right">Last read {manga.lastRead}</p>
                      )}
                    </div>
                  )}
                </CardContent>
                <CardFooter className="flex flex-col gap-2 p-4 pt-0">
                  <Button asChild className="w-full">
                    <Link href={`/manga/${manga.id}/read`}>
                      <BookOpen className="mr-2 h-4 w-4" />
                      Continue Reading
                    </Link>
                  </Button>
                  <DownloadMangaButton manga={manga} className="w-full" />
                  <div className="grid grid-cols-3 gap-2">
                    <Button variant="outline" size="icon" onClick={handleToggleFavorite}>
                      <Heart className={`h-4 w-4 ${manga.favorite ? "fill-red-500 text-red-500" : ""}`} />
                      <span className="sr-only">Favorite</span>
                    </Button>
                    <Button variant="outline" size="icon" asChild>
                      <Link href={`/manga/${manga.id}/edit`}>
                        <Edit className="h-4 w-4" />
                        <span className="sr-only">Edit</span>
                      </Link>
                    </Button>
                    <Button variant="outline" size="icon">
                      <Share2 className="h-4 w-4" />
                      <span className="sr-only">Share</span>
                    </Button>
                  </div>
                </CardFooter>
              </Card>
            </div>

            <div className="lg:col-span-2">
              <Card className="mb-6">
                <CardHeader>
                  <CardTitle className="text-2xl">{manga.title}</CardTitle>
                  <CardDescription>
                    {manga.author} {manga.releaseYear ? `• ${manga.releaseYear}` : ""}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <h3 className="font-semibold mb-2">Synopsis</h3>
                  <p className="text-muted-foreground">{manga.synopsis || "No synopsis available."}</p>
                </CardContent>
              </Card>

              <Tabs defaultValue="chapters">
                <TabsList className="grid w-full grid-cols-2">
                  <TabsTrigger value="chapters">Chapters</TabsTrigger>
                  <TabsTrigger value="related">Related Manga</TabsTrigger>
                </TabsList>
                <TabsContent value="chapters" className="mt-4">
                  <Card>
                    <CardHeader>
                      <CardTitle>Chapters</CardTitle>
                      <CardDescription>Track your reading progress through chapters</CardDescription>
                    </CardHeader>
                    <CardContent>
                      {chaptersError && (
                        <Alert variant="destructive" className="mb-4">
                          <AlertDescription>{chaptersError}</AlertDescription>
                        </Alert>
                      )}

                      {chaptersLoading ? (
                        <div className="space-y-2">
                          {Array.from({ length: 5 }).map((_, index) => (
                            <Skeleton key={index} className="h-16 w-full" />
                          ))}
                        </div>
                      ) : chapters.length > 0 ? (
                        <ChapterList mangaId={manga.id} chapters={chapters} />
                      ) : (
                        <p className="text-muted-foreground">No chapters available.</p>
                      )}
                    </CardContent>
                  </Card>
                </TabsContent>
                <TabsContent value="related" className="mt-4">
                  <Card>
                    <CardHeader>
                      <CardTitle>Related Manga</CardTitle>
                      <CardDescription>Similar titles you might enjoy</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <p className="text-muted-foreground">No related manga found.</p>
                    </CardContent>
                  </Card>
                </TabsContent>
              </Tabs>
            </div>
          </div>
        )}
      </div>
    </ProtectedRoute>
  )
}
