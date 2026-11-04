import { useEffect } from "react";
import { connectToJobEvents } from "@/lib/sse";
import { useDownloadStore } from "@/store/download-store";

export function useJobSSE(jobId: string | null, active: boolean = true) {
  const updateFromSSE = useDownloadStore((s) => s.updateFromSSE);

  useEffect(() => {
    if (!jobId || !active) return;

    const cleanup = connectToJobEvents(jobId, {
      onProgress: (data) => {
        updateFromSSE(data);
      },
      onComplete: (data) => {
        updateFromSSE(data);
      },
      onError: (err) => {
        console.warn(`Job ${jobId} error:`, err);
      },
    });

    return () => cleanup();
  }, [jobId, active, updateFromSSE]);
}
