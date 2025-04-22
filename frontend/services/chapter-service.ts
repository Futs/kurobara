import { get, post, withErrorHandling } from "./api"
import type { Chapter } from "@/types/manga"

interface ChapterListResponse {
  data: Chapter[]
  total: number
}

interface ChapterPagesResponse {
  pages: string[]
  chapterInfo: Chapter
}

export const ChapterService = {
  getByMangaId: withErrorHandling(async (mangaId: number): Promise<ChapterListResponse> => {
    return get<ChapterListResponse>(`/manga/${mangaId}/chapters`)
  }),

  getById: withErrorHandling(async (mangaId: number, chapterId: string): Promise<Chapter> => {
    return get<Chapter>(`/manga/${mangaId}/chapters/${chapterId}`)
  }),

  getChapterPages: withErrorHandling(async (mangaId: number, chapterId: string): Promise<ChapterPagesResponse> => {
    return get<ChapterPagesResponse>(`/manga/${mangaId}/chapters/${chapterId}/pages`)
  }),

  markAsRead: withErrorHandling(async (mangaId: number, chapterId: string): Promise<Chapter> => {
    return post<Chapter>(`/manga/${mangaId}/chapters/${chapterId}/read`)
  }),

  markAsUnread: withErrorHandling(async (mangaId: number, chapterId: string): Promise<Chapter> => {
    return post<Chapter>(`/manga/${mangaId}/chapters/${chapterId}/unread`)
  }),

  markMultipleAsRead: withErrorHandling(async (mangaId: number, chapterIds: string[]): Promise<void> => {
    return post<void>(`/manga/${mangaId}/chapters/read`, { chapterIds })
  }),
}
