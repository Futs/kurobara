"use client"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { WifiOff, RefreshCw } from "lucide-react"
import Link from "next/link"

export default function OfflinePage() {
  return (
    <div className="container flex items-center justify-center min-h-screen py-10">
      <Card className="w-full max-w-md">
        <CardHeader>
          <div className="flex justify-center mb-4">
            <WifiOff className="h-12 w-12 text-muted-foreground" />
          </div>
          <CardTitle className="text-2xl text-center">You're Offline</CardTitle>
          <CardDescription className="text-center">
            It looks like you've lost your internet connection. Some features may be unavailable.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-center text-muted-foreground mb-4">
            You can still access your downloaded manga and continue reading offline.
          </p>
          <div className="flex flex-col gap-2">
            <Button asChild variant="outline" className="w-full">
              <Link href="/collection">Go to My Collection</Link>
            </Button>
            <Button asChild variant="outline" className="w-full">
              <Link href="/reading">Continue Reading</Link>
            </Button>
          </div>
        </CardContent>
        <CardFooter>
          <Button className="w-full" onClick={() => window.location.reload()}>
            <RefreshCw className="mr-2 h-4 w-4" />
            Try Again
          </Button>
        </CardFooter>
      </Card>
    </div>
  )
}
