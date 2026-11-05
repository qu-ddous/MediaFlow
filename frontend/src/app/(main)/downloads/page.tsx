import React from "react";
import { DownloadQueue } from "@/components/downloads/download-queue";

export default function DownloadsPage() {
  return (
    <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8 py-10 space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">Active Downloads</h1>
        <p className="text-xs text-slate-500 mt-1">
          Monitor your current download queue and transcoding processes in real time.
        </p>
      </div>

      <DownloadQueue />
    </div>
  );
}

