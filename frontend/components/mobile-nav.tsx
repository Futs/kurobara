"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { LogOut, Menu, User } from "lucide-react"
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetFooter,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet"
import { useAuth } from "@/hooks/use-auth"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Separator } from "@/components/ui/separator"

export function MobileNav() {
  const pathname = usePathname()
  const { user, isAuthenticated, logout } = useAuth()

  return (
    <Sheet>
      <SheetTrigger asChild>
        <Button variant="ghost" size="icon" className="md:hidden">
          <Menu className="h-5 w-5" />
          <span className="sr-only">Toggle menu</span>
        </Button>
      </SheetTrigger>
      <SheetContent side="right">
        <SheetHeader>
          <SheetTitle>Kurobara</SheetTitle>
          <SheetDescription>Manga management made easy</SheetDescription>
        </SheetHeader>

        {isAuthenticated && user && (
          <div className="my-4 flex items-center gap-4">
            <Avatar>
              <AvatarImage src={user.avatar || ""} alt={user.username} />
              <AvatarFallback>{user.username.substring(0, 2).toUpperCase()}</AvatarFallback>
            </Avatar>
            <div>
              <p className="font-medium">{user.username}</p>
              <p className="text-xs text-muted-foreground">{user.email}</p>
            </div>
          </div>
        )}

        <nav className="flex flex-col gap-4 mt-8">
          <Link
            href="/"
            className={cn(
              "text-lg font-medium transition-colors hover:text-primary",
              pathname === "/" ? "text-primary" : "text-muted-foreground",
            )}
          >
            Dashboard
          </Link>
          <Link
            href="/collection"
            className={cn(
              "text-lg font-medium transition-colors hover:text-primary",
              pathname === "/collection" || pathname?.startsWith("/collection/")
                ? "text-primary"
                : "text-muted-foreground",
            )}
          >
            Collection
          </Link>
          <Link
            href="/reading"
            className={cn(
              "text-lg font-medium transition-colors hover:text-primary",
              pathname === "/reading" || pathname?.startsWith("/reading/") ? "text-primary" : "text-muted-foreground",
            )}
          >
            Reading
          </Link>
          <Link
            href="/discover"
            className={cn(
              "text-lg font-medium transition-colors hover:text-primary",
              pathname === "/discover" ? "text-primary" : "text-muted-foreground",
            )}
          >
            Discover
          </Link>

          {isAuthenticated ? (
            <>
              <Separator className="my-2" />
              <Link
                href="/profile"
                className={cn(
                  "flex items-center text-lg font-medium transition-colors hover:text-primary",
                  pathname === "/profile" ? "text-primary" : "text-muted-foreground",
                )}
              >
                <User className="mr-2 h-4 w-4" />
                Profile
              </Link>
            </>
          ) : (
            <>
              <Separator className="my-2" />
              <div className="flex flex-col gap-2">
                <Button asChild>
                  <Link href="/login">Sign In</Link>
                </Button>
                <Button asChild variant="outline">
                  <Link href="/register">Sign Up</Link>
                </Button>
              </div>
            </>
          )}
        </nav>

        {isAuthenticated && (
          <SheetFooter className="mt-auto">
            <Button
              variant="destructive"
              className="w-full"
              onClick={() => {
                logout()
              }}
            >
              <LogOut className="mr-2 h-4 w-4" />
              Log out
            </Button>
          </SheetFooter>
        )}
      </SheetContent>
    </Sheet>
  )
}
