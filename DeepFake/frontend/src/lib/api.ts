import axios, { AxiosProgressEvent } from "axios";
import {
  DetectionApiResponse,
  HistoryEntry,
  ApiError,
  AuthResponse,
  LoginCredentials,
  RegisterCredentials,
  VerifyResponse,
} from "@/types";

// Force IPv4 to prevent 'ECONNREFUSED' errors on Windows
const API_BASE_URL = "http://127.0.0.1:5000";

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 600000, // 5 minutes (for large video uploads)
  headers: {
    "Content-Type": "application/json",
  },
});

// Request Interceptor (Auth)
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("auth_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error),
);

// Response Interceptor (Auth Error Handling)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("auth_token");
      window.location.href = "/";
    }
    return Promise.reject(error);
  },
);

export const apiService = {
  // --- ANALYZE MEDIA (Video or Audio) ---
  async analyzeVideo(
    file: File,
    onUploadProgress?: (progress: number) => void,
    onProcessingStage?: (stage: string, progress: number) => void,
  ): Promise<DetectionApiResponse> {
    const formData = new FormData();
    formData.append("file", file);

    try {
      // ✅ FIX 1: Removed 'ApiResponse' wrapper.
      // We expect raw 'DetectionApiResponse' from the backend.
      const response = await api.post<DetectionApiResponse>(
        "/predict/media",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
          onUploadProgress: (progressEvent: AxiosProgressEvent) => {
            if (progressEvent.total && onUploadProgress) {
              const progress = Math.round(
                (progressEvent.loaded * 100) / progressEvent.total,
              );
              onUploadProgress(progress);
            }
          },
        },
      );

      // UI Simulation (Optional visual feedback)
      if (onProcessingStage) {
        onProcessingStage("Analyzing frames...", 40);
        await new Promise((r) => setTimeout(r, 400));
        onProcessingStage("Detecting anomalies...", 70);
        await new Promise((r) => setTimeout(r, 400));
        onProcessingStage("Finalizing results...", 90);
        await new Promise((r) => setTimeout(r, 400));
      }

      // ✅ FIX 2: Return data directly
      return response.data;
    } catch (error: any) {
      // Safe Error Casting
      const apiError = error.response?.data?.error as ApiError | undefined;
      throw new Error(apiError?.message || error.message || "Analysis failed");
    }
  },

  // --- GET HISTORY ---
  async getHistory(): Promise<HistoryEntry[]> {
    try {
      // ✅ FIX 3: Expect raw array, not wrapped
      const response = await api.post<HistoryEntry[]>("/history", {});
      return response.data;
    } catch (error: any) {
      const apiError = error.response?.data?.error as ApiError | undefined;
      throw new Error(apiError?.message || "Failed to fetch history");
    }
  },

  // --- DELETE HISTORY ---
  // Accepts string or number to be safe
  async deleteHistoryEntry(resultId: string | number): Promise<void> {
    try {
      await api.delete(`/history/delete/${resultId}`);
    } catch (error: any) {
      const apiError = error.response?.data?.error as ApiError | undefined;
      throw new Error(apiError?.message || "Failed to delete history entry");
    }
  },

  // --- REPORT RESULT (Optional Stub) ---
  async reportResult(
    resultId: string,
    type: "false_positive" | "false_negative",
  ): Promise<void> {
    console.log(`Reporting ${type} for ${resultId}`);
    return Promise.resolve();
  },

  // --- AUTHENTICATION ---
  async register(credentials: RegisterCredentials): Promise<AuthResponse> {
    try {
      const response = await api.post<AuthResponse>(
        "/auth/register",
        credentials,
      );
      return response.data;
    } catch (error: any) {
      const apiError = error.response?.data?.error as
        | string
        | ApiError
        | undefined;
      const message =
        typeof apiError === "string"
          ? apiError
          : apiError?.message || "Registration failed";
      throw new Error(message);
    }
  },

  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    try {
      const response = await api.post<AuthResponse>("/auth/login", credentials);
      return response.data;
    } catch (error: any) {
      const apiError = error.response?.data?.error as
        | string
        | ApiError
        | undefined;
      const message =
        typeof apiError === "string"
          ? apiError
          : apiError?.message || "Login failed";
      throw new Error(message);
    }
  },

  async verify(): Promise<VerifyResponse> {
    try {
      const response = await api.get<VerifyResponse>("/auth/verify");
      return response.data;
    } catch (error: any) {
      const apiError = error.response?.data?.error as
        | string
        | ApiError
        | undefined;
      const message =
        typeof apiError === "string"
          ? apiError
          : apiError?.message || "Token verification failed";
      throw new Error(message);
    }
  },
};

export const detectionAPI = apiService;
