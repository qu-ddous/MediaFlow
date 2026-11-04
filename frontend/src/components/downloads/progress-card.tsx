"use client";

import React from "react";
import { Download, XCircle, RefreshCw, CheckCircle2, AlertCircle, FileVideo, FileAudio, ExternalLink, Trash2 } from "lucide-react";
import { DownloadJob } from "@/types";
import { useJobSSE } from "@/hooks/use-sse";
import { useCancelDownload, useDeleteDownload, useRetryDownload } from "@/hooks/use-downloads";
import { formatFileSize, truncateText } from "@/lib/utils";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";

interface ProgressCardProps {
  job: DownloadJob;
}

export function ProgressCard({ job }: ProgressCardProps) {
  // Connect to SSE for real-time events if active
  const isActive = job.status === "downloading" || job.status === "processing" || job.status === "pending";
  useJobSSE(job.job_id, isActive);

  const cancelMutation = useCancelDownload();
  const retryMutation = useRetryDownload();
  const deleteMutation = useDeleteDownload();

  const isAudio = ["mp3", "m4a", "wav", "flac"].includes((job.requested_format || "").toLowerCase());

  const getStatusBadge = () => {
    switch (job.status) {
      case "completed":
        return <Badge variant="success">Completed</Badge>;
      case "downloading":
        return <Badge variant="default" className="animate-pulse-subtle">Downloading</Badge>;
      case "processing":
        return <Badge variant="warning" className="animate-pulse-subtle">Transcoding</Badge>;
      case "failed":
        return <Badge variant="error">Failed</Badge>;
      case "cancelled":
        return <Badge variant="neutral">Cancelled</Badge>;
      default:
        return <Badge variant="neutral">Pending</Badge>;
    }
  };

  return (
    <div className="p-5 rounded-2xl bg-white border border-slate-200/90 shadow-sm transition-all hover:shadow-md space-y-4">
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-start gap-3 flex-1 min-w-0">
          <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl bg-slate-100 text-slate-600">
            {isAudio ? <FileAudio className="h-5 w-5" /> : <FileVideo className="h-5 w-5" />}
          </div>
          <div className="min-w-0 flex-1">
            <h4 className="text-sm font-semibold text-slate-900 truncate">
              {job.title || truncateText(job.source_url, 45)}
            </h4>
            <div className="flex items-center gap-2 mt-1 text-xs text-slate-500">
              <span className="font-semibold uppercase text-slate-700">.{job.requested_format || "mp4"}</span>
              <span>•</span>
              <span>{job.requested_quality || "Original"}</span>
              {job.file_size ? (
                <>
                  <span>•</span>
                  <span>{formatFileSize(job.file_size)}</span>
                </>
              ) : null}
            </div>
          </div>
        </div>

        <div>{getStatusBadge()}</div>
      </div>

      {/* Progress Bar (when active or completed) */}
      {(job.status === "downloading" || job.status === "processing") && (
        <div className="space-y-1.5">
          <div className="flex justify-between text-xs font-medium text-slate-600">
            <span>{job.status === "processing" ? "Finalizing media..." : "Downloading stream..."}</span>
            <span>{job.progress.toFixed(1)}%</span>
          </div>
          <Progress value={job.progress} />
          {job.download_speed && (
            <div className="flex justify-between text-[11px] text-slate-400">
              <span>Speed: {job.download_speed}</span>
              <span>In queue</span>
            </div>
          )}
        </div>
      )}

      {/* Error state */}
      {job.status === "failed" && job.error_message && (
        <div className="p-3 rounded-xl bg-red-50 border border-red-200 text-xs text-red-600 flex items-start gap-2">
          <AlertCircle className="h-4 w-4 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="font-semibold">Download Failed</p>
            <p className="text-red-500 mt-0.5">{job.error_message}</p>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex items-center justify-end gap-2 pt-1 border-t border-slate-100">
        {job.status === "completed" && (
          <a
            href={api.getDownloadFileUrl(job.job_id)}
            download
            className="inline-flex items-center gap-1.5 rounded-xl bg-primary-600 px-4 py-2 text-xs font-semibold text-white hover:bg-primary-700 shadow-sm transition-all"
          >
            <Download className="h-3.5 w-3.5" />
            Save File
          </a>
        )}

        {(job.status === "downloading" || job.status === "processing" || job.status === "pending") && (
          <Button
            size="sm"
            variant="ghost"
            onClick={() => cancelMutation.mutate(job.job_id)}
            isLoading={cancelMutation.isPending}
            className="text-xs text-slate-500 hover:text-red-600"
          >
            <XCircle className="h-3.5 w-3.5 mr-1" />
            Cancel
          </Button>
        )}

        {(job.status === "failed" || job.status === "cancelled") && (
          <Button
            size="sm"
            variant="outline"
            onClick={() => retryMutation.mutate(job.job_id)}
            isLoading={retryMutation.isPending}
            className="text-xs"
          >
            <RefreshCw className="h-3.5 w-3.5 mr-1" />
            Retry
          </Button>
        )}

        <button
          onClick={() => deleteMutation.mutate(job.job_id)}
          title="Delete from list"
          className="p-2 text-slate-400 hover:text-red-500 rounded-lg transition-colors"
        >
          <Trash2 className="h-3.5 w-3.5" />
        </button>
      </div>
    </div>
  );
}
