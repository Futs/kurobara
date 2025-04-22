import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Progress } from "@/components/ui/progress"
import Link from "next/link"
import type { Manga } from "@/types/manga"

interface ReadingProgressProps {
  manga: Manga[]
}

export function ReadingProgress({ manga }: ReadingProgressProps) {
  if (manga.length === 0) {
    return (
      <div className="text-center py-6">
        <p className="text-muted-foreground">No manga in progress.</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {manga.map((manga) => (
        <Link
          key={manga.id}
          href={`/manga/${manga.id}/read`}
          className="flex items-center space-x-4 rounded-md border p-4 transition-all hover:bg-accent"
        >
          <Avatar>
            <AvatarImage src={manga.cover || "/placeholder.svg?height=40&width=40"} alt={manga.title} />
            <AvatarFallback>{manga.title.substring(0, 2)}</AvatarFallback>
          </Avatar>
          <div className="flex-1 space-y-2">
            <div className="flex justify-between">
              <p className="font-medium leading-none">{manga.title}</p>
              <span className="text-xs text-muted-foreground">{manga.lastRead || "Recently read"}</span>
            </div>
            <div className="flex items-center gap-2">
              <Progress
                value={manga.progressPercentage || 0}
                className="h-2 dark:bg-secondary/50"
                indicatorClassName="dark:bg-primary"
              />
              <span className="text-xs text-muted-foreground whitespace-nowrap">
                {manga.progress || 0}/{manga.totalChapters || "?"}
              </span>
            </div>
          </div>
        </Link>
      ))}
    </div>
  )
}
