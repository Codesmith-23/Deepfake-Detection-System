import { useState, useCallback } from "react";
import { DetectionResult, UploadProgress } from "@/types";
import { detectionAPI } from "@/lib/api";

// Simple ID generator
const generateId = () =>
  `analysis_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

export function useDetection() {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<UploadProgress>({
    progress: 0,
    stage: "uploading",
  });
  const [result, setResult] = useState<DetectionResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const analyzeVideo = useCallback(async (file: File) => {
    setIsAnalyzing(true);
    setError(null);
    setResult(null);
    setUploadProgress({
      progress: 0,
      stage: "uploading",
      message: "Uploading video...",
    });

    try {
      const response = await detectionAPI.analyzeVideo(
        file,
        (progress) => {
          setUploadProgress({
            progress,
            stage: "uploading",
            message: `Uploading video... ${progress}%`,
          });
        },
        (stage, progress) => {
          setUploadProgress({
            progress,
            stage: "processing",
            message: stage,
          });
        },
      );

      // ✅ FIX: Include ALL fields from the backend response
      const detectionResult: DetectionResult = {
        id: generateId(),
        result: response.result,
        confidence: response.confidence,
        timestamp: new Date().toISOString(),
        filename: file.name,
        fileSize: file.size,

        // ✅ CRITICAL: Include nested analysis objects
        video_analysis: response.video_analysis,
        audio_analysis: response.audio_analysis,

        // ✅ Evidence arrays with proper URL formatting
        flaggedFrames:
          response.flaggedFrames?.map((frame: any) => {
            const url = typeof frame === "string" ? frame : frame.url || frame;
            // Ensure URL starts with http://
            const fullUrl = url.startsWith("http")
              ? url
              : `http://127.0.0.1:5000${url}`;
            console.log(`📸 Frame URL: ${url} -> ${fullUrl}`);
            return {
              url: fullUrl,
              timestamp: frame.timestamp || 0,
              confidence: frame.confidence || 0,
            };
          }) || [],

        // ✅ Audio segments
        audio_segments:
          response.audio_segments || response.audio_analysis?.segments || [],

        processingTime: response.processingTime,
      };

      console.log("✅ DETECTION RESULT CREATED:", detectionResult);
      setResult(detectionResult);
      setUploadProgress({
        progress: 100,
        stage: "complete",
        message: "Analysis complete!",
      });
    } catch (err: any) {
      console.error("❌ DETECTION ERROR:", err);
      setError(err.message || "An error occurred during analysis");
    } finally {
      setIsAnalyzing(false);
    }
  }, []);

  const reset = useCallback(() => {
    setIsAnalyzing(false);
    setUploadProgress({ progress: 0, stage: "uploading" });
    setResult(null);
    setError(null);
  }, []);

  return {
    isAnalyzing,
    uploadProgress,
    result,
    error,
    analyzeVideo,
    reset,
  };
}
