import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import Link from "next/link"
import type { Manga } from "@/types/manga"

interface RecentlyAddedMangaProps {
  manga: Manga[]
}

export function RecentlyAddedManga({ manga }: RecentlyAddedMangaProps) {
  if (manga.length === 0) {
    return (
      <div className="text-center py-6">
        <p className="text-muted-foreground">No manga added yet.</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {manga.map((manga) => (
        <Link
          key={manga.id}
          href={`/manga/${manga.id}`}
          className="flex items-center space-x-4 rounded-md border p-4 transition-all hover:bg-accent"
        >
          <Avatar>
            <AvatarImage src={manga.cover || "/placeholder.svg?height=40&width=40"} alt={manga.title} />
            <AvatarFallback>{manga.title.substring(0, 2)}</AvatarFallback>
          </Avatar>
          <div className="flex-1 space-y-1">
            <p className="font-medium leading-none">{manga.title}</p>
            <p className="text-sm text-muted-foreground">{manga.author}</p>
          </div>
          <div className="flex flex-col items-end gap-2">
            <Badge variant="outline">{manga.status}</Badge>
            <span className="text-xs text-muted-foreground">
              {manga.createdAt ? new Date(manga.createdAt).toLocaleDateString() : "Recently added"}
            </span>
          </div>
        </Link>
      ))}
    </div>
  )
}
