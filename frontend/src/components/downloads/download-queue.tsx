"use client";

import React, { useState } from "react";
import { Download, Inbox, Trash2, CheckCircle2, Clock, AlertCircle } from "lucide-react";
import { useDownloadStore } from "@/store/download-store";
import { useDownloads } from "@/hooks/use-downloads";
import { ProgressCard } from "./progress-card";
import { EmptyState } from "@/components/common/empty-state";
import { Skeleton } from "@/components/ui/skeleton";
import { Modal } from "@/components/ui/modal";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";

export function DownloadQueue() {
  const { data: serverJobs, isLoading } = useDownloads();
  const storeJobs = useDownloadStore((s) => s.activeDownloads);
  const clearCompleted = useDownloadStore((s) => s.clearCompleted);
  const { toast } = useToast();

  const [filter, setFilter] = useState<"all" | "active" | "completed">("all");
  const [isClearModalOpen, setIsClearModalOpen] = useState(false);

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

  const activeCount = allJobs.filter(
    (j) => j.status === "downloading" || j.status === "processing" || j.status === "pending"
  ).length;
  const completedCount = allJobs.filter((j) => j.status === "completed").length;

  const filteredJobs = allJobs.filter((j) => {
    if (filter === "active") {
      return j.status === "downloading" || j.status === "processing" || j.status === "pending";
    }
    if (filter === "completed") {
      return j.status === "completed";
    }
    return true;
  });

  const handleClearCompleted = () => {
    clearCompleted();
    setIsClearModalOpen(false);
    toast({
      title: "Completed Jobs Cleared",
      description: "Finished download entries have been cleared from active queue view.",
      type: "info",
    });
  };

  if (isLoading && allJobs.length === 0) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <Skeleton key={i} className="h-32 w-full rounded-2xl" />
        ))}
      </div>
    );
  }

  if (allJobs.length === 0) {
    return (
      <EmptyState
        icon={Inbox}
        title="No active downloads"
        description="Paste a video, audio, or direct media URL on the homepage to start downloading."
      />
    );
  }

  return (
    <div className="space-y-4">
      {/* Controls & Filter Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-2 border-b border-slate-100">
        <div className="flex items-center gap-1.5 text-xs">
          <button
            onClick={() => setFilter("all")}
            className={`px-3 py-1.5 rounded-lg font-semibold transition-colors ${
              filter === "all"
                ? "bg-slate-900 text-white"
                : "bg-slate-100 text-slate-600 hover:bg-slate-200"
            }`}
          >
            All ({allJobs.length})
          </button>
          <button
            onClick={() => setFilter("active")}
            className={`px-3 py-1.5 rounded-lg font-semibold transition-colors ${
              filter === "active"
                ? "bg-primary-600 text-white"
                : "bg-slate-100 text-slate-600 hover:bg-slate-200"
            }`}
          >
            In Progress ({activeCount})
          </button>
          <button
            onClick={() => setFilter("completed")}
            className={`px-3 py-1.5 rounded-lg font-semibold transition-colors ${
              filter === "completed"
                ? "bg-emerald-600 text-white"
                : "bg-slate-100 text-slate-600 hover:bg-slate-200"
            }`}
          >
            Completed ({completedCount})
          </button>
        </div>

        {completedCount > 0 && (
          <button
            onClick={() => setIsClearModalOpen(true)}
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-red-600 transition-colors"
          >
            <Trash2 className="h-3.5 w-3.5" />
            Clear Completed
          </button>
        )}
      </div>

      {/* List */}
      <div className="space-y-3">
        {filteredJobs.length === 0 ? (
          <div className="p-8 text-center text-xs text-slate-500 bg-slate-50 rounded-2xl border border-slate-200/60">
            No items matching selected filter &quot;{filter}&quot;.
          </div>
        ) : (
          filteredJobs.map((job) => <ProgressCard key={job.job_id} job={job} />)
        )}
      </div>

      {/* Confirmation Modal */}
      <Modal
        isOpen={isClearModalOpen}
        onClose={() => setIsClearModalOpen(false)}
        title="Clear Completed Tasks?"
        description="This will remove completed tasks from your active queue list view. Your saved files on disk will not be deleted."
      >
        <div className="flex justify-end gap-2.5 pt-4">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setIsClearModalOpen(false)}
          >
            Cancel
          </Button>
          <Button
            variant="danger"
            size="sm"
            onClick={handleClearCompleted}
          >
            Clear List
          </Button>
        </div>
      </Modal>
    </div>
  );
}
