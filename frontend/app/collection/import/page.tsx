"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import { z } from "zod"
import { ArrowLeft, Loader2 } from "lucide-react"
import Link from "next/link"
import { FileUpload } from "@/components/import/file-upload"
import { ImportProgress } from "@/components/import/import-progress"
import { ImportPreview } from "@/components/import/import-preview"
import { ImportService } from "@/services/import-service"
import { useToast } from "@/hooks/use-toast"
import { ProtectedRoute } from "@/components/protected-route"
import type { ImportedManga, ImportProgress as ImportProgressType } from "@/types/import"
import type { MangaFormData } from "@/types/manga"

const formSchema = z.object({
  title: z.string().min(1, "Title is required"),
  author: z.string().min(1, "Author is required"),
  artist: z.string().optional(),
  status: z.string().min(1, "Status is required"),
  releaseYear: z.string().regex(/^\d{4}$/, "Must be a valid year"),
  publisher: z.string().optional(),
  genres: z.string().min(1, "At least one genre is required"),
  synopsis: z.string().optional(),
  totalChapters: z.string().regex(/^\d+$/, "Must be a number"),
})

export default function ImportPage() {
  const router = useRouter()
  const { toast } = useToast()
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [importedManga, setImportedManga] = useState<ImportedManga | null>(null)
  const [importProgress, setImportProgress] = useState<ImportProgressType>({
    status: "idle",
    progress: 0,
    message: "",
  })
  const [isSaving, setIsSaving] = useState(false)

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      title: "",
      author: "",
      artist: "",
      status: "reading",
      releaseYear: "",
      publisher: "",
      genres: "",
      synopsis: "",
      totalChapters: "",
    },
  })

  const handleFileSelect = async (file: File) => {
    setSelectedFile(file)
    setImportedManga(null)

    try {
      const imported = await ImportService.importFile(file, setImportProgress)
      setImportedManga(imported)

      // Pre-fill the form with data from the imported manga
      form.setValue("title", imported.title)
      form.setValue("totalChapters", imported.pageCount.toString())
    } catch (error) {
      console.error("Import error:", error)
      toast({
        title: "Import Failed",
        description: error instanceof Error ? error.message : "Failed to import file",
        variant: "destructive",
      })
    }
  }

  const onSubmit = async (values: z.infer<typeof formSchema>) => {
    if (!importedManga) return

    setIsSaving(true)

    try {
      // Prepare manga form data
      const mangaData: MangaFormData = {
        ...values,
        coverUrl: importedManga.coverImage,
      }

      // Save the imported manga
      const mangaId = await ImportService.saveImportedManga(importedManga, mangaData, setImportProgress)

      toast({
        title: "Import Successful",
        description: "Manga has been added to your collection",
      })

      // Navigate to the manga detail page
      router.push(`/manga/${mangaId}`)
    } catch (error) {
      console.error("Save error:", error)
      toast({
        title: "Save Failed",
        description: error instanceof Error ? error.message : "Failed to save manga",
        variant: "destructive",
      })
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <ProtectedRoute>
      <div className="container py-10">
        <div className="mb-6">
          <Button asChild variant="ghost" className="mb-2">
            <Link href="/collection">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Collection
            </Link>
          </Button>
          <h1 className="text-3xl font-bold tracking-tight">Import Manga</h1>
          <p className="text-muted-foreground">Import CBR and CBZ files to your collection</p>
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          <div>
            <Card className="mb-6">
              <CardHeader>
                <CardTitle>Upload File</CardTitle>
                <CardDescription>Upload a CBR or CBZ file to import manga</CardDescription>
              </CardHeader>
              <CardContent>
                <FileUpload onFileSelect={handleFileSelect} className="mb-4" />
                <ImportProgress progress={importProgress} />
              </CardContent>
            </Card>

            {importedManga && <ImportPreview importedManga={importedManga} />}
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Manga Details</CardTitle>
              <CardDescription>Enter the details of the manga you're importing</CardDescription>
            </CardHeader>
            <CardContent>
              <Form {...form}>
                <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
                  <div className="grid gap-4 md:grid-cols-2">
                    <FormField
                      control={form.control}
                      name="title"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Title</FormLabel>
                          <FormControl>
                            <Input placeholder="One Piece" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="author"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Author</FormLabel>
                          <FormControl>
                            <Input placeholder="Eiichiro Oda" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="artist"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Artist (if different from author)</FormLabel>
                          <FormControl>
                            <Input placeholder="Artist name" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="status"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Reading Status</FormLabel>
                          <Select onValueChange={field.onChange} defaultValue={field.value}>
                            <FormControl>
                              <SelectTrigger>
                                <SelectValue placeholder="Select status" />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              <SelectItem value="reading">Reading</SelectItem>
                              <SelectItem value="completed">Completed</SelectItem>
                              <SelectItem value="on-hold">On Hold</SelectItem>
                              <SelectItem value="dropped">Dropped</SelectItem>
                              <SelectItem value="plan-to-read">Plan to Read</SelectItem>
                            </SelectContent>
                          </Select>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="releaseYear"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Release Year</FormLabel>
                          <FormControl>
                            <Input placeholder="1997" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="publisher"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Publisher</FormLabel>
                          <FormControl>
                            <Input placeholder="Shueisha" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="genres"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Genres</FormLabel>
                          <FormControl>
                            <Input placeholder="Action, Adventure, Fantasy" {...field} />
                          </FormControl>
                          <FormDescription>Separate genres with commas</FormDescription>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="totalChapters"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Total Pages/Chapters</FormLabel>
                          <FormControl>
                            <Input placeholder="1000" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>

                  <FormField
                    control={form.control}
                    name="synopsis"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Synopsis</FormLabel>
                        <FormControl>
                          <Textarea
                            placeholder="Enter a brief description of the manga..."
                            className="min-h-[120px]"
                            {...field}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <div className="flex justify-end gap-4">
                    <Button variant="outline" asChild>
                      <Link href="/collection">Cancel</Link>
                    </Button>
                    <Button type="submit" disabled={!importedManga || isSaving || importProgress.status === "saving"}>
                      {isSaving && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                      {isSaving ? "Saving..." : "Save to Collection"}
                    </Button>
                  </div>
                </form>
              </Form>
            </CardContent>
          </Card>
        </div>
      </div>
    </ProtectedRoute>
  )
}
