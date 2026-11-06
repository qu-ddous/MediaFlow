"use client";

import React, { useState } from "react";
import { Download, Trash2, History, ExternalLink, FileVideo, FileAudio } from "lucide-react";
import { useDownloads, useDeleteDownload } from "@/hooks/use-downloads";
import { formatFileSize, truncateText } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/common/empty-state";
import { Modal } from "@/components/ui/modal";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import { api } from "@/lib/api";

export default function HistoryPage() {
  const { data: downloads, isLoading } = useDownloads();
  const deleteMutation = useDeleteDownload();
  const { toast } = useToast();

  const [jobToDelete, setJobToDelete] = useState<string | null>(null);

  const completed = (downloads || []).filter((d) => d.status === "completed");

  const confirmDelete = async () => {
    if (!jobToDelete) return;
    try {
      await deleteMutation.mutateAsync(jobToDelete);
      toast({
        title: "Record Deleted",
        description: "The download history record and temporary file were removed.",
        type: "info",
      });
    } catch {
      toast({
        title: "Delete Failed",
        description: "Unable to delete download record.",
        type: "error",
      });
    } finally {
      setJobToDelete(null);
    }
  };

  return (
    <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8 py-10 space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">Download History</h1>
        <p className="text-xs text-slate-500 mt-1">
          Review recent media files processed in this session. Files remain accessible for 24 hours.
        </p>
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-20 w-full rounded-2xl" />
          ))}
        </div>
      ) : completed.length === 0 ? (
        <EmptyState
          icon={History}
          title="No completed downloads yet"
          description="Finished media files will appear here ready to save or stream."
        />
      ) : (
        <div className="space-y-3">
          {completed.map((job) => {
            const isAudio = ["mp3", "m4a", "wav", "flac"].includes((job.requested_format || "").toLowerCase());
            return (
              <div
                key={job.job_id}
                className="flex items-center justify-between p-4 rounded-2xl bg-white border border-slate-200/80 shadow-sm hover:shadow transition-all"
              >
                <div className="flex items-center gap-3 min-w-0 flex-1">
                  <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl bg-slate-100 text-slate-600">
                    {isAudio ? <FileAudio className="h-5 w-5" /> : <FileVideo className="h-5 w-5" />}
                  </div>
                  <div className="min-w-0 flex-1">
                    <h4 className="text-sm font-semibold text-slate-900 truncate">
                      {job.title || truncateText(job.source_url, 40)}
                    </h4>
                    <div className="flex items-center gap-2 mt-0.5 text-xs text-slate-500">
                      <Badge variant="neutral" className="uppercase font-semibold">
                        .{job.requested_format || "mp4"}
                      </Badge>
                      <span>{formatFileSize(job.file_size)}</span>
                      <span>•</span>
                      <span>{new Date(job.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <a
                    href={api.getDownloadFileUrl(job.job_id)}
                    download
                    className="inline-flex items-center gap-1.5 rounded-xl bg-primary-600 px-3.5 py-2 text-xs font-semibold text-white hover:bg-primary-700 transition-colors shadow-sm"
                  >
                    <Download className="h-3.5 w-3.5" />
                    Download
                  </a>

                  <button
                    onClick={() => setJobToDelete(job.job_id)}
                    className="p-2 text-slate-400 hover:text-red-500 rounded-lg transition-colors"
                    title="Delete record"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={Boolean(jobToDelete)}
        onClose={() => setJobToDelete(null)}
        title="Delete Download History?"
        description="This will permanently delete the downloaded media file from the server storage."
      >
        <div className="flex justify-end gap-2.5 pt-4">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setJobToDelete(null)}
          >
            Cancel
          </Button>
          <Button
            variant="danger"
            size="sm"
            onClick={confirmDelete}
            isLoading={deleteMutation.isPending}
          >
            Delete File
          </Button>
        </div>
      </Modal>
    </div>
  );
}
