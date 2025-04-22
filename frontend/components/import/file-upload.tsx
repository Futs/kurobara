"use client"

import type React from "react"

import { useState, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Upload, File, X } from "lucide-react"
import type { ImportedFile } from "@/types/import"

interface FileUploadProps {
  onFileSelect: (file: File) => void
  accept?: string
  maxSize?: number // in bytes
  className?: string
}

export function FileUpload({
  onFileSelect,
  accept = ".cbz,.cbr,.zip,.rar",
  maxSize = 500 * 1024 * 1024,
  className,
}: FileUploadProps) {
  const [dragActive, setDragActive] = useState(false)
  const [selectedFile, setSelectedFile] = useState<ImportedFile | null>(null)
  const [error, setError] = useState<string | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()

    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }

  const validateFile = (file: File): string | null => {
    // Check file type
    const fileExtension = file.name.split(".").pop()?.toLowerCase()
    const validExtensions = ["cbz", "cbr", "zip", "rar"]

    if (!validExtensions.includes(fileExtension || "")) {
      return `Invalid file type. Please upload a CBZ or CBR file.`
    }

    // Check file size
    if (file.size > maxSize) {
      return `File is too large. Maximum size is ${Math.round(maxSize / (1024 * 1024))}MB.`
    }

    return null
  }

  const processFile = (file: File) => {
    const validationError = validateFile(file)

    if (validationError) {
      setError(validationError)
      setSelectedFile(null)
      return
    }

    setError(null)
    setSelectedFile({
      name: file.name,
      type: file.type,
      size: file.size,
      lastModified: file.lastModified,
    })

    onFileSelect(file)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      processFile(e.dataTransfer.files[0])
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault()

    if (e.target.files && e.target.files.length > 0) {
      processFile(e.target.files[0])
    }
  }

  const handleButtonClick = () => {
    inputRef.current?.click()
  }

  const handleRemoveFile = () => {
    setSelectedFile(null)
    setError(null)
    if (inputRef.current) {
      inputRef.current.value = ""
    }
  }

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + " bytes"
    else if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB"
    else return (bytes / (1024 * 1024)).toFixed(1) + " MB"
  }

  return (
    <div className={className}>
      <input ref={inputRef} type="file" accept={accept} onChange={handleChange} className="hidden" />

      {!selectedFile ? (
        <Card
          className={`border-2 border-dashed ${
            dragActive ? "border-primary" : "border-border"
          } hover:border-primary transition-colors cursor-pointer`}
          onDragEnter={handleDrag}
          onDragOver={handleDrag}
          onDragLeave={handleDrag}
          onDrop={handleDrop}
          onClick={handleButtonClick}
        >
          <CardContent className="flex flex-col items-center justify-center py-10 text-center">
            <Upload className="h-10 w-10 text-muted-foreground mb-4" />
            <h3 className="text-lg font-medium mb-2">Drag & drop your file here</h3>
            <p className="text-sm text-muted-foreground mb-4">or click to browse (CBZ, CBR files)</p>
            <Button type="button" variant="outline">
              Select File
            </Button>
            {error && <p className="text-sm text-destructive mt-4">{error}</p>}
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardContent className="flex items-center p-4">
            <File className="h-8 w-8 text-primary mr-4" />
            <div className="flex-1">
              <p className="font-medium truncate">{selectedFile.name}</p>
              <p className="text-sm text-muted-foreground">{formatFileSize(selectedFile.size)}</p>
            </div>
            <Button variant="ghost" size="icon" onClick={handleRemoveFile} className="ml-2">
              <X className="h-4 w-4" />
              <span className="sr-only">Remove file</span>
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
