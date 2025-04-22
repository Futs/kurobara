"use client"

import { Progress } from "@/components/ui/progress"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Loader2, CheckCircle2, XCircle } from "lucide-react"
import type { ImportProgress as ImportProgressType } from "@/types/import"

interface ImportProgressProps {
  progress: ImportProgressType
}

export function ImportProgress({ progress }: ImportProgressProps) {
  const { status, progress: percentage, message, error } = progress

  if (status === "idle") {
    return null
  }

  if (status === "error") {
    return (
      <Alert variant="destructive">
        <XCircle className="h-4 w-4" />
        <AlertTitle>Error</AlertTitle>
        <AlertDescription>
          {message}
          {error && <div className="mt-2 text-sm">{error}</div>}
        </AlertDescription>
      </Alert>
    )
  }

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <div className="flex items-center">
          {status === "complete" ? (
            <CheckCircle2 className="h-4 w-4 text-green-500 mr-2" />
          ) : (
            <Loader2 className="h-4 w-4 animate-spin mr-2" />
          )}
          <span className="font-medium">{message}</span>
        </div>
        <span className="text-sm text-muted-foreground">{Math.round(percentage)}%</span>
      </div>
      <Progress value={percentage} className="h-2" />
    </div>
  )
}
