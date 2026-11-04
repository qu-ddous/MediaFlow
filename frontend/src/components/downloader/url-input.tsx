"use client";

import React, { useState } from "react";
import { Link2, Clipboard, ArrowRight, Loader2, Sparkles, CheckCircle2 } from "lucide-react";
import { Button } from "@/lib/../components/ui/button";

interface UrlInputProps {
  onAnalyze: (url: string) => void;
  isLoading: boolean;
  error?: string | null;
}

export function UrlInput({ onAnalyze, isLoading, error }: UrlInputProps) {
  const [url, setUrl] = useState("");
  const [copied, setCopied] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (url.trim()) {
      onAnalyze(url.trim());
    }
  };

  const handlePaste = async () => {
    try {
      const text = await navigator.clipboard.readText();
      if (text) {
        setUrl(text);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      }
    } catch {
      // Clipboard permission denied or unavailable
    }
  };

  return (
    <div className="w-full max-w-3xl mx-auto">
      <form onSubmit={handleSubmit} className="relative">
        <div className="flex flex-col sm:flex-row items-center gap-2 p-2 bg-white rounded-2xl border border-slate-200/90 shadow-xl shadow-slate-200/50 transition-all focus-within:border-primary-500 focus-within:ring-4 focus-within:ring-primary-500/10">
          {/* Input field */}
          <div className="relative flex-1 w-full flex items-center">
            <Link2 className="absolute left-4 h-5 w-5 text-slate-400" />
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="Paste video, audio, or direct media URL here..."
              disabled={isLoading}
              required
              className="w-full bg-transparent pl-12 pr-12 py-3.5 text-sm sm:text-base text-slate-900 placeholder:text-slate-400 focus:outline-none"
            />
            <button
              type="button"
              onClick={handlePaste}
              title="Paste from clipboard"
              className="absolute right-3 p-1.5 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-100 transition-colors"
            >
              {copied ? (
                <CheckCircle2 className="h-4 w-4 text-emerald-500" />
              ) : (
                <Clipboard className="h-4 w-4" />
              )}
            </button>
          </div>

          {/* Action button */}
          <Button
            type="submit"
            isLoading={isLoading}
            size="lg"
            className="w-full sm:w-auto min-w-[130px] rounded-xl font-medium"
          >
            {isLoading ? (
              "Analyzing..."
            ) : (
              <>
                Analyze
                <ArrowRight className="ml-2 h-4 w-4" />
              </>
            )}
          </Button>
        </div>

        {error && (
          <div className="mt-3 p-3 rounded-xl bg-red-50 border border-red-200/80 text-xs text-red-600 flex items-center gap-2 animate-fade-in">
            <span className="font-semibold">Error:</span> {error}
          </div>
        )}
      </form>

      {/* Quick source pills */}
      <div className="mt-4 flex flex-wrap items-center justify-center gap-2 text-xs text-slate-500">
        <span className="text-slate-400 font-medium">Supported Sources:</span>
        <span className="px-2.5 py-1 rounded-full bg-slate-100 text-slate-600 font-medium">Direct MP4/MP3</span>
        <span className="px-2.5 py-1 rounded-full bg-slate-100 text-slate-600 font-medium">Vimeo</span>
        <span className="px-2.5 py-1 rounded-full bg-slate-100 text-slate-600 font-medium">Dailymotion</span>
        <span className="px-2.5 py-1 rounded-full bg-slate-100 text-slate-600 font-medium">SoundCloud</span>
        <span className="px-2.5 py-1 rounded-full bg-slate-100 text-slate-600 font-medium">Public HLS/DASH</span>
      </div>
    </div>
  );
}
