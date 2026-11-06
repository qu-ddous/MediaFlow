"use client";

import React, { useState } from "react";
import { Layers, Sparkles, UploadCloud, FileVideo, CheckCircle2, ArrowRight } from "lucide-react";
import { useDownloads } from "@/hooks/use-downloads";
import { Button } from "@/components/ui/button";
import { Select } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/hooks/use-toast";
import { api } from "@/lib/api";

export default function ConverterPage() {
  const { data: downloads } = useDownloads();
  const completedJobs = (downloads || []).filter((d) => d.status === "completed");
  const { toast } = useToast();

  const [mode, setMode] = useState<"downloads" | "upload">("downloads");
  const [selectedJobId, setSelectedJobId] = useState<string>("");
  const [fileToUpload, setFileToUpload] = useState<File | null>(null);

  const [targetFormat, setTargetFormat] = useState("mp4");
  const [targetResolution, setTargetResolution] = useState("original");
  const [isConverting, setIsConverting] = useState(false);
  const [convertedJobId, setConvertedJobId] = useState<string | null>(null);

  const handleConvert = async (e: React.FormEvent) => {
    e.preventDefault();

    if (mode === "downloads" && !selectedJobId) {
      toast({
        title: "Selection required",
        description: "Please select a completed download to convert",
        type: "error",
      });
      return;
    }

    if (mode === "upload" && !fileToUpload) {
      toast({
        title: "File required",
        description: "Please choose or drop a media file to upload",
        type: "error",
      });
      return;
    }

    setIsConverting(true);
    setConvertedJobId(null);

    try {
      if (mode === "downloads") {
        const res = await api.startConversion({
          job_id: selectedJobId,
          output_format: targetFormat,
          resolution: targetResolution !== "original" ? targetResolution : undefined,
        });
        setConvertedJobId(res.job_id);
        toast({
          title: "Transcode Queued",
          description: `Task ${res.job_id.slice(0, 8)}... has started processing.`,
          type: "success",
        });
      } else if (fileToUpload) {
        const formData = new FormData();
        formData.append("file", fileToUpload);
        formData.append("output_format", targetFormat);
        if (targetResolution !== "original") {
          formData.append("resolution", targetResolution);
        }

        const res = await api.uploadAndConvert(formData);
        setConvertedJobId(res.job_id);
        toast({
          title: "Upload & Transcode Queued",
          description: `File uploaded successfully. Transcoding started.`,
          type: "success",
        });
      }
    } catch (err: any) {
      toast({
        title: "Conversion Failed",
        description: err.message || "Failed to start conversion",
        type: "error",
      });
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
          Convert video containers, downscale resolutions, or extract pure high-bitrate audio using FFmpeg.
        </p>
      </div>

      {/* Mode Toggle */}
      <div className="flex border-b border-slate-200 gap-4">
        <button
          type="button"
          onClick={() => setMode("downloads")}
          className={`flex items-center gap-2 pb-3.5 text-sm font-semibold border-b-2 transition-colors ${
            mode === "downloads"
              ? "border-primary-600 text-primary-600"
              : "border-transparent text-slate-500 hover:text-slate-800"
          }`}
        >
          <Layers className="h-4 w-4" />
          From Session Downloads
        </button>

        <button
          type="button"
          onClick={() => setMode("upload")}
          className={`flex items-center gap-2 pb-3.5 text-sm font-semibold border-b-2 transition-colors ${
            mode === "upload"
              ? "border-primary-600 text-primary-600"
              : "border-transparent text-slate-500 hover:text-slate-800"
          }`}
        >
          <UploadCloud className="h-4 w-4" />
          Upload Local File
        </button>
      </div>

      <form onSubmit={handleConvert} className="p-6 rounded-2xl bg-white border border-slate-200/90 shadow-sm space-y-6">
        {mode === "downloads" ? (
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
                No completed files found in current session. Either download a file or switch to &quot;Upload Local File&quot;.
              </p>
            )}
          </div>
        ) : (
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1.5">
              Upload Media File (Video or Audio)
            </label>
            <div className="mt-1 flex justify-center rounded-2xl border-2 border-dashed border-slate-300 px-6 pt-5 pb-6 hover:border-primary-500 transition-colors">
              <div className="space-y-1 text-center">
                <UploadCloud className="mx-auto h-10 w-10 text-slate-400" />
                <div className="flex text-sm text-slate-600 justify-center">
                  <label
                    htmlFor="file-upload"
                    className="relative cursor-pointer rounded-md bg-white font-medium text-primary-600 focus-within:outline-none hover:text-primary-500"
                  >
                    <span>Upload a file</span>
                    <input
                      id="file-upload"
                      name="file-upload"
                      type="file"
                      className="sr-only"
                      accept="video/*,audio/*,.mp4,.webm,.mkv,.avi,.mov,.mp3,.wav,.m4a,.flac"
                      onChange={(e) => setFileToUpload(e.target.files?.[0] || null)}
                    />
                  </label>
                  <p className="pl-1">or drag and drop</p>
                </div>
                <p className="text-xs text-slate-400">
                  {fileToUpload ? (
                    <span className="font-semibold text-slate-800">{fileToUpload.name} ({(fileToUpload.size / (1024 * 1024)).toFixed(1)} MB)</span>
                  ) : (
                    "MP4, WebM, MKV, MP3, WAV up to 2GB"
                  )}
                </p>
              </div>
            </div>
          </div>
        )}

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

        {convertedJobId && (
          <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 flex items-center justify-between text-xs text-emerald-800">
            <span className="flex items-center gap-2">
              <CheckCircle2 className="h-4 w-4 text-emerald-600" />
              Conversion processing in background (Task: {convertedJobId.slice(0, 8)}...)
            </span>
            <a
              href={api.getConvertedFileUrl(convertedJobId)}
              className="font-semibold text-emerald-700 underline hover:text-emerald-900 inline-flex items-center gap-1"
              download
            >
              Download Output <ArrowRight className="h-3 w-3" />
            </a>
          </div>
        )}

        <Button
          type="submit"
          size="lg"
          isLoading={isConverting}
          disabled={(mode === "downloads" && !selectedJobId) || (mode === "upload" && !fileToUpload)}
          className="w-full font-semibold"
        >
          <Sparkles className="h-4 w-4 mr-2" />
          {isConverting ? "Processing..." : "Transcode Media"}
        </Button>
      </form>
    </div>
  );
}
