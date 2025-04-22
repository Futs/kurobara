import { get, withErrorHandling } from "./api"

interface DashboardStats {
  totalManga: number
  reading: number
  completed: number
  readingStreak: number
  longestStreak: number
  recentlyAdded: number
}

export const StatsService = {
  getDashboardStats: withErrorHandling(async (): Promise<DashboardStats> => {
    return get<DashboardStats>("/stats/dashboard")
  }),
}
