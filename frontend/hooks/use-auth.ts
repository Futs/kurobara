"use client"

import type React from "react"

import { useState, useEffect, createContext, useContext } from "react"
import { useRouter, usePathname } from "next/navigation"
import { AuthService } from "@/services/auth-service"
import type { AuthState, LoginCredentials, RegisterCredentials, User } from "@/types/auth"

interface AuthContextType extends AuthState {
  login: (credentials: LoginCredentials) => Promise<void>
  register: (credentials: RegisterCredentials) => Promise<void>
  logout: () => Promise<void>
  updateProfile: (data: Partial<User>) => Promise<void>
  clearError: () => void
}

const initialState: AuthState = {
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: true,
  error: null,
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<AuthState>(initialState)
  const router = useRouter()
  const pathname = usePathname()

  // Initialize auth state from localStorage
  useEffect(() => {
    const initializeAuth = async () => {
      const token = localStorage.getItem("auth_token")
      if (token) {
        try {
          const user = await AuthService.getCurrentUser()
          setState({
            user,
            token,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          })
        } catch (error) {
          // Token is invalid or expired
          localStorage.removeItem("auth_token")
          setState({
            ...initialState,
            isLoading: false,
          })
        }
      } else {
        setState({
          ...initialState,
          isLoading: false,
        })
      }
    }

    initializeAuth()
  }, [])

  // Redirect to login if not authenticated and trying to access protected routes
  useEffect(() => {
    const protectedRoutes = ["/collection", "/reading", "/manga/add"]
    const isProtectedRoute = protectedRoutes.some((route) => pathname?.startsWith(route))
    const authRoutes = ["/login", "/register"]
    const isAuthRoute = authRoutes.some((route) => pathname === route)

    if (!state.isLoading) {
      if (!state.isAuthenticated && isProtectedRoute) {
        router.push(`/login?redirect=${encodeURIComponent(pathname || "/")}`)
      } else if (state.isAuthenticated && isAuthRoute) {
        router.push("/")
      }
    }
  }, [state.isAuthenticated, state.isLoading, pathname, router])

  const login = async (credentials: LoginCredentials) => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }))
    try {
      const response = await AuthService.login(credentials)
      localStorage.setItem("auth_token", response.token)
      setState({
        user: response.user,
        token: response.token,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      })
    } catch (error: any) {
      setState((prev) => ({
        ...prev,
        isLoading: false,
        error: error.message || "Failed to login",
      }))
      throw error
    }
  }

  const register = async (credentials: RegisterCredentials) => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }))
    try {
      const response = await AuthService.register(credentials)
      localStorage.setItem("auth_token", response.token)
      setState({
        user: response.user,
        token: response.token,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      })
    } catch (error: any) {
      setState((prev) => ({
        ...prev,
        isLoading: false,
        error: error.message || "Failed to register",
      }))
      throw error
    }
  }

  const logout = async () => {
    setState((prev) => ({ ...prev, isLoading: true }))
    try {
      await AuthService.logout()
    } catch (error) {
      console.error("Error during logout:", error)
    } finally {
      localStorage.removeItem("auth_token")
      setState({
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
      })
      router.push("/login")
    }
  }

  const updateProfile = async (data: Partial<User>) => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }))
    try {
      const updatedUser = await AuthService.updateProfile(data)
      setState((prev) => ({
        ...prev,
        user: updatedUser,
        isLoading: false,
      }))
    } catch (error: any) {
      setState((prev) => ({
        ...prev,
        isLoading: false,
        error: error.message || "Failed to update profile",
      }))
      throw error
    }
  }

  const clearError = () => {
    setState((prev) => ({ ...prev, error: null }))
  }

  const value = {
    ...state,
    login,
    register,
    logout,
    updateProfile,
    clearError,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}
