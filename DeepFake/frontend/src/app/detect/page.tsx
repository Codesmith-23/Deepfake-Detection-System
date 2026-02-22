"use client";

import React, { useState } from "react";
import {
  AlertCircle,
  Loader2,
  Play,
  RotateCcw,
  FileAudio,
  FileVideo,
} from "lucide-react";
import { useDetection } from "@/hooks/useDetection";
import { detectionAPI } from "@/lib/api";
import DetectionResults from "@/components/DetectionResults";
import withAuth from "@/lib/withAuth";

import VideoUpload from "@/components/VideoUpload";
import Button from "@/components/ui/Button";
import ProgressBar from "@/components/ui/ProgressBar";

function DetectPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const { isAnalyzing, uploadProgress, result, error, analyzeVideo, reset } =
    useDetection();

  // 🔍 DEBUG: Log the result when it changes
  React.useEffect(() => {
    if (result) {
      console.log("📦 RESULT IN DETECT PAGE:", result);
      console.log("🎥 Video Analysis:", result.video_analysis);
      console.log("🎤 Audio Analysis:", result.audio_analysis);
    }
  }, [result]);

  const handleFileSelect = (file: File) => {
    setSelectedFile(file);
  };

  const handleFileRemove = () => {
    setSelectedFile(null);
    reset();
  };

  const handleAnalyze = () => {
    if (selectedFile) {
      analyzeVideo(selectedFile);
    }
  };

  const handleAnalyzeAnother = () => {
    setSelectedFile(null);
    reset();
  };

  const getProgressStageMessage = () => {
    switch (uploadProgress.stage) {
      case "uploading":
        return "Uploading media to server...";
      case "processing":
        return uploadProgress.message || "Processing media streams...";
      case "analyzing":
        return "Analyzing for synthetic patterns...";
      case "complete":
        return "Analysis complete!";
      default:
        return "Preparing...";
    }
  };

  const getProgressVariant = () => {
    if (error) return "error";
    if (uploadProgress.stage === "complete") return "success";
    return "default";
  };

  // ✅ SAFE DATA EXTRACTION WITH FALLBACKS
  const isDeepfake = result?.result === "deepfake";
  const finalConfidence = Number(result?.confidence || 0);

  // Video data - handle both nested and flat structure
  const videoAnalysis = result?.video_analysis || {};
  const videoLabel = videoAnalysis?.label || result?.videoLabel || "unknown";
  const videoConf = Number(
    videoAnalysis?.conf ||
      videoAnalysis?.confidence ||
      result?.videoConfidence ||
      0,
  );
  const isVideoFake = videoLabel === "deepfake";

  // Audio data - handle both nested and flat structure
  const audioAnalysis = result?.audio_analysis || {};
  const audioLabel = audioAnalysis?.label || result?.audioLabel || "unknown";
  const audioConf = Number(
    audioAnalysis?.conf ||
      audioAnalysis?.confidence ||
      result?.audioConfidence ||
      0,
  );
  const isAudioFake = audioLabel === "fake";
  const isAudioUnavailable =
    audioLabel === "Not Detected" ||
    audioLabel === "unavailable" ||
    audioLabel === "unknown";

  // Evidence arrays - safe access
  const flaggedFrames = result?.flaggedFrames || [];
  const audioSegments = result?.audio_segments || audioAnalysis?.segments || [];

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white mb-4">
            Multimodal Deepfake Detection
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
            Upload video or audio files. Our system analyzes both
            <strong> Visual</strong> and <strong> Auditory</strong> channels to
            detect manipulation.
          </p>
        </div>

        {/* Main Content */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
          {!result ? (
            // ================= UPLOAD & PROGRESS STATE =================
            <div className="p-8">
              {/* Upload Section */}
              <div className="mb-8">
                <VideoUpload
                  onFileSelect={handleFileSelect}
                  selectedFile={selectedFile}
                  onFileRemove={handleFileRemove}
                  disabled={isAnalyzing}
                />
              </div>

              {/* Analysis Controls */}
              {selectedFile && !isAnalyzing && (
                <div className="text-center">
                  <Button onClick={handleAnalyze} size="lg" className="px-8">
                    <Play size={20} />
                    Start Analysis
                  </Button>
                </div>
              )}

              {/* Progress Section */}
              {isAnalyzing && (
                <div className="space-y-6">
                  <div className="text-center">
                    <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-100 dark:bg-primary-900/20 rounded-full mb-4">
                      <Loader2 className="w-8 h-8 text-primary-600 animate-spin" />
                    </div>
                    <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                      Analyzing Media
                    </h3>
                    <p className="text-gray-600 dark:text-gray-400">
                      {getProgressStageMessage()}
                    </p>
                  </div>

                  <ProgressBar
                    progress={uploadProgress.progress}
                    variant={getProgressVariant()}
                    className="max-w-md mx-auto"
                  />
                </div>
              )}

              {/* Error State */}
              {error && (
                <div className="bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-800 rounded-lg p-6 mt-6">
                  <div className="flex items-center space-x-3">
                    <AlertCircle className="w-6 h-6 text-red-600 flex-shrink-0" />
                    <div>
                      <h3 className="text-lg font-medium text-red-800 dark:text-red-200">
                        Analysis Failed
                      </h3>
                      <p className="text-red-700 dark:text-red-300 mt-1">
                        {error}
                      </p>
                      <div className="mt-4">
                        <Button
                          variant="outline"
                          onClick={handleAnalyzeAnother}
                          className="border-red-300 text-red-700"
                        >
                          <RotateCcw size={16} /> Try Again
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ) : (
            // ================= RESULTS STATE =================
            <div className=" p-6 md:p-8 animate-fade-in ">
              <DetectionResults
                result={result}
                onAnalyzeAnother={handleAnalyzeAnother}
              />
            </div>
          )}
        </div>

        {/* Footer Info Cards */}
        {!result && (
          <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
                Supported Formats
              </h3>
              <ul className="space-y-2 text-gray-600 dark:text-gray-400 text-sm">
                <li className="flex items-center gap-2">
                  <div className="w-1.5 h-1.5 bg-primary-600 rounded-full" />
                  MP4, AVI, MOV, MKV (Video)
                </li>
                <li className="flex items-center gap-2">
                  <div className="w-1.5 h-1.5 bg-primary-600 rounded-full" />
                  MP3, WAV, FLAC, M4A (Audio)
                </li>
              </ul>
            </div>
            <div className="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
                Analysis Features
              </h3>
              <ul className="space-y-2 text-gray-600 dark:text-gray-400 text-sm">
                <li className="flex items-center gap-2">
                  <div className="w-1.5 h-1.5 bg-primary-600 rounded-full" />
                  Facial manipulation detection
                </li>
                <li className="flex items-center gap-2">
                  <div className="w-1.5 h-1.5 bg-primary-600 rounded-full" />
                  Voice synthesis detection
                </li>
              </ul>
            </div>
            <div className="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
                Processing Time
              </h3>
              <ul className="space-y-2 text-gray-600 dark:text-gray-400 text-sm">
                <li className="flex items-center gap-2">
                  <div className="w-1.5 h-1.5 bg-primary-600 rounded-full" />
                  Audio: ~30-60 seconds
                </li>
                <li className="flex items-center gap-2">
                  <div className="w-1.5 h-1.5 bg-primary-600 rounded-full" />
                  Video: ~1-3 minutes
                </li>
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default withAuth(DetectPage);
