export interface ImportedFile {
  name: string
  type: string
  size: number
  lastModified: number
}

export interface ImportedManga {
  title: string
  fileName: string
  fileType: "cbr" | "cbz" | "zip" | "rar" | "folder"
  fileSize: number
  pageCount: number
  coverImage?: string
  pages: string[]
}

export interface ImportProgress {
  status: "idle" | "extracting" | "processing" | "saving" | "complete" | "error"
  progress: number
  message: string
  error?: string
}
