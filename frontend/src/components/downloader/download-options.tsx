"use client";

import React, { useState } from "react";
import { Download, Film, Music, Check, Sparkles, AlertCircle } from "lucide-react";
import { MediaInfo } from "@/types";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Select } from "@/components/ui/select";
import { formatFileSize } from "@/lib/utils";

interface DownloadOptionsProps {
  media: MediaInfo;
  onDownload: (format: string, quality: string) => void;
  isDownloading: boolean;
}

export function DownloadOptions({ media, onDownload, isDownloading }: DownloadOptionsProps) {
  const [mode, setMode] = useState<"video" | "audio">("video");

  // Video options
  const [selectedVideoFormat, setSelectedVideoFormat] = useState("mp4");
  const [selectedResolution, setSelectedResolution] = useState(
    media.resolutions[0]?.label || "best"
  );

  // Audio options
  const [selectedAudioFormat, setSelectedAudioFormat] = useState("mp3");
  const [selectedAudioQuality, setSelectedAudioQuality] = useState("192k");

  // Determine if conversion is required
  const originalExt = (media.original_format || "").toLowerCase();
  const needsConversion =
    mode === "video"
      ? selectedVideoFormat !== originalExt && originalExt !== ""
      : true;

  // Estimated size calculation
  const currentResolutionObj = media.resolutions.find(
    (r) => r.label === selectedResolution
  );

  const matchedSizeObj = media.estimated_sizes.find(
    (s) => s.quality === selectedResolution
  );

  const handleStart = () => {
    if (mode === "video") {
      onDownload(selectedVideoFormat, selectedResolution);
    } else {
      onDownload(selectedAudioFormat, selectedAudioQuality);
    }
  };

  return (
    <div className="p-6 rounded-2xl bg-white border border-slate-200/90 shadow-sm space-y-6">
      {/* Mode selection tabs */}
      <div className="flex border-b border-slate-200">
        <button
          type="button"
          onClick={() => setMode("video")}
          className={`flex items-center gap-2 pb-3.5 px-4 text-sm font-semibold border-b-2 transition-colors ${
            mode === "video"
              ? "border-primary-600 text-primary-600"
              : "border-transparent text-slate-500 hover:text-slate-800"
          }`}
        >
          <Film className="h-4 w-4" />
          Video + Audio
        </button>

        <button
          type="button"
          onClick={() => setMode("audio")}
          className={`flex items-center gap-2 pb-3.5 px-4 text-sm font-semibold border-b-2 transition-colors ${
            mode === "audio"
              ? "border-primary-600 text-primary-600"
              : "border-transparent text-slate-500 hover:text-slate-800"
          }`}
        >
          <Music className="h-4 w-4" />
          Audio Only
        </button>
      </div>

      {mode === "video" ? (
        /* Video Form */
        <div className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                Resolution & Quality
              </label>
              <Select
                value={selectedResolution}
                onChange={(e) => setSelectedResolution(e.target.value)}
              >
                {media.resolutions && media.resolutions.length > 0 ? (
                  media.resolutions.map((res) => (
                    <option key={res.label} value={res.label}>
                      {res.label} {res.fps ? `(${res.fps}fps)` : ""}
                    </option>
                  ))
                ) : (
                  <option value="best">Original Source Quality (Auto)</option>
                )}
              </Select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                Container Format
              </label>
              <Select
                value={selectedVideoFormat}
                onChange={(e) => setSelectedVideoFormat(e.target.value)}
              >
                <option value="mp4">MP4 (Default, Wide Support)</option>
                <option value="webm">WebM (VP9 / Opus)</option>
                <option value="mkv">MKV (Matroska)</option>
                <option value="mov">MOV (QuickTime)</option>
              </Select>
            </div>
          </div>

          {/* Details & badges */}
          <div className="flex flex-wrap items-center justify-between gap-3 p-3.5 rounded-xl bg-slate-50 border border-slate-200/60 text-xs">
            <div className="flex items-center gap-2">
              <span className="text-slate-500 font-medium">Processing Method:</span>
              {needsConversion ? (
                <Badge variant="warning">
                  <Sparkles className="h-3 w-3 mr-1" /> Transcoding to .{selectedVideoFormat}
                </Badge>
              ) : (
                <Badge variant="success">
                  <Check className="h-3 w-3 mr-1" /> Direct Stream Copy
                </Badge>
              )}
            </div>

            {matchedSizeObj?.size_label && (
              <div className="text-slate-600 font-medium">
                Approx. Size: <span className="font-semibold text-slate-900">{matchedSizeObj.size_label}</span>
              </div>
            )}
          </div>
        </div>
      ) : (
        /* Audio Form */
        <div className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                Audio Format
              </label>
              <Select
                value={selectedAudioFormat}
                onChange={(e) => setSelectedAudioFormat(e.target.value)}
              >
                <option value="mp3">MP3 (Universal, 320k max)</option>
                <option value="m4a">M4A / AAC (Apple Compatible)</option>
                <option value="wav">WAV (Uncompressed PCM)</option>
                <option value="flac">FLAC (Lossless)</option>
              </Select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                Bitrate Quality
              </label>
              <Select
                value={selectedAudioQuality}
                onChange={(e) => setSelectedAudioQuality(e.target.value)}
              >
                <option value="320k">320 kbps (Studio Quality)</option>
                <option value="256k">256 kbps (High Quality)</option>
                <option value="192k">192 kbps (Standard Quality)</option>
                <option value="128k">128 kbps (Compact)</option>
              </Select>
            </div>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200/60 text-xs flex items-center gap-2 text-slate-600">
            <Sparkles className="h-4 w-4 text-primary-600" />
            Audio will be extracted directly with FFmpeg high-efficiency resampler.
          </div>
        </div>
      )}

      {/* Start Button */}
      <Button
        onClick={handleStart}
        isLoading={isDownloading}
        size="lg"
        className="w-full text-base font-semibold"
      >
        <Download className="h-5 w-5 mr-2" />
        {isDownloading ? "Starting Download..." : `Download ${mode === "video" ? selectedVideoFormat.toUpperCase() : selectedAudioFormat.toUpperCase()}`}
      </Button>
    </div>
  );
}

