"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Slider } from "@/components/ui/slider"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { ChevronLeft, ChevronRight, Home, List, Maximize2, Minimize2, Settings, X } from "lucide-react"
import Link from "next/link"
import { useReader } from "@/hooks/use-reader"

export function ReaderControls() {
  const {
    pageNumber,
    totalPages,
    mangaId,
    chapterNumber,
    direction,
    viewMode,
    zoomLevel,
    fitToWidth,
    showPageNumbers,
    backgroundColor,
    isFullscreen,
    isControlsVisible,
    nextPage,
    prevPage,
    goToPage,
    toggleFullscreen,
    toggleControls,
    updateSettings,
    resetSettings,
  } = useReader()

  const [pageInput, setPageInput] = useState(pageNumber.toString())

  const handlePageInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setPageInput(e.target.value)
  }

  const handlePageInputSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const page = Number.parseInt(pageInput)
    if (!isNaN(page)) {
      goToPage(page)
    }
  }

  if (!isControlsVisible) {
    return (
      <button
        className="fixed top-0 left-0 w-full h-full z-40 cursor-none bg-transparent"
        onClick={toggleControls}
        aria-label="Show controls"
      />
    )
  }

  return (
    <div className="fixed inset-0 z-40 pointer-events-none">
      {/* Top bar */}
      <div className="absolute top-0 left-0 right-0 bg-background/90 backdrop-blur-sm p-2 flex items-center justify-between pointer-events-auto border-b border-primary/20 dark:bg-gradient-to-r dark:from-primary/5 dark:to-accent/10">
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="icon" asChild>
            <Link href={`/manga/${mangaId}`}>
              <Home className="h-4 w-4" />
              <span className="sr-only">Back to manga</span>
            </Link>
          </Button>
          <Button variant="ghost" size="icon" asChild>
            <Link href={`/manga/${mangaId}/chapters`}>
              <List className="h-4 w-4" />
              <span className="sr-only">Chapters</span>
            </Link>
          </Button>
          <div className="text-sm font-medium">Chapter {chapterNumber}</div>
        </div>

        <div className="flex items-center gap-2">
          <Popover>
            <PopoverTrigger asChild>
              <Button variant="ghost" size="icon">
                <Settings className="h-4 w-4" />
                <span className="sr-only">Settings</span>
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-80">
              <div className="grid gap-4">
                <div className="space-y-2">
                  <h4 className="font-medium leading-none">Reader Settings</h4>
                  <p className="text-sm text-muted-foreground">Customize your reading experience</p>
                </div>
                <div className="grid gap-2">
                  <div className="grid grid-cols-3 items-center gap-4">
                    <Label htmlFor="direction">Reading Direction</Label>
                    <Tabs
                      value={direction}
                      onValueChange={(value) => updateSettings({ direction: value as "ltr" | "rtl" })}
                      className="col-span-2"
                    >
                      <TabsList className="grid w-full grid-cols-2">
                        <TabsTrigger value="ltr">Left to Right</TabsTrigger>
                        <TabsTrigger value="rtl">Right to Left</TabsTrigger>
                      </TabsList>
                    </Tabs>
                  </div>
                  <div className="grid grid-cols-3 items-center gap-4">
                    <Label htmlFor="viewMode">View Mode</Label>
                    <Tabs
                      value={viewMode}
                      onValueChange={(value) =>
                        updateSettings({ viewMode: value as "single" | "double" | "continuous" })
                      }
                      className="col-span-2"
                    >
                      <TabsList className="grid w-full grid-cols-3">
                        <TabsTrigger value="single">Single</TabsTrigger>
                        <TabsTrigger value="double">Double</TabsTrigger>
                        <TabsTrigger value="continuous">Continuous</TabsTrigger>
                      </TabsList>
                    </Tabs>
                  </div>
                  <div className="grid grid-cols-3 items-center gap-4">
                    <Label htmlFor="zoom">Zoom ({zoomLevel}%)</Label>
                    <div className="col-span-2 flex items-center gap-2">
                      <Slider
                        id="zoom"
                        min={50}
                        max={200}
                        step={10}
                        value={[zoomLevel]}
                        onValueChange={(value) => updateSettings({ zoomLevel: value[0] })}
                      />
                    </div>
                  </div>
                  <div className="grid grid-cols-3 items-center gap-4">
                    <Label htmlFor="fitToWidth">Fit to Width</Label>
                    <div className="col-span-2">
                      <Switch
                        id="fitToWidth"
                        checked={fitToWidth}
                        onCheckedChange={(checked) => updateSettings({ fitToWidth: checked })}
                      />
                    </div>
                  </div>
                  <div className="grid grid-cols-3 items-center gap-4">
                    <Label htmlFor="showPageNumbers">Show Page Numbers</Label>
                    <div className="col-span-2">
                      <Switch
                        id="showPageNumbers"
                        checked={showPageNumbers}
                        onCheckedChange={(checked) => updateSettings({ showPageNumbers: checked })}
                      />
                    </div>
                  </div>
                  <div className="grid grid-cols-3 items-center gap-4">
                    <Label htmlFor="backgroundColor">Background</Label>
                    <div className="col-span-2 flex items-center gap-2">
                      <Input
                        id="backgroundColor"
                        type="color"
                        value={backgroundColor}
                        onChange={(e) => updateSettings({ backgroundColor: e.target.value })}
                        className="w-10 h-10 p-1"
                      />
                      <div
                        className="w-6 h-6 rounded-full border cursor-pointer"
                        style={{ backgroundColor: "#ffffff" }}
                        onClick={() => updateSettings({ backgroundColor: "#ffffff" })}
                      />
                      <div
                        className="w-6 h-6 rounded-full border cursor-pointer"
                        style={{ backgroundColor: "#f5f5f5" }}
                        onClick={() => updateSettings({ backgroundColor: "#f5f5f5" })}
                      />
                      <div
                        className="w-6 h-6 rounded-full border cursor-pointer"
                        style={{ backgroundColor: "#1a1a1a" }}
                        onClick={() => updateSettings({ backgroundColor: "#1a1a1a" })}
                      />
                      <div
                        className="w-6 h-6 rounded-full border cursor-pointer"
                        style={{ backgroundColor: "#000000" }}
                        onClick={() => updateSettings({ backgroundColor: "#000000" })}
                      />
                    </div>
                  </div>
                  <Button variant="outline" onClick={resetSettings}>
                    Reset to Defaults
                  </Button>
                </div>
              </div>
            </PopoverContent>
          </Popover>
          <Button variant="ghost" size="icon" onClick={toggleFullscreen}>
            {isFullscreen ? <Minimize2 className="h-4 w-4" /> : <Maximize2 className="h-4 w-4" />}
            <span className="sr-only">{isFullscreen ? "Exit Fullscreen" : "Enter Fullscreen"}</span>
          </Button>
          <Button variant="ghost" size="icon" onClick={toggleControls}>
            <X className="h-4 w-4" />
            <span className="sr-only">Hide Controls</span>
          </Button>
        </div>
      </div>

      {/* Bottom bar */}
      <div className="absolute bottom-0 left-0 right-0 bg-background/90 backdrop-blur-sm p-2 flex items-center justify-between pointer-events-auto border-t border-primary/20 dark:bg-gradient-to-r dark:from-primary/5 dark:to-accent/10">
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="sm" onClick={prevPage} disabled={pageNumber <= 1}>
            {direction === "ltr" ? <ChevronLeft className="h-4 w-4 mr-1" /> : <ChevronRight className="h-4 w-4 mr-1" />}
            Previous
          </Button>
          <Button variant="ghost" size="sm" onClick={nextPage} disabled={pageNumber >= totalPages}>
            Next
            {direction === "ltr" ? <ChevronRight className="h-4 w-4 ml-1" /> : <ChevronLeft className="h-4 w-4 ml-1" />}
          </Button>
        </div>

        <form onSubmit={handlePageInputSubmit} className="flex items-center gap-2">
          <Input
            type="text"
            value={pageInput}
            onChange={handlePageInputChange}
            className="w-16 h-8 text-center"
            aria-label="Page number"
          />
          <span className="text-sm text-muted-foreground">/ {totalPages}</span>
        </form>
      </div>

      {/* Left/Right navigation areas */}
      <div
        className={`absolute top-[40px] bottom-[40px] ${
          direction === "ltr" ? "left-0" : "right-0"
        } w-1/4 pointer-events-auto`}
        onClick={prevPage}
      />
      <div
        className={`absolute top-[40px] bottom-[40px] ${
          direction === "ltr" ? "right-0" : "left-0"
        } w-1/4 pointer-events-auto`}
        onClick={nextPage}
      />
    </div>
  )
}
