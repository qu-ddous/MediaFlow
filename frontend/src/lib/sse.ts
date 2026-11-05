import { DownloadProgressEvent } from "@/types";
import { API_BASE_URL } from "./constants";

export interface SSECallbacks {
  onProgress?: (data: DownloadProgressEvent) => void;
  onComplete?: (data: DownloadProgressEvent) => void;
  onError?: (error: Error) => void;
}

export function connectToJobEvents(
  jobId: string,
  callbacks: SSECallbacks
): () => void {
  const url = `${API_BASE_URL}/api/v1/events/${jobId}`;
  let eventSource: EventSource | null = null;
  let isClosed = false;

  try {
    eventSource = new EventSource(url);

    eventSource.onmessage = (event) => {
      if (isClosed) return;
      try {
        const data: DownloadProgressEvent = JSON.parse(event.data);
        callbacks.onProgress?.(data);

        if (data.status === "completed") {
          callbacks.onComplete?.(data);
          eventSource?.close();
        } else if (data.status === "failed" || data.status === "cancelled") {
          callbacks.onError?.(new Error(data.error || `Task ${data.status}`));
          eventSource?.close();
        }
      } catch (err) {
        console.error("Failed to parse SSE payload:", err);
      }
    };

    eventSource.onerror = (err) => {
      if (isClosed) return;
      console.warn("SSE connection error:", err);
      // EventSource automatically retries HTTP reconnects
    };
  } catch (err) {
    callbacks.onError?.(err as Error);
  }

  // Return teardown function
  return () => {
    isClosed = true;
    if (eventSource) {
      eventSource.close();
      eventSource = null;
    }
  };
}

