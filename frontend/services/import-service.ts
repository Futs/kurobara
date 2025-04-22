import { MangaService } from "./manga-service"
import type { ImportedManga, ImportProgress } from "@/types/import"
import type { MangaFormData } from "@/types/manga"

// Helper function to extract file name without extension
function getFileNameWithoutExtension(fileName: string): string {
  return fileName.replace(/\.[^/.]+$/, "")
}

// Helper function to convert ArrayBuffer to Base64
function arrayBufferToBase64(buffer: ArrayBuffer): string {
  let binary = ""
  const bytes = new Uint8Array(buffer)
  const len = bytes.byteLength
  for (let i = 0; i < len; i++) {
    binary += String.fromCharCode(bytes[i])
  }
  return window.btoa(binary)
}

// Helper function to determine if a file is an image
function isImageFile(fileName: string): boolean {
  const imageExtensions = [".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"]
  const lowerCaseFileName = fileName.toLowerCase()
  return imageExtensions.some((ext) => lowerCaseFileName.endsWith(ext))
}

// Helper function to sort image files naturally
function naturalSort(files: string[]): string[] {
  return files.sort((a, b) => {
    // Extract numbers from file names
    const aMatch = a.match(/\d+/) || ["0"]
    const bMatch = b.match(/\d+/) || ["0"]

    // Convert to numbers for comparison
    const aNum = Number.parseInt(aMatch[0], 10)
    const bNum = Number.parseInt(bMatch[0], 10)

    // If both have numbers, compare them
    if (!isNaN(aNum) && !isNaN(bNum)) {
      return aNum - bNum
    }

    // Otherwise, use standard string comparison
    return a.localeCompare(b)
  })
}

export const ImportService = {
  // Import a CBZ file (ZIP format)
  importCBZ: async (file: File, progressCallback: (progress: ImportProgress) => void): Promise<ImportedManga> => {
    progressCallback({
      status: "extracting",
      progress: 0,
      message: "Extracting CBZ file...",
    })

    try {
      // Load JSZip dynamically
      const JSZip = (await import("jszip")).default

      // Read the file
      const zipData = await JSZip.loadAsync(file)

      // Get all image files
      const imageFiles: string[] = []
      const imageBuffers: ArrayBuffer[] = []
      let fileCount = 0
      let processedCount = 0

      // Count files first
      zipData.forEach((relativePath, zipEntry) => {
        if (!zipEntry.dir && isImageFile(relativePath)) {
          fileCount++
        }
      })

      // Process each file
      const promises = []
      zipData.forEach((relativePath, zipEntry) => {
        if (!zipEntry.dir && isImageFile(relativePath)) {
          const promise = zipEntry.async("arraybuffer").then((content) => {
            imageFiles.push(relativePath)
            imageBuffers.push(content)
            processedCount++
            progressCallback({
              status: "processing",
              progress: (processedCount / fileCount) * 100,
              message: `Processing page ${processedCount} of ${fileCount}...`,
            })
          })
          promises.push(promise)
        }
      })

      await Promise.all(promises)

      // Sort files naturally
      const sortedIndices = naturalSort([...imageFiles]).map((file) => imageFiles.indexOf(file))
      const sortedBuffers = sortedIndices.map((index) => imageBuffers[index])

      // Convert to base64 for display
      const pages = sortedBuffers.map((buffer) => {
        const base64 = arrayBufferToBase64(buffer)
        const mimeType = "image/jpeg" // Assume JPEG for simplicity
        return `data:${mimeType};base64,${base64}`
      })

      progressCallback({
        status: "complete",
        progress: 100,
        message: "Import complete!",
      })

      return {
        title: getFileNameWithoutExtension(file.name),
        fileName: file.name,
        fileType: "cbz",
        fileSize: file.size,
        pageCount: pages.length,
        coverImage: pages[0],
        pages,
      }
    } catch (error) {
      console.error("Error importing CBZ:", error)
      progressCallback({
        status: "error",
        progress: 0,
        message: "Import failed",
        error: error instanceof Error ? error.message : "Unknown error",
      })
      throw error
    }
  },

  // Import a CBR file (RAR format)
  importCBR: async (file: File, progressCallback: (progress: ImportProgress) => void): Promise<ImportedManga> => {
    progressCallback({
      status: "extracting",
      progress: 0,
      message: "Extracting CBR file...",
    })

    try {
      // Note: Browser-based RAR extraction is limited
      // This is a simplified implementation that may not work with all CBR files
      // For a production app, consider using a server-side solution

      // Load rarjs dynamically
      const rarjs = await import("rarjs")
      const { RarArchive } = rarjs

      // Read the file as ArrayBuffer
      const fileBuffer = await file.arrayBuffer()

      // Create a RAR archive instance
      const archive = await RarArchive.open(fileBuffer)

      // Get all entries
      const entries = await archive.getEntries()

      // Filter image files
      const imageEntries = entries.filter((entry) => isImageFile(entry.name))

      // Sort entries naturally
      const sortedEntries = naturalSort(imageEntries.map((entry) => entry.name))
        .map((name) => imageEntries.find((entry) => entry.name === name))
        .filter(Boolean) as typeof imageEntries

      // Extract each image
      const pages: string[] = []
      let processedCount = 0

      for (const entry of sortedEntries) {
        // Extract the file
        const extracted = await entry.extract()

        // Convert to base64
        const base64 = arrayBufferToBase64(extracted)
        const mimeType = "image/jpeg" // Assume JPEG for simplicity
        pages.push(`data:${mimeType};base64,${base64}`)

        // Update progress
        processedCount++
        progressCallback({
          status: "processing",
          progress: (processedCount / sortedEntries.length) * 100,
          message: `Processing page ${processedCount} of ${sortedEntries.length}...`,
        })
      }

      progressCallback({
        status: "complete",
        progress: 100,
        message: "Import complete!",
      })

      return {
        title: getFileNameWithoutExtension(file.name),
        fileName: file.name,
        fileType: "cbr",
        fileSize: file.size,
        pageCount: pages.length,
        coverImage: pages[0],
        pages,
      }
    } catch (error) {
      console.error("Error importing CBR:", error)
      progressCallback({
        status: "error",
        progress: 0,
        message: "Import failed",
        error: error instanceof Error ? error.message : "Unknown error",
      })
      throw error
    }
  },

  // Save imported manga to the collection
  saveImportedManga: async (
    importedManga: ImportedManga,
    formData: MangaFormData,
    progressCallback: (progress: ImportProgress) => void,
  ): Promise<number> => {
    progressCallback({
      status: "saving",
      progress: 0,
      message: "Saving manga to collection...",
    })

    try {
      // Create the manga in the database
      const manga = await MangaService.create(formData)

      // TODO: Save pages to the server or cloud storage
      // This would typically involve uploading each page to your backend
      // For now, we'll just simulate progress

      for (let i = 0; i < importedManga.pages.length; i++) {
        // Simulate saving each page
        await new Promise((resolve) => setTimeout(resolve, 100))

        progressCallback({
          status: "saving",
          progress: (i / importedManga.pages.length) * 100,
          message: `Saving page ${i + 1} of ${importedManga.pages.length}...`,
        })
      }

      progressCallback({
        status: "complete",
        progress: 100,
        message: "Manga saved successfully!",
      })

      return manga.id
    } catch (error) {
      console.error("Error saving imported manga:", error)
      progressCallback({
        status: "error",
        progress: 0,
        message: "Failed to save manga",
        error: error instanceof Error ? error.message : "Unknown error",
      })
      throw error
    }
  },

  // Detect file type and import accordingly
  importFile: async (file: File, progressCallback: (progress: ImportProgress) => void): Promise<ImportedManga> => {
    const fileExtension = file.name.split(".").pop()?.toLowerCase()

    if (fileExtension === "cbz" || fileExtension === "zip") {
      return this.importCBZ(file, progressCallback)
    } else if (fileExtension === "cbr" || fileExtension === "rar") {
      return this.importCBR(file, progressCallback)
    } else {
      throw new Error(`Unsupported file type: ${fileExtension}`)
    }
  },
}
