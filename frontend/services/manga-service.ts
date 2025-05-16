import { get, post, put, del, withErrorHandling } from "./api"
import type { Manga, MangaFilters, MangaFormData } from "@/types/manga"

interface MangaListResponse {
  data: Manga[]
  total: number
  page: number
  limit: number
}

export const MangaService = {
  getAll: withErrorHandling(async (filters?: MangaFilters): Promise<MangaListResponse> => {
    return get<MangaListResponse>("/manga", filters)
  }),

  getById: withErrorHandling(async (id: number): Promise<Manga> => {
    return get<Manga>(`/manga/${id}`)
  }),

  create: withErrorHandling(async (data: MangaFormData): Promise<Manga> => {
    // Convert form data to the format expected by the API
    const mangaData = {
      ...data,
      releaseYear: data.releaseYear ? Number.parseInt(data.releaseYear) : undefined,
      totalChapters: Number.parseInt(data.totalChapters),
      genres: data.genres.split(",").map((g) => g.trim()),
    }

    return post<Manga>("/manga", mangaData)
  }),

  update: withErrorHandling(async (id: number, data: Partial<Manga>): Promise<Manga> => {
    return put<Manga>(`/manga/${id}`, data)
  }),

  delete: withErrorHandling(async (id: number): Promise<void> => {
    return del<void>(`/manga/${id}`)
  }),

  toggleFavorite: withErrorHandling(async (id: number): Promise<Manga> => {
    return post<Manga>(`/manga/${id}/favorite`)
  }),

  updateProgress: withErrorHandling(async (id: number, progress: number): Promise<Manga> => {
    return put<Manga>(`/manga/${id}/progress`, { progress })
  }),

  getRecentlyAdded: withErrorHandling(async (limit = 5): Promise<Manga[]> => {
    return get<Manga[]>("/manga/recent", { limit })
  }),

  getReadingProgress: withErrorHandling(async (limit = 5): Promise<Manga[]> => {
    return get<Manga[]>("/manga/reading-progress", { limit })
  }),

  search: withErrorHandling(async (query: string): Promise<Manga[]> => {
    return get<Manga[]>("/manga/search", { query })
  }),
}

export async function getManga(id: string) {
  // Add caching options
  const response = await fetch(`${API_URL}/manga/${id}`, {
    next: { revalidate: 3600 }, // Cache for 1 hour
  });
  
  if (!response.ok) {
    throw new Error('Failed to fetch manga');
  }
  
  return response.json();
}
