'use client';

import React, { useState, useCallback } from 'react';
import { useDropzone, FileRejection } from 'react-dropzone';
import { Upload, File, X, Play, Music } from 'lucide-react'; // Added Music icon
import { cn, formatFileSize } from '@/lib/utils';
import Button from '@/components/ui/Button';

interface VideoUploadProps {
  onFileSelect: (file: File) => void;
  disabled?: boolean;
  selectedFile?: File | null;
  onFileRemove?: () => void;
}

const VideoUpload: React.FC<VideoUploadProps> = ({
  onFileSelect,
  disabled = false,
  selectedFile,
  onFileRemove,
}) => {
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback((acceptedFiles: File[], rejectedFiles: FileRejection[]) => {
    setError(null);
    
    if (rejectedFiles.length > 0) {
      const firstRejection = rejectedFiles[0];
      if (firstRejection.errors[0]?.code === 'file-too-large') {
        setError('File is too large. Maximum size is 500MB.');
      } else if (firstRejection.errors[0]?.code === 'file-invalid-type') {
        setError('Invalid file type. Please select a Video (MP4, AVI, MOV) or Audio (WAV, MP3) file.');
      } else {
        setError('File upload failed. Please try again.');
      }
      return;
    }

    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0];
      // Note: You might need to relax your 'validateVideoFile' utility function if it strictly checks for video mime types
      // For now, we trust the dropzone 'accept' prop to filter correct files.
      onFileSelect(file);
    }
  }, [onFileSelect]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      // 🎥 Video Formats
      'video/mp4': ['.mp4'],
      'video/avi': ['.avi'],
      'video/quicktime': ['.mov'],
      'video/x-msvideo': ['.avi'],
      'video/x-matroska': ['.mkv'],
      
      // 🎵 Audio Formats (Matches your Backend)
      'audio/mpeg': ['.mp3'],
      'audio/wav': ['.wav'],
      'audio/x-wav': ['.wav'], 
      'audio/flac': ['.flac'],
      'audio/mp4': ['.m4a'],
      'audio/x-m4a': ['.m4a']
    },
    maxFiles: 1,
    maxSize: 500 * 1024 * 1024, // 500MB
    disabled,
  });

  const handleRemoveFile = () => {
    setError(null);
    onFileRemove?.();
  };

  const isAudio = selectedFile?.type.startsWith('audio');

  if (selectedFile) {
    return (
      <div className="w-full p-6 border-2 border-gray-200 dark:border-gray-700 rounded-xl bg-white dark:bg-gray-800">
        <div className="flex items-center space-x-4">
          <div className="flex-shrink-0">
            <div className="w-12 h-12 bg-primary-100 dark:bg-primary-900/20 rounded-lg flex items-center justify-center">
              {isAudio ? (
                <Music className="w-6 h-6 text-primary-600" />
              ) : (
                <File className="w-6 h-6 text-primary-600" />
              )}
            </div>
          </div>
          
          <div className="flex-1 min-w-0">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white truncate">
              {selectedFile.name}
            </h3>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              {formatFileSize(selectedFile.size)} • {isAudio ? 'Audio File' : 'Video File'}
            </p>
          </div>
          
          <div className="flex items-center space-x-2">
            <div className="w-16 h-12 bg-gray-100 dark:bg-gray-700 rounded-lg flex items-center justify-center">
              {isAudio ? (
                 <Music className="w-4 h-4 text-gray-500 dark:text-gray-400" />
              ) : (
                 <Play className="w-4 h-4 text-gray-500 dark:text-gray-400" />
              )}
            </div>
            
            <Button
              variant="ghost"
              size="sm"
              onClick={handleRemoveFile}
              disabled={disabled}
              className="text-gray-500 hover:text-red-500"
            >
              <X size={16} />
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full">
      <div
        {...getRootProps()}
        className={cn(
          'w-full p-12 border-2 border-dashed rounded-xl transition-all duration-200 cursor-pointer',
          'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2',
          isDragActive
            ? 'border-primary-400 bg-primary-50 dark:bg-primary-950/20'
            : 'border-gray-300 dark:border-gray-600 hover:border-primary-400 hover:bg-gray-50 dark:hover:bg-gray-800',
          disabled && 'opacity-50 cursor-not-allowed',
          error && 'border-red-300 bg-red-50 dark:bg-red-950/20'
        )}
      >
        <input {...getInputProps()} />
        
        <div className="text-center">
          <Upload 
            className={cn(
              'mx-auto h-12 w-12 mb-4',
              isDragActive ? 'text-primary-600' : 'text-gray-400',
              error && 'text-red-400'
            )} 
          />
          
          <div className="mb-2">
            {isDragActive ? (
              <p className="text-lg font-medium text-primary-600">
                Drop the media file here
              </p>
            ) : (
              <p className="text-lg font-medium text-gray-900 dark:text-white">
                Drag & drop Video or Audio
              </p>
            )}
          </div>
          
          <p className="text-gray-500 dark:text-gray-400 mb-4">
            or click to browse files
          </p>
          
          <div className="flex flex-wrap justify-center gap-2 text-sm text-gray-500 dark:text-gray-400">
            <span className="bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">MP4</span>
            <span className="bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">AVI</span>
            <span className="bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">MOV</span>
            <span className="bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-200 px-2 py-1 rounded">WAV</span>
            <span className="bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-200 px-2 py-1 rounded">MP3</span>
          </div>
          
          <p className="text-xs text-gray-400 dark:text-gray-500 mt-2">
            Maximum file size: 500MB
          </p>
        </div>
      </div>
      
      {error && (
        <div className="mt-3 p-3 bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-800 rounded-lg">
          <p className="text-sm text-red-600 dark:text-red-400">
            {error}
          </p>
        </div>
      )}
    </div>
  );
};

export default VideoUpload;