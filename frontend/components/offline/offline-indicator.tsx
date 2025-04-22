"use client"

import { useOffline } from "@/hooks/use-offline"
import { WifiOff } from "lucide-react"
import { Badge } from "@/components/ui/badge"

export function OfflineIndicator() {
  const { offline } = useOffline()

  if (!offline) return null

  return (
    <Badge variant="outline" className="bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200">
      <WifiOff className="h-3 w-3 mr-1" />
      Offline
    </Badge>
  )
}
