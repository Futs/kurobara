export interface ReaderSettings {
  direction: "ltr" | "rtl"
  viewMode: "single" | "double" | "continuous"
  zoomLevel: number
  fitToWidth: boolean
  showPageNumbers: boolean
  backgroundColor: string
}

export interface PageInfo {
  pageNumber: number
  totalPages: number
  chapterNumber: number
  mangaId: number
  chapterId: string
}

export interface ReaderState extends ReaderSettings, PageInfo {
  isLoading: boolean
  isFullscreen: boolean
  isControlsVisible: boolean
  error: string | null
}
