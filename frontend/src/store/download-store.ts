import { create } from "zustand";
import { DownloadJob, DownloadProgressEvent } from "@/types";

interface DownloadStore {
  activeDownloads: Record<string, DownloadJob>;
  addOrUpdateJob: (job: DownloadJob) => void;
  updateFromSSE: (event: DownloadProgressEvent) => void;
  removeJob: (jobId: string) => void;
  clearCompleted: () => void;
}

export const useDownloadStore = create<DownloadStore>((set) => ({
  activeDownloads: {},

  addOrUpdateJob: (job) =>
    set((state) => ({
      activeDownloads: {
        ...state.activeDownloads,
        [job.job_id]: {
          ...state.activeDownloads[job.job_id],
          ...job,
        },
      },
    })),

  updateFromSSE: (event) =>
    set((state) => {
      const existing = state.activeDownloads[event.task_id];
      if (!existing) return state;

      return {
        activeDownloads: {
          ...state.activeDownloads,
          [event.task_id]: {
            ...existing,
            progress: event.progress,
            status: event.status,
            download_speed: event.speed_str || existing.download_speed,
            file_size: event.file_size || existing.file_size,
            error_message: event.error || existing.error_message,
          },
        },
      };
    }),

  removeJob: (jobId) =>
    set((state) => {
      const next = { ...state.activeDownloads };
      delete next[jobId];
      return { activeDownloads: next };
    }),

  clearCompleted: () =>
    set((state) => {
      const filtered = Object.fromEntries(
        Object.entries(state.activeDownloads).filter(
          ([_, job]) => job.status !== "completed" && job.status !== "failed" && job.status !== "cancelled"
        )
      );
      return { activeDownloads: filtered };
    }),
}));
