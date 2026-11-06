"use client";

import React, { useState } from "react";
import Link from "next/link";
import {
  DownloadCloud,
  Zap,
  ShieldCheck,
  Cpu,
  Layers,
  ArrowRight,
  Sparkles,
  ChevronDown,
  CheckCircle2,
  FileCheck,
  Headphones,
  Sliders,
} from "lucide-react";
import { UrlInput } from "@/components/downloader/url-input";
import { MediaPreview } from "@/components/downloader/media-preview";
import { DownloadOptions } from "@/components/downloader/download-options";
import { DownloadQueue } from "@/components/downloads/download-queue";
import { useAnalyzeUrl } from "@/hooks/use-analyze";
import { useStartDownload } from "@/hooks/use-downloads";
import { useToast } from "@/hooks/use-toast";
import { MediaInfo } from "@/types";

export default function HomePage() {
  const [analyzedMedia, setAnalyzedMedia] = useState<MediaInfo | null>(null);
  const [openFaq, setOpenFaq] = useState<number | null>(null);
  const { toast } = useToast();

  const analyzeMutation = useAnalyzeUrl();
  const downloadMutation = useStartDownload();

  const handleAnalyze = async (url: string) => {
    try {
      const result = await analyzeMutation.mutateAsync(url);
      setAnalyzedMedia(result);
      toast({
        title: "Media Analyzed",
        description: `Found available streams for "${result.title?.slice(0, 30) || 'media'}..."`,
        type: "success",
      });
    } catch (err: any) {
      toast({
        title: "Analysis Failed",
        description: err.message || "Failed to analyze URL",
        type: "error",
      });
    }
  };

  const handleStartDownload = async (format: string, quality: string) => {
    if (!analyzedMedia) return;
    try {
      await downloadMutation.mutateAsync({
        url: analyzedMedia.url,
        format,
        quality,
      });
      toast({
        title: "Download Queued",
        description: `Task added to download queue. Real-time progress starting...`,
        type: "success",
      });
      // Scroll smoothly to download manager
      const element = document.getElementById("download-queue-section");
      if (element) {
        element.scrollIntoView({ behavior: "smooth" });
      }
    } catch (err: any) {
      toast({
        title: "Download Request Failed",
        description: err.message || "Unable to queue download",
        type: "error",
      });
    }
  };

  const faqs = [
    {
      q: "Which sources and platforms are supported?",
      a: "MediaFlow supports direct HTTP/HTTPS media streams (MP4, WebM, MP3, WAV, etc.) and publicly permitted content across major video-sharing and audio platforms. It strictly observes author and platform permissions without circumventing DRM or access controls.",
    },
    {
      q: "Can I extract audio only from a video stream?",
      a: "Yes! MediaFlow features high-fidelity audio extraction powered by FFmpeg. You can extract pure audio in MP3, M4A (AAC), WAV, or lossless FLAC up to 320 kbps.",
    },
    {
      q: "How does the real-time progress work?",
      a: "We utilize Server-Sent Events (SSE) directly connected to our asynchronous background processing workers. You receive instantaneous speed, percentage, and ETA metrics with zero simulated progress bars.",
    },
    {
      q: "How long are downloaded files retained?",
      a: "Downloaded files are securely stored in your session workspace for 24 hours. After this period, our automated storage lifecycle cleans up temporary files to preserve privacy and disk quota.",
    },
  ];

  return (
    <div className="space-y-16 pb-20">
      {/* ── Section 2: Hero ── */}
      <section className="relative overflow-hidden pt-12 sm:pt-20 pb-12 border-b border-slate-200/60 bg-gradient-to-b from-white via-slate-50/50 to-background">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 text-center relative z-10">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary-50 border border-primary-200/60 text-primary-700 text-xs font-semibold mb-6 shadow-sm">
            <Sparkles className="h-3.5 w-3.5 text-primary-600" />
            Universal Media Engine v1.0
          </div>

          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-slate-900 max-w-4xl mx-auto leading-tight">
            Download and Convert Media with <span className="text-primary-600">Ease</span>
          </h1>

          <p className="mt-4 sm:mt-6 text-base sm:text-lg text-slate-600 max-w-2xl mx-auto leading-relaxed">
            One simple workspace for accessing, downloading, and converting media you are authorized to use. High-resolution streams, zero bloat, instant processing.
          </p>

          <div className="mt-8 sm:mt-10">
            <UrlInput
              onAnalyze={handleAnalyze}
              isLoading={analyzeMutation.isPending}
              error={analyzeMutation.error?.message}
            />
          </div>
        </div>
      </section>

      {/* ── Section 3 & 4: Media Preview & Download Options ── */}
      {analyzedMedia && (
        <section className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8 space-y-6 animate-slide-up">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold text-slate-900">Analysis Result</h2>
            <button
              onClick={() => setAnalyzedMedia(null)}
              className="text-xs text-slate-400 hover:text-slate-600 underline"
            >
              Clear
            </button>
          </div>
          <MediaPreview media={analyzedMedia} />
          <DownloadOptions
            media={analyzedMedia}
            onDownload={handleStartDownload}
            isDownloading={downloadMutation.isPending}
          />
        </section>
      )}

      {/* ── Section 5: Active Download Manager ── */}
      <section id="download-queue-section" className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-slate-900 tracking-tight">Active Downloads & Queue</h2>
            <p className="text-xs text-slate-500 mt-0.5">Real-time status streamed via Server-Sent Events</p>
          </div>
          <Link
            href="/history"
            className="text-xs font-semibold text-primary-600 hover:text-primary-700 inline-flex items-center gap-1"
          >
            View all history <ArrowRight className="h-3.5 w-3.5" />
          </Link>
        </div>
        <DownloadQueue />
      </section>

      {/* ── Section 8: How It Works ── */}
      <section className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 pt-8">
        <div className="text-center max-w-2xl mx-auto mb-12">
          <h2 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">How It Works</h2>
          <p className="text-sm text-slate-500 mt-2">Three frictionless steps to high-fidelity media access</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="p-6 rounded-2xl bg-white border border-slate-200/80 shadow-sm relative">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary-50 text-primary-600 font-bold text-lg mb-4">
              01
            </div>
            <h3 className="text-base font-semibold text-slate-900">Paste Media Link</h3>
            <p className="text-xs text-slate-500 mt-2 leading-relaxed">
              Submit any public media URL or authorized stream link. Our security engine verifies SSRF safety instantly.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-white border border-slate-200/80 shadow-sm relative">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary-50 text-primary-600 font-bold text-lg mb-4">
              02
            </div>
            <h3 className="text-base font-semibold text-slate-900">Select Format & Quality</h3>
            <p className="text-xs text-slate-500 mt-2 leading-relaxed">
              Choose from 4K down to 360p video, or select studio-quality MP3 / FLAC audio extraction.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-white border border-slate-200/80 shadow-sm relative">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary-50 text-primary-600 font-bold text-lg mb-4">
              03
            </div>
            <h3 className="text-base font-semibold text-slate-900">Instant Download</h3>
            <p className="text-xs text-slate-500 mt-2 leading-relaxed">
              Stream the finished file straight to your local device at maximum network throughput.
            </p>
          </div>
        </div>
      </section>

      {/* ── Feature Highlights ── */}
      <section className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 pt-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="flex items-start gap-4 p-5 rounded-2xl bg-white border border-slate-200/80">
            <div className="p-2.5 rounded-xl bg-primary-50 text-primary-600 flex-shrink-0">
              <Zap className="h-5 w-5" />
            </div>
            <div>
              <h4 className="text-sm font-semibold text-slate-900">Fast Async Processing</h4>
              <p className="text-xs text-slate-500 mt-1">Multi-threaded stream pipelines avoid long buffering times.</p>
            </div>
          </div>

          <div className="flex items-start gap-4 p-5 rounded-2xl bg-white border border-slate-200/80">
            <div className="p-2.5 rounded-xl bg-emerald-50 text-emerald-600 flex-shrink-0">
              <ShieldCheck className="h-5 w-5" />
            </div>
            <div>
              <h4 className="text-sm font-semibold text-slate-900">Enterprise SSRF Protection</h4>
              <p className="text-xs text-slate-500 mt-1">Private IP isolation and strict DNS safety guarantees.</p>
            </div>
          </div>

          <div className="flex items-start gap-4 p-5 rounded-2xl bg-white border border-slate-200/80">
            <div className="p-2.5 rounded-xl bg-indigo-50 text-indigo-600 flex-shrink-0">
              <Cpu className="h-5 w-5" />
            </div>
            <div>
              <h4 className="text-sm font-semibold text-slate-900">Real FFmpeg Transcoding</h4>
              <p className="text-xs text-slate-500 mt-1">Accurate re-encoding with H.264, VP9, AAC, and MP3.</p>
            </div>
          </div>
        </div>
      </section>

      {/* ── Section 9: FAQ ── */}
      <section className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8 pt-8">
        <div className="text-center mb-8">
          <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Frequently Asked Questions</h2>
          <p className="text-xs text-slate-500 mt-1">Everything you need to know about formats, privacy, and speed</p>
        </div>

        <div className="space-y-3">
          {faqs.map((faq, index) => {
            const isOpen = openFaq === index;
            return (
              <div
                key={index}
                className="rounded-xl border border-slate-200/80 bg-white overflow-hidden transition-all"
              >
                <button
                  type="button"
                  onClick={() => setOpenFaq(isOpen ? null : index)}
                  className="w-full flex items-center justify-between p-4 text-left text-sm font-semibold text-slate-900 hover:bg-slate-50 transition-colors"
                >
                  <span>{faq.q}</span>
                  <ChevronDown
                    className={`h-4 w-4 text-slate-400 transition-transform duration-200 ${
                      isOpen ? "rotate-180 text-primary-600" : ""
                    }`}
                  />
                </button>
                {isOpen && (
                  <div className="px-4 pb-4 pt-1 text-xs text-slate-600 leading-relaxed border-t border-slate-100">
                    {faq.a}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </section>
    </div>
  );
}

