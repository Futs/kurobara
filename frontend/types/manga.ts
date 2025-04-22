export interface Manga {
  id: number
  title: string
  cover?: string
  author: string
  artist?: string
  status: "reading" | "completed" | "on-hold" | "dropped" | "plan-to-read"
  progress?: number
  totalChapters: number
  progressPercentage?: number
  genres: string[]
  synopsis?: string
  rating?: number
  releaseYear?: number
  publisher?: string
  demographic?: string
  lastRead?: string
  favorite?: boolean
  createdAt?: string
  updatedAt?: string
}

export interface Chapter {
  id: string
  mangaId: number
  number: number
  title: string
  releaseDate: string
  read: boolean
  current?: boolean
  pages?: number
  createdAt?: string
  updatedAt?: string
}

export interface MangaFormData {
  title: string
  author: string
  artist?: string
  status: string
  releaseYear?: string
  publisher?: string
  genres: string
  synopsis?: string
  totalChapters: string
  coverUrl?: string
}

export interface MangaFilters {
  status?: string
  search?: string
  sort?: string
  page?: number
  limit?: number
}
