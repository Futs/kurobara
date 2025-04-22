const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

export class ApiError extends Error {
  status: number
  data?: any

  constructor(message: string, status: number, data?: any) {
    super(message)
    this.name = "ApiError"
    this.status = status
    this.data = data
  }
}

// Helper to get the auth token from localStorage
const getAuthToken = (): string | null => {
  if (typeof window !== "undefined") {
    return localStorage.getItem("auth_token")
  }
  return null
}

export async function fetchApi<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`
  const token = getAuthToken()

  const headers = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  }

  const response = await fetch(url, {
    ...options,
    headers,
  })

  // For 204 No Content responses
  if (response.status === 204) {
    return {} as T
  }

  // For all other responses, try to parse JSON
  let data
  try {
    data = await response.json()
  } catch (error) {
    if (!response.ok) {
      throw new ApiError("An error occurred while fetching data", response.status)
    }
    return {} as T
  }

  if (!response.ok) {
    // Handle authentication errors
    if (response.status === 401) {
      // Clear token if it's invalid or expired
      if (typeof window !== "undefined") {
        localStorage.removeItem("auth_token")
      }
      // You could also redirect to login page here
    }
    throw new ApiError(data.message || "An error occurred while fetching data", response.status, data)
  }

  return data as T
}

export async function get<T>(
  endpoint: string,
  params?: Record<string, string | number | boolean | undefined>,
): Promise<T> {
  const queryParams = params
    ? "?" +
      new URLSearchParams(
        Object.entries(params)
          .filter(([_, value]) => value !== undefined)
          .map(([key, value]) => [key, String(value)]),
      ).toString()
    : ""

  return fetchApi<T>(`${endpoint}${queryParams}`, {
    method: "GET",
  })
}

export async function post<T, D = any>(endpoint: string, data?: D): Promise<T> {
  return fetchApi<T>(endpoint, {
    method: "POST",
    body: data ? JSON.stringify(data) : undefined,
  })
}

export async function put<T, D = any>(endpoint: string, data?: D): Promise<T> {
  return fetchApi<T>(endpoint, {
    method: "PUT",
    body: data ? JSON.stringify(data) : undefined,
  })
}

export async function patch<T, D = any>(endpoint: string, data?: D): Promise<T> {
  return fetchApi<T>(endpoint, {
    method: "PATCH",
    body: data ? JSON.stringify(data) : undefined,
  })
}

export async function del<T>(endpoint: string): Promise<T> {
  return fetchApi<T>(endpoint, {
    method: "DELETE",
  })
}

export function withErrorHandling<T extends (...args: any[]) => Promise<any>>(
  fn: T,
): (...args: Parameters<T>) => Promise<Awaited<ReturnType<T>>> {
  return async (...args: Parameters<T>) => {
    try {
      return await fn(...args)
    } catch (error) {
      if (error instanceof ApiError) {
        console.error(`API Error (${error.status}):`, error.message)
        // You could add additional error handling here, like showing a toast notification
      } else {
        console.error("Unexpected error:", error)
      }
      throw error
    }
  }
}
