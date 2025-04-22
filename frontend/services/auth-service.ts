import { get, post, put } from "./api"
import type { AuthResponse, LoginCredentials, RegisterCredentials, User } from "@/types/auth"

export const AuthService = {
  login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
    return post<AuthResponse>("/auth/login", credentials)
  },

  register: async (credentials: RegisterCredentials): Promise<AuthResponse> => {
    return post<AuthResponse>("/auth/register", credentials)
  },

  logout: async (): Promise<void> => {
    return post<void>("/auth/logout")
  },

  getCurrentUser: async (): Promise<User> => {
    return get<User>("/auth/me")
  },

  updateProfile: async (data: Partial<User>): Promise<User> => {
    return put<User>("/auth/profile", data)
  },

  changePassword: async (data: { currentPassword: string; newPassword: string }): Promise<void> => {
    return post<void>("/auth/change-password", data)
  },

  requestPasswordReset: async (email: string): Promise<void> => {
    return post<void>("/auth/forgot-password", { email })
  },

  resetPassword: async (data: { token: string; password: string }): Promise<void> => {
    return post<void>("/auth/reset-password", data)
  },
}
