import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

export function formatDuration(seconds: number): string {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.floor(seconds % 60);
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
}

export function formatDate(dateInput: Date | string): string {
  const date = typeof dateInput === 'string' ? new Date(dateInput) : dateInput;
  if (isNaN(date.getTime())) {
    console.warn('Invalid date value:', dateInput);
    return 'Invalid Date';
  }

  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
}


export function isValidVideoFile(file: File): boolean {
  const acceptedTypes = ['video/mp4', 'video/avi', 'video/quicktime', 'video/x-msvideo'];
  return acceptedTypes.includes(file.type);
}

export function getVideoFileExtension(filename: string): string {
  return filename.split('.').pop()?.toLowerCase() || '';
}

export function validateVideoFile(file: File): { valid: boolean; error?: string } {
  const maxSize = 500 * 1024 * 1024; // 500MB
  const acceptedExtensions = ['mp4', 'avi', 'mov'];
  
  if (!isValidVideoFile(file)) {
    return {
      valid: false,
      error: `Invalid file type. Please select a video file (${acceptedExtensions.join(', ')})`,
    };
  }

  if (file.size > maxSize) {
    return {
      valid: false,
      error: `File size too large. Maximum size is ${formatFileSize(maxSize)}`,
    };
  }

  const extension = getVideoFileExtension(file.name);
  if (!acceptedExtensions.includes(extension)) {
    return {
      valid: false,
      error: `Unsupported file extension. Supported formats: ${acceptedExtensions.join(', ')}`,
    };
  }

  return { valid: true };
}

export function getConfidenceColor(confidence: number): string {
  if (confidence >= 80) return 'text-danger-600';
  if (confidence >= 60) return 'text-accent-600';
  if (confidence >= 40) return 'text-yellow-600';
  return 'text-success-600';
}

export function getConfidenceLabel(result: 'deepfake' | 'real', confidence: number): string {
  if (result === 'deepfake') {
    if (confidence >= 90) return 'Highly Likely Deepfake';
    if (confidence >= 70) return 'Likely Deepfake';
    if (confidence >= 50) return 'Possibly Deepfake';
    return 'Uncertain - Lean Deepfake';
  } else {
    if (confidence >= 90) return 'Highly Likely Real';
    if (confidence >= 70) return 'Likely Real';
    if (confidence >= 50) return 'Possibly Real';
    return 'Uncertain - Lean Real';
  }
}

export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout;
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}

export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean;
  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
}
