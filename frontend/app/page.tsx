"use client"

import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import Link from "next/link"
import { BookOpen, BookPlus, Clock, ListChecks, TrendingUp } from "lucide-react"
import { RecentlyAddedManga } from "@/components/recently-added-manga"
import { ReadingProgress } from "@/components/reading-progress"
import { MangaService } from "@/services/manga-service"
import { StatsService } from "@/services/stats-service"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Skeleton } from "@/components/ui/skeleton"
import type { Manga } from "@/types/manga"

export default function Home() {
  const [stats, setStats] = useState<{
    totalManga: number
    reading: number
    completed: number
    readingStreak: number
    longestStreak: number
  } | null>(null)

  const [recentManga, setRecentManga] = useState<Manga[]>([])
  const [readingManga, setReadingManga] = useState<Manga[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadDashboardData = async () => {
      setLoading(true)
      setError(null)

      try {
        // Load stats
        const statsData = await StatsService.getDashboardStats()
        setStats({
          totalManga: statsData.totalManga,
          reading: statsData.reading,
          completed: statsData.completed,
          readingStreak: statsData.readingStreak,
          longestStreak: statsData.longestStreak,
        })

        // Load recently added manga
        const recentlyAdded = await MangaService.getRecentlyAdded(4)
        setRecentManga(recentlyAdded)

        // Load reading progress
        const readingProgress = await MangaService.getReadingProgress(3)
        setReadingManga(readingProgress)
      } catch (err) {
        console.error("Failed to load dashboard data:", err)
        setError("Failed to load dashboard data. Please try again later.")
      } finally {
        setLoading(false)
      }
    }

    loadDashboardData()
  }, [])

  return (
    <div className="container py-10">
      <h1 className="text-4xl font-bold tracking-tight mb-6">Welcome to Kurobara</h1>

      {error && (
        <Alert variant="destructive" className="mb-6">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        {loading ? (
          Array.from({ length: 4 }).map((_, index) => <Skeleton key={index} className="h-32" />)
        ) : (
          <>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Manga</CardTitle>
                <BookOpen className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats?.totalManga || 0}</div>
                <p className="text-xs text-muted-foreground">+{recentManga.length} added recently</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Currently Reading</CardTitle>
                <Clock className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats?.reading || 0}</div>
                <p className="text-xs text-muted-foreground">{readingManga.length} updated recently</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Completed</CardTitle>
                <ListChecks className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats?.completed || 0}</div>
                <p className="text-xs text-muted-foreground">
                  {stats
                    ? `${Math.round((stats.completed / stats.totalManga) * 100)}% of your collection`
                    : "0% of your collection"}
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Reading Streak</CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats?.readingStreak || 0} days</div>
                <p className="text-xs text-muted-foreground">Your longest streak: {stats?.longestStreak || 0} days</p>
              </CardContent>
            </Card>
          </>
        )}
      </div>

      <div className="grid gap-6 md:grid-cols-2 mt-6">
        <Card className="col-span-1">
          <CardHeader>
            <CardTitle>Recently Added</CardTitle>
            <CardDescription>The latest additions to your collection</CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="space-y-4">
                {Array.from({ length: 4 }).map((_, index) => (
                  <Skeleton key={index} className="h-16" />
                ))}
              </div>
            ) : (
              <RecentlyAddedManga manga={recentManga} />
            )}
          </CardContent>
          <CardFooter>
            <Button asChild variant="outline" className="w-full">
              <Link href="/collection">View All</Link>
            </Button>
          </CardFooter>
        </Card>

        <Card className="col-span-1">
          <CardHeader>
            <CardTitle>Reading Progress</CardTitle>
            <CardDescription>Continue where you left off</CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="space-y-4">
                {Array.from({ length: 3 }).map((_, index) => (
                  <Skeleton key={index} className="h-16" />
                ))}
              </div>
            ) : (
              <ReadingProgress manga={readingManga} />
            )}
          </CardContent>
          <CardFooter>
            <Button asChild variant="outline" className="w-full">
              <Link href="/reading">View All</Link>
            </Button>
          </CardFooter>
        </Card>
      </div>

      <div className="mt-6">
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              <Button asChild className="h-auto py-4 flex flex-col items-center justify-center gap-2">
                <Link href="/manga/add">
                  <BookPlus className="h-5 w-5" />
                  <span>Add New Manga</span>
                </Link>
              </Button>
              <Button asChild variant="outline" className="h-auto py-4 flex flex-col items-center justify-center gap-2">
                <Link href="/reading/continue">
                  <Clock className="h-5 w-5" />
                  <span>Continue Reading</span>
                </Link>
              </Button>
              <Button asChild variant="outline" className="h-auto py-4 flex flex-col items-center justify-center gap-2">
                <Link href="/collection/import">
                  <BookOpen className="h-5 w-5" />
                  <span>Import Collection</span>
                </Link>
              </Button>
              <Button asChild variant="outline" className="h-auto py-4 flex flex-col items-center justify-center gap-2">
                <Link href="/discover">
                  <TrendingUp className="h-5 w-5" />
                  <span>Discover New Manga</span>
                </Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
