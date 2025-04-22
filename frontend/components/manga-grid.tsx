import { Card, CardContent, CardFooter } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import Link from "next/link"
import Image from "next/image"
import type { Manga } from "@/types/manga"

interface MangaGridProps {
  manga: Manga[]
}

export function MangaGrid({ manga }: MangaGridProps) {
  return (
    <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6">
      {manga.map((manga) => (
        <Link key={manga.id} href={`/manga/${manga.id}`}>
          <Card className="overflow-hidden h-full transition-all hover:shadow-md">
            <div className="aspect-[2/3] relative overflow-hidden">
              <Image
                src={manga.cover || "/placeholder.svg?height=300&width=200"}
                alt={manga.title}
                fill
                className="object-cover"
              />
              <div className="absolute top-2 right-2">
                <Badge
                  variant="outline"
                  className={`${
                    manga.status === "reading"
                      ? "bg-primary/10 text-primary border-primary/20"
                      : manga.status === "completed"
                        ? "bg-green-500/10 text-green-500 border-green-500/20"
                        : manga.status === "on-hold"
                          ? "bg-orange-500/10 text-orange-500 border-orange-500/20"
                          : manga.status === "dropped"
                            ? "bg-destructive/10 text-destructive border-destructive/20"
                            : "bg-secondary/80"
                  }`}
                >
                  {manga.status}
                </Badge>
              </div>
            </div>
            <CardContent className="p-3">
              <h3 className="font-semibold line-clamp-1">{manga.title}</h3>
              <p className="text-sm text-muted-foreground line-clamp-1">{manga.author}</p>
            </CardContent>
            <CardFooter className="p-3 pt-0 flex justify-between items-center">
              <div className="flex flex-wrap gap-1">
                {manga.genres.slice(0, 2).map((genre) => (
                  <Badge key={genre} variant="outline" className="text-xs">
                    {genre}
                  </Badge>
                ))}
                {manga.genres.length > 2 && (
                  <Badge variant="outline" className="text-xs">
                    +{manga.genres.length - 2}
                  </Badge>
                )}
              </div>
              <span className="text-xs text-muted-foreground">
                {manga.progress !== undefined && `${manga.progress}/${manga.totalChapters}`}
              </span>
            </CardFooter>
          </Card>
        </Link>
      ))}
    </div>
  )
}
