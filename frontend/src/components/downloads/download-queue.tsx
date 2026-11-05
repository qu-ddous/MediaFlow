"use client";

import React from "react";
import { Download, Inbox } from "lucide-react";
import { useDownloadStore } from "@/store/download-store";
import { useDownloads } from "@/hooks/use-downloads";
import { ProgressCard } from "./progress-card";

export function DownloadQueue() {
  const { data: serverJobs, isLoading } = useDownloads();
  const storeJobs = useDownloadStore((s) => s.activeDownloads);

  // Combine jobs, favoring store state for real-time progress
  const jobsMap = { ...storeJobs };
  if (serverJobs) {
    serverJobs.forEach((job) => {
      if (!jobsMap[job.job_id]) {
        jobsMap[job.job_id] = job;
      }
    });
  }

  const allJobs = Object.values(jobsMap).sort(
    (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  );

  if (isLoading && allJobs.length === 0) {
    return (
      <div className="space-y-4">
        {[1, 2].map((i) => (
          <div key={i} className="h-32 rounded-2xl bg-slate-100/70 animate-pulse" />
        ))}
      </div>
    );
  }

  if (allJobs.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-center rounded-2xl bg-white border border-slate-200/80">
        <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-100 text-slate-400 mb-3">
          <Inbox className="h-6 w-6" />
        </div>
        <h4 className="text-sm font-semibold text-slate-800">No active downloads</h4>
        <p className="text-xs text-slate-500 mt-1 max-w-sm">
          Paste a video or audio URL above to start analyzing and downloading media.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {allJobs.map((job) => (
        <ProgressCard key={job.job_id} job={job} />
      ))}
    </div>
  );
}

