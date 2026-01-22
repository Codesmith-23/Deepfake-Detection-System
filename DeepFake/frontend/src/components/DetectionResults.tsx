'use client';

import React, { useState } from 'react';
import { 
  CheckCircle, 
  AlertTriangle, 
  Download, 
  Flag, 
  Image as ImageIcon, 
  Video, 
  Mic, 
  FileText,
  HardDrive,
  Clock,
  Activity
} from 'lucide-react';
import Button from '@/components/ui/Button';
import ProgressBar from '@/components/ui/ProgressBar';
import Modal from '@/components/ui/Modal';
import { cn, formatFileSize, getConfidenceColor, getConfidenceLabel } from '@/lib/utils';
import { DetectionResult } from '@/types';

// 🔧 CONFIGURATION
const BACKEND_URL = "http://127.0.0.1:5000";

interface DetectionResultsProps {
  result: DetectionResult;
  onAnalyzeAnother: () => void;
  onReportResult?: (type: 'false_positive' | 'false_negative') => void;
}

const DetectionResults: React.FC<DetectionResultsProps> = ({
  result,
  onAnalyzeAnother,
  onReportResult,
}) => {
  const [showFramesModal, setShowFramesModal] = useState(false);
  const [showReportModal, setShowReportModal] = useState(false);

  // --- 1. ROBUST DATA EXTRACTION (Fixed TS Errors) ---
  const isDeepfake = result.result === 'deepfake';
  const mainConfidence = Number(result.confidence || 0);
  const confidenceColor = getConfidenceColor(mainConfidence);
  
  const resultForLabel = result.result === 'authentic' ? 'real' : (result.result || 'real');
  const confidenceLabel = getConfidenceLabel(resultForLabel as 'deepfake' | 'real', mainConfidence);

  // 🛡️ TS FIX: Use ({} as any) to prevent "Property does not exist" errors
  const videoAnalysis = result.video_analysis || ({} as any);
  const videoConf = Number(videoAnalysis.conf ?? videoAnalysis.confidence ?? 0);
  const isVideoFake = videoAnalysis.label === 'deepfake' || videoAnalysis.label === 'fake';

  const audioAnalysis = result.audio_analysis || ({} as any);
  const audioConf = Number(audioAnalysis.conf ?? audioAnalysis.confidence ?? 0);
  const isAudioFake = audioAnalysis.label === 'fake';
  const isAudioUnavailable = !audioAnalysis.label || audioAnalysis.label === 'unavailable' || audioAnalysis.label === 'unknown' || audioAnalysis.label === 'Not Detected';

  const audioSegments = result.audio_segments || audioAnalysis.segments || [];
  const flaggedFrames = result.flaggedFrames || [];

  // --- 2. IMAGE URL FIX ---
  const getFrameUrl = (frame: any) => {
    let path = typeof frame === 'string' ? frame : frame?.url;
    if (!path) return "";
    if (path.startsWith('http')) return path; 
    if (path.startsWith('/')) path = path.substring(1);
    return `${BACKEND_URL}/${path}`;
  };


  // --- 3. CLEANUP HANDLER (NEW) ---
  const handleAnalyzeAnother = async () => {
    try {
      console.log("🧹 Triggering frame cleanup...");
      // Tell Backend to wipe all frames immediately
      await fetch(`${BACKEND_URL}/cleanup/frames`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'wipe' }),
      });
      console.log("✨ Frames wiped successfully.");
    } catch (error) {
      console.error("❌ Cleanup failed:", error);
    } finally {
      // Reset the UI (Standard behavior) regardless of cleanup success
      onAnalyzeAnother();
    }
  };


  const handleDownloadReport = () => {
    const reportData = { ...result, exportedAt: new Date().toISOString() };
    const dataStr = JSON.stringify(reportData, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr);
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', `deepfake-analysis-${result.id}.json`);
    linkElement.click();
  };

  return (
    <div className="w-full space-y-6 animate-fade-in">
      
      {/* ============ 1. MAIN VERDICT CARD (Original UI Preserved) ============ */}
      <div className={cn(
        'p-8 rounded-xl border-2 shadow-lg transition-colors duration-300',
        isDeepfake
          ? 'bg-red-50 border-red-200 dark:bg-red-950/20 dark:border-red-800'
          : 'bg-green-50 border-green-200 dark:bg-green-950/20 dark:border-green-800'
      )}>
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-4">
            {isDeepfake ? (
              <div className="p-3 bg-red-100 dark:bg-red-900/50 rounded-full">
                <AlertTriangle className="h-10 w-10 text-red-600 dark:text-red-400" />
              </div>
            ) : (
              <div className="p-3 bg-green-100 dark:bg-green-900/50 rounded-full">
                <CheckCircle className="h-10 w-10 text-green-600 dark:text-green-400" />
              </div>
            )}
            <div>
              <h2 className="text-3xl font-bold text-gray-900 dark:text-white tracking-tight">
                {isDeepfake ? 'Likely Deepfake' : 'Likely Authentic'}
              </h2>
              <p className="text-lg text-gray-600 dark:text-gray-400 mt-1">
                {confidenceLabel}
              </p>
            </div>
          </div>

          <div className="text-right">
            <div className={cn('text-5xl font-black tracking-tighter', confidenceColor)}>
              {mainConfidence.toFixed(2)}%
            </div>
            <p className="text-sm font-bold text-gray-500 dark:text-gray-400 uppercase tracking-widest mt-1">
              Confidence
            </p>
          </div>
        </div>

        <div className="mb-8">
          <ProgressBar
            progress={mainConfidence}
            variant={isDeepfake ? 'error' : 'success'}
            showLabel={false}
            className="h-4 rounded-full"
          />
        </div>

        {/* METADATA GRID */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-sm border-t border-gray-200 dark:border-gray-700 pt-6">
          <div className="flex items-start gap-3">
            <div className="p-2 bg-white dark:bg-gray-800 rounded-lg shadow-sm">
              <FileText className="w-5 h-5 text-gray-500" />
            </div>
            <div>
              <p className="text-gray-500 dark:text-gray-400 font-semibold mb-1">File Name</p>
              <p className="font-medium text-gray-900 dark:text-white truncate max-w-[180px]" title={result.filename}>
                {result.filename}
              </p>
            </div>
          </div>
          
          <div className="flex items-start gap-3">
            <div className="p-2 bg-white dark:bg-gray-800 rounded-lg shadow-sm">
              <HardDrive className="w-5 h-5 text-gray-500" />
            </div>
            <div>
              <p className="text-gray-500 dark:text-gray-400 font-semibold mb-1">File Size</p>
              <p className="font-medium text-gray-900 dark:text-white">
                {result.fileSize ? formatFileSize(result.fileSize) : 'N/A'}
              </p>
            </div>
          </div>

          <div className="flex items-start gap-3">
            <div className="p-2 bg-white dark:bg-gray-800 rounded-lg shadow-sm">
              <Clock className="w-5 h-5 text-gray-500" />
            </div>
            <div>
              <p className="text-gray-500 dark:text-gray-400 font-semibold mb-1">Analysis Time</p>
              <p className="font-medium text-gray-900 dark:text-white">
                {result.processingTime ? `${result.processingTime}s` : '0.0s'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* ============ 2. SIDE-BY-SIDE SPLIT CHANNELS (Fixed Layout) ============ */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-stretch">
        
        {/* --- LEFT: VIDEO CHANNEL (Contains Frames Inside!) --- */}
        <div className={cn(
          'p-6 rounded-xl border-2 transition-all shadow-sm flex flex-col',
          isVideoFake 
            ? 'bg-red-50 border-red-200 dark:bg-red-900/10 dark:border-red-800' 
            : 'bg-white border-gray-200 dark:bg-gray-800 dark:border-gray-700'
        )}>
          <div className="flex justify-between items-center mb-4">
            <div className="flex items-center gap-3">
              <div className={cn("p-2 rounded-lg", isVideoFake ? "bg-red-100 dark:bg-red-900/50" : "bg-blue-100 dark:bg-blue-900/50")}>
                <Video className={cn("w-6 h-6", isVideoFake ? "text-red-600" : "text-blue-600")} />
              </div>
              <h3 className="font-bold text-lg text-gray-900 dark:text-white">Visual Channel</h3>
            </div>
            <span className={cn(
              "px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wide",
              isVideoFake 
                ? "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300" 
                : "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300"
            )}>
              {isVideoFake ? "Manipulated" : "Genuine"}
            </span>
          </div>
          
          <div className="flex items-baseline gap-2 mb-2">
            <span className={cn("text-4xl font-bold", isVideoFake ? "text-red-600" : "text-gray-900 dark:text-white")}>
              {videoConf.toFixed(2)}%
            </span>
            <span className="text-sm font-medium text-gray-500 uppercase">confidence</span>
          </div>
          
          <div className="mb-4">
             <ProgressBar 
                progress={videoConf} 
                variant={isVideoFake ? 'error' : 'success'} 
                showLabel={false} 
                className="h-2"
             />
          </div>

          {/*  FRAMES INSIDE THE VIDEO CARD (Only if Fake) */}
          {isVideoFake && flaggedFrames.length > 0 ? (
            <div className="mt-auto pt-4 border-t border-gray-200 dark:border-gray-700">
               <div className="flex justify-between items-center mb-3">
                 <p className="text-xs font-bold text-red-600 uppercase flex items-center gap-1">
                    <Activity size={12} /> Suspicious Frames ({flaggedFrames.length})
                 </p>
                 {flaggedFrames.length > 3 && (
                   <button onClick={() => setShowFramesModal(true)} className="text-xs text-blue-500 hover:underline">View All</button>
                 )}
               </div>
               <div className="grid grid-cols-3 gap-2">
                 {flaggedFrames.slice(0, 3).map((frame: any, i: number) => (
                   <div key={i} className="aspect-video relative rounded overflow-hidden bg-gray-100 border border-red-200 group">
                      <img 
                        src={getFrameUrl(frame)} 
                        className="w-full h-full object-cover" 
                        onError={(e) => {e.currentTarget.style.display='none'}}
                        alt={`Suspicious frame ${i}`}
                      />
                     
                   </div>
                 ))}
               </div>
            </div>
          ) : (
            <div className="mt-auto h-24 flex items-center justify-center text-gray-400 text-sm italic border-t border-dashed border-gray-200 dark:border-gray-700 pt-4">
               No visual anomalies detected
            </div>
          )}
        </div>

        {/* --- RIGHT: AUDIO CHANNEL (Contains Segments Inside!) --- */}
        <div className={cn(
          'p-6 rounded-xl border-2 transition-all shadow-sm flex flex-col',
          isAudioFake 
            ? 'bg-red-50 border-red-200 dark:bg-red-900/10 dark:border-red-800' 
            : 'bg-white border-gray-200 dark:bg-gray-800 dark:border-gray-700'
        )}>
          <div className="flex justify-between items-center mb-4">
            <div className="flex items-center gap-3">
               <div className={cn("p-2 rounded-lg", isAudioFake ? "bg-red-100 dark:bg-red-900/50" : "bg-purple-100 dark:bg-purple-900/50")}>
                <Mic className={cn("w-6 h-6", isAudioFake ? "text-red-600" : "text-purple-600")} />
              </div>
              <h3 className="font-bold text-lg text-gray-900 dark:text-white">Audio Channel</h3>
            </div>
            <span className={cn(
              "px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wide",
              isAudioFake 
                ? "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300" 
                : isAudioUnavailable 
                ? "bg-gray-100 text-gray-500" 
                : "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300"
            )}>
              {isAudioFake ? "Synthetic" : isAudioUnavailable ? "N/A" : "Natural"}
            </span>
          </div>

          <div className="flex items-baseline gap-2 mb-2">
            <span className={cn("text-4xl font-bold", isAudioFake ? "text-red-600" : "text-gray-900 dark:text-white")}>
              {isAudioUnavailable ? 'N/A' : `${audioConf.toFixed(2)}%`}
            </span>
            <span className="text-sm font-medium text-gray-500 uppercase">confidence</span>
          </div>

          <div className="mb-4">
            {!isAudioUnavailable && (
              <ProgressBar 
                progress={audioConf} 
                variant={isAudioFake ? 'error' : 'success'} 
                showLabel={false} 
                className="h-2"
              />
            )}
          </div>

          {/* 🎵 SEGMENTS INSIDE THE AUDIO CARD (Only if Fake) */}
          {isAudioFake && audioSegments.length > 0 ? (
            <div className="mt-auto pt-4 border-t border-gray-200 dark:border-gray-700">
               <p className="text-xs font-bold text-red-600 mb-2 uppercase flex items-center gap-1">
                 <Activity size={12} /> Synthetic Segments
               </p>
               <div className="space-y-2">
                 {audioSegments.slice(0, 3).map((seg: any, i: number) => (
                   <div key={i} className="flex justify-between items-center text-xs bg-red-100/50 dark:bg-red-900/20 px-3 py-2 rounded border border-red-100 dark:border-red-800">
                     <span className="font-mono">{seg.start?.toFixed(1)}s - {seg.end?.toFixed(1)}s</span>
                     <span className="font-bold text-red-700">{seg.confidence?.toFixed(0)}% Fake</span>
                   </div>
                 ))}
               </div>
            </div>
          ) : (
             <div className="mt-auto h-24 flex items-center justify-center text-gray-400 text-sm italic border-t border-dashed border-gray-200 dark:border-gray-700 pt-4">
               {isAudioUnavailable ? "No audio track found" : "Audio waveform consistent"}
            </div>
          )}
        </div>
      </div>

      {/* ============ 3. ACTION BUTTONS ============ */}
      <div className="flex flex-col sm:flex-row gap-4 pt-4 border-t border-gray-100 dark:border-gray-800">
        <Button onClick={handleAnalyzeAnother} size="lg" className="flex-1 shadow-lg hover:shadow-xl transition-all">
          Analyze Another Video
        </Button>

        <Button variant="outline" onClick={handleDownloadReport} size="lg" className="shadow-sm">
          <Download size={20} className="mr-2" /> Download Report
        </Button>

        <Button variant="ghost" onClick={() => setShowReportModal(true)} size="lg">
          <Flag size={20} className="mr-2" /> Report Issue
        </Button>
      </div>

      {/* ============ MODALS ============ */}
      <Modal isOpen={showFramesModal} onClose={() => setShowFramesModal(false)} title="All Suspicious Frames" size="xl">
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4 p-1">
          {flaggedFrames.map((frame: any, idx: number) => (
            <div key={idx} className="relative aspect-video rounded-lg overflow-hidden bg-gray-100 dark:bg-gray-700 border group">
              <img src={getFrameUrl(frame)} alt="Frame" className="w-full h-full object-cover" />
              <div className="absolute top-2 left-2 bg-black/70 text-white text-xs px-2 py-1 rounded font-mono">
                {frame.timestamp?.toFixed(2)}s
              </div>
              <div className="absolute top-2 right-2 bg-red-600 text-white text-xs px-2 py-1 rounded font-bold">
                 {Math.round(frame.confidence || 0)}%
              </div>
            </div>
          ))}
        </div>
      </Modal>

      <Modal isOpen={showReportModal} onClose={() => setShowReportModal(false)} title="Report Analysis Issue" size="md">
        <div className="space-y-4">
          <p className="text-gray-600">Help us improve by reporting issues.</p>
          <div className="space-y-3">
            <Button variant="outline" className="w-full justify-start h-auto py-4 px-4 border-2 hover:border-blue-500 hover:bg-blue-50 dark:hover:bg-blue-900/20" onClick={() => { onReportResult?.('false_positive'); setShowReportModal(false); }}>
              <div className="flex items-start gap-3">
                <div className="p-2 bg-green-100 rounded-full text-green-600 mt-1">
                  <CheckCircle size={18} />
                </div>
                <div className="text-left">
                  <span className="block font-semibold text-gray-900 dark:text-white">False Positive</span>
                  <span className="text-sm text-gray-500">This video is actually authentic/real.</span>
                </div>
              </div>
            </Button>
            
            <Button variant="outline" className="w-full justify-start h-auto py-4 px-4 border-2 hover:border-red-500 hover:bg-red-50 dark:hover:bg-red-900/20" onClick={() => { onReportResult?.('false_negative'); setShowReportModal(false); }}>
              <div className="flex items-start gap-3">
                <div className="p-2 bg-red-100 rounded-full text-red-600 mt-1">
                  <AlertTriangle size={18} />
                </div>
                <div className="text-left">
                  <span className="block font-semibold text-gray-900 dark:text-white">False Negative</span>
                  <span className="text-sm text-gray-500">This video is actually a deepfake.</span>
                </div>
              </div>
            </Button>
          </div>
          <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
            <Button variant="ghost" size="sm" className="w-full" onClick={() => setShowReportModal(false)}>Cancel</Button>
          </div>
        </div>
      </Modal>

    </div>
  );
};

export default DetectionResults;