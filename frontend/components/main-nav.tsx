"use client"

import type React from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { BookOpen, LogOut, User } from "lucide-react"
import { cn } from "@/lib/utils"
import { useAuth } from "@/hooks/use-auth"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { ThemeToggle } from "@/components/theme-toggle"

export function MainNav({ className, ...props }: React.HTMLAttributes<HTMLElement>) {
  const pathname = usePathname()
  const { user, isAuthenticated, logout } = useAuth()

  return (
    <div className="mr-4 flex">
      <Link href="/" className="mr-6 flex items-center space-x-2">
        <BookOpen className="h-6 w-6" />
        <span className="hidden font-bold sm:inline-block">Kurobara</span>
      </Link>
      <nav className={cn("flex items-center space-x-4 lg:space-x-6", className)} {...props}>
        <Link
          href="/"
          className={cn(
            "text-sm font-medium transition-colors hover:text-primary",
            pathname === "/" ? "text-primary font-semibold" : "text-muted-foreground",
          )}
        >
          Dashboard
        </Link>
        <Link
          href="/collection"
          className={cn(
            "text-sm font-medium transition-colors hover:text-primary",
            pathname === "/collection" || pathname?.startsWith("/collection/")
              ? "text-primary font-semibold"
              : "text-muted-foreground",
          )}
        >
          Collection
        </Link>
        <Link
          href="/reading"
          className={cn(
            "text-sm font-medium transition-colors hover:text-primary",
            pathname === "/reading" || pathname?.startsWith("/reading/")
              ? "text-primary font-semibold"
              : "text-muted-foreground",
          )}
        >
          Reading
        </Link>
        <Link
          href="/discover"
          className={cn(
            "text-sm font-medium transition-colors hover:text-primary",
            pathname === "/discover" ? "text-primary font-semibold" : "text-muted-foreground",
          )}
        >
          Discover
        </Link>
      </nav>
      <div className="ml-auto flex items-center gap-2">
        <ThemeToggle />
        {isAuthenticated ? (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="relative h-8 w-8 rounded-full">
                <Avatar className="h-8 w-8">
                  <AvatarImage src={user?.avatar || ""} alt={user?.username || ""} />
                  <AvatarFallback>{user?.username?.substring(0, 2).toUpperCase() || "U"}</AvatarFallback>
                </Avatar>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="w-56" align="end" forceMount>
              <div className="flex items-center justify-start gap-2 p-2">
                <div className="flex flex-col space-y-1 leading-none">
                  <p className="font-medium">{user?.username}</p>
                  <p className="text-xs text-muted-foreground">{user?.email}</p>
                </div>
              </div>
              <DropdownMenuSeparator />
              <DropdownMenuItem asChild>
                <Link href="/profile" className="cursor-pointer">
                  <User className="mr-2 h-4 w-4" />
                  <span>Profile</span>
                </Link>
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem className="cursor-pointer text-red-600 focus:text-red-600" onSelect={() => logout()}>
                <LogOut className="mr-2 h-4 w-4" />
                <span>Log out</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        ) : (
          <div className="hidden md:flex md:items-center md:gap-2">
            <Button variant="ghost" asChild>
              <Link href="/login">Sign In</Link>
            </Button>
            <Button asChild>
              <Link href="/register">Sign Up</Link>
            </Button>
          </div>
        )}
      </div>
    </div>
  )
}
