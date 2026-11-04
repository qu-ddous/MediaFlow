import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useDownloadStore } from "@/store/download-store";
import { DownloadJob } from "@/types";

export function useDownloads() {
  const addOrUpdateJob = useDownloadStore((s) => s.addOrUpdateJob);

  return useQuery<DownloadJob[]>({
    queryKey: ["downloads"],
    queryFn: async () => {
      const list = await api.getDownloads();
      list.forEach((job) => addOrUpdateJob(job));
      return list;
    },
    refetchInterval: 5000,
  });
}

export function useStartDownload() {
  const queryClient = useQueryClient();
  const addOrUpdateJob = useDownloadStore((s) => s.addOrUpdateJob);

  return useMutation({
    mutationFn: ({ url, format, quality }: { url: string; format: string; quality: string }) =>
      api.startDownload(url, format, quality),
    onSuccess: (data, vars) => {
      // Optimistically add to store
      addOrUpdateJob({
        job_id: data.job_id,
        source_url: vars.url,
        requested_format: vars.format,
        requested_quality: vars.quality,
        status: "pending",
        progress: 0,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      });
      queryClient.invalidateQueries({ queryKey: ["downloads"] });
    },
  });
}

export function useCancelDownload() {
  const queryClient = useQueryClient();
  const addOrUpdateJob = useDownloadStore((s) => s.addOrUpdateJob);

  return useMutation({
    mutationFn: (jobId: string) => api.cancelDownload(jobId),
    onSuccess: (_, jobId) => {
      const current = useDownloadStore.getState().activeDownloads[jobId];
      if (current) {
        addOrUpdateJob({ ...current, status: "cancelled" });
      }
      queryClient.invalidateQueries({ queryKey: ["downloads"] });
    },
  });
}

export function useRetryDownload() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (jobId: string) => api.retryDownload(jobId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["downloads"] });
    },
  });
}

export function useDeleteDownload() {
  const queryClient = useQueryClient();
  const removeJob = useDownloadStore((s) => s.removeJob);

  return useMutation({
    mutationFn: (jobId: string) => api.deleteDownload(jobId),
    onSuccess: (_, jobId) => {
      removeJob(jobId);
      queryClient.invalidateQueries({ queryKey: ["downloads"] });
    },
  });
}
