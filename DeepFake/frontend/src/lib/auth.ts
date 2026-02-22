import { User } from "@/types";

const TOKEN_KEY = "auth_token";
const USER_KEY = "user_data";

export const authService = {
  // Store authentication data
  setAuth(token: string, user: User): void {
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  },

  // Get stored token
  getToken(): string | null {
    if (typeof window === "undefined") return null;
    return localStorage.getItem(TOKEN_KEY);
  },

  // Get stored user
  getUser(): User | null {
    if (typeof window === "undefined") return null;
    const userData = localStorage.getItem(USER_KEY);
    if (!userData) return null;
    try {
      return JSON.parse(userData);
    } catch {
      return null;
    }
  },

  // Check if user is authenticated
  isAuthenticated(): boolean {
    return !!this.getToken();
  },

  // Clear authentication data
  logout(): void {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  },

  // Initialize auth state (check if token exists)
  initAuth(): { isAuthenticated: boolean; user: User | null } {
    const token = this.getToken();
    const user = this.getUser();
    return {
      isAuthenticated: !!token,
      user,
    };
  },
};
