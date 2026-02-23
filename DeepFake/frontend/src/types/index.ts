// ==========================================
// 1. ANALYSIS & RESULT TYPES
// ==========================================

export interface AudioSegment {
  start: number;
  end: number;
  confidence: number;
  label: string;
}

export interface AudioAnalysis {
  label?: string;
  confidence?: number;
  conf?: number;
  segments?: AudioSegment[];
}

export interface VideoAnalysis {
  label?: string;
  confidence?: number;
  conf?: number;
}

export interface MatchedEntity {
  entity_id: string;
  name: string;
  type: "creator" | "celebrity" | "brand_character";
  confidence: number;
}

export interface CopyrightViolation {
  violation_detected: boolean;
  matched_entity?: MatchedEntity;
  license_status?: "authorized" | "unauthorized" | "unknown";
  violation_type?:
    | "unauthorized_likeness"
    | "unknown_rights"
    | "synthetic_but_unregistered";
  reason?: string;
}

export interface DetectionResult {
  id?: string;
  filename?: string;
  fileSize?: number;
  result?: "deepfake" | "authentic";
  confidence?: number;
  timestamp?: string | Date;
  processingTime?: number;

  // New Fields for Split Analysis
  video_analysis?: VideoAnalysis;
  audio_analysis?: AudioAnalysis;

  // Additional properties that might come from backend
  type?: string;
  videoLabel?: string;
  audioLabel?: string;
  videoConfidence?: number;
  audioConfidence?: number;

  // Evidence Arrays
  flaggedFrames?: Array<{
    url?: string;
    timestamp?: number;
    confidence?: number;
  }>;
  audio_segments?: Array<{
    start?: number;
    end?: number;
    confidence?: number;
    label?: string;
  }>;

  // Copyright violation detection (Phase 3)
  copyright_check?: CopyrightViolation;
}

// ==========================================
// 2. API RESPONSE TYPES
// ==========================================

export interface ApiError {
  code?: string;
  message: string;
  details?: any;
}

export interface ApiResponse<T> {
  success?: boolean;
  data?: T;
  error?: ApiError;
}

// Combine them so API responses have all Detection fields
export interface DetectionApiResponse extends DetectionResult {}

// ==========================================
// 3. COMPONENT & UTILITY TYPES
// ==========================================

export interface BoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
  confidence: number;
}

export interface UploadProgress {
  progress: number;
  stage: "uploading" | "processing" | "analyzing" | "complete";
  message?: string;
}

export interface HistoryEntry {
  id: string;
  analysisID: string;
  file_name: string; // Must match Python's "file_name"
  result: "deepfake" | "authentic" | "real";
  confidence: number;
  timestamp: string;
  file_size: string | number; // Python sends this as text or number
}

export interface ThemeConfig {
  isDark: boolean;
}

// Props
export interface ButtonProps {
  variant?: "primary" | "secondary" | "outline" | "ghost" | "danger";
  size?: "sm" | "md" | "lg";
  children: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  loading?: boolean;
  className?: string;
  type?: "button" | "submit" | "reset";
}

export interface ProgressBarProps {
  progress: number;
  className?: string;
  showLabel?: boolean;
  variant?: "default" | "success" | "warning" | "error";
}

export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  size?: "sm" | "md" | "lg" | "xl";
}

// ==========================================
// 4. AUTHENTICATION TYPES
// ==========================================

export interface User {
  id: number;
  username: string;
  email: string;
}

export interface AuthResponse {
  message: string;
  token: string;
  user: User;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterCredentials {
  username: string;
  email: string;
  password: string;
}

export interface VerifyResponse {
  valid: boolean;
  user: {
    id: number;
    username: string;
  };
}
