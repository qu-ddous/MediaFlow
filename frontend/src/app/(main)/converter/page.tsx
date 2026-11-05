"use client";

import React, { useState } from "react";
import { Layers, Sparkles, ArrowRight, CheckCircle2 } from "lucide-react";
import { useDownloads } from "@/hooks/use-downloads";
import { Button } from "@/components/ui/button";
import { Select } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { api } from "@/lib/api";

export default function ConverterPage() {
  const { data: downloads } = useDownloads();
  const completedJobs = (downloads || []).filter((d) => d.status === "completed");

  const [selectedJobId, setSelectedJobId] = useState<string>("");
  const [targetFormat, setTargetFormat] = useState("mp4");
  const [targetResolution, setTargetResolution] = useState("original");
  const [isConverting, setIsConverting] = useState(false);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleConvert = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedJobId) {
      setErrorMsg("Please select a completed download to convert");
      return;
    }

    setIsConverting(true);
    setErrorMsg(null);
    setSuccessMsg(null);

    try {
      const res = await api.startConversion({
        job_id: selectedJobId,
        output_format: targetFormat,
        resolution: targetResolution !== "original" ? targetResolution : undefined,
      });

      setSuccessMsg(`Conversion job queued (ID: ${res.job_id.slice(0, 8)}...). Check the download manager.`);
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to start conversion");
    } finally {
      setIsConverting(false);
    }
  };

  return (
    <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-slate-900">
          Media Transcoder & Format Converter
        </h1>
        <p className="text-xs sm:text-sm text-slate-500 mt-1">
          Convert video containers, downscale resolutions, or extract pure high-bitrate audio using FFmpeg 7.
        </p>
      </div>

      <form onSubmit={handleConvert} className="p-6 rounded-2xl bg-white border border-slate-200/90 shadow-sm space-y-6">
        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1.5">
            Select Source File (From Downloads)
          </label>
          <Select
            value={selectedJobId}
            onChange={(e) => setSelectedJobId(e.target.value)}
          >
            <option value="">-- Choose a downloaded file --</option>
            {completedJobs.map((j) => (
              <option key={j.job_id} value={j.job_id}>
                {j.title || j.source_url} (.{j.requested_format})
              </option>
            ))}
          </Select>
          {completedJobs.length === 0 && (
            <p className="text-[11px] text-amber-600 mt-1.5">
              No completed files found in session. Download a file first from the Downloader.
            </p>
          )}
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1.5">
              Target Output Format
            </label>
            <Select
              value={targetFormat}
              onChange={(e) => setTargetFormat(e.target.value)}
            >
              <optgroup label="Video Formats">
                <option value="mp4">MP4 (H.264 / AAC)</option>
                <option value="webm">WebM (VP9 / Opus)</option>
                <option value="mkv">MKV (Matroska)</option>
                <option value="mov">MOV (Apple ProRes / QuickTime)</option>
              </optgroup>
              <optgroup label="Audio Only Extraction">
                <option value="mp3">MP3 (320 kbps)</option>
                <option value="m4a">M4A (AAC)</option>
                <option value="wav">WAV (Lossless PCM)</option>
                <option value="flac">FLAC (Lossless)</option>
              </optgroup>
            </Select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1.5">
              Target Resolution
            </label>
            <Select
              value={targetResolution}
              onChange={(e) => setTargetResolution(e.target.value)}
            >
              <option value="original">Keep Original Resolution</option>
              <option value="1080p">1080p Full HD (1920x1080)</option>
              <option value="720p">720p HD (1280x720)</option>
              <option value="480p">480p SD (854x480)</option>
              <option value="360p">360p Mobile (640x360)</option>
            </Select>
          </div>
        </div>

        {errorMsg && (
          <p className="text-xs text-red-600 bg-red-50 p-3 rounded-xl border border-red-200">
            {errorMsg}
          </p>
        )}

        {successMsg && (
          <p className="text-xs text-emerald-700 bg-emerald-50 p-3 rounded-xl border border-emerald-200 flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4" />
            {successMsg}
          </p>
        )}

        <Button
          type="submit"
          size="lg"
          isLoading={isConverting}
          disabled={!selectedJobId}
          className="w-full font-semibold"
        >
          <Sparkles className="h-4 w-4 mr-2" />
          Transcode Media
        </Button>
      </form>
    </div>
  );
}

