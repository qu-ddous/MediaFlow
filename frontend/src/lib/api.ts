import {
  ConversionJob,
  DownloadJob,
  MediaInfo,
  SystemCapabilities,
} from "@/types";
import { API_BASE_URL } from "./constants";

export class ApiError extends Error {
  code?: string;
  status: number;
  constructor(message: string, status: number, code?: string) {
    super(message);
    this.status = status;
    this.code = code;
  }
}

async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  const headers = {
    "Content-Type": "application/json",
    ...options?.headers,
  };

  const response = await fetch(url, { ...options, headers });

  if (!response.ok) {
    let errorMessage = `HTTP error ${response.status}`;
    let errorCode: string | undefined;

    try {
      const errorData = await response.json();
      if (errorData.detail) {
        if (typeof errorData.detail === "string") {
          errorMessage = errorData.detail;
        } else if (errorData.detail.message) {
          errorMessage = errorData.detail.message;
          errorCode = errorData.detail.code;
        }
      } else if (errorData.message) {
        errorMessage = errorData.message;
      }
    } catch {
      // Non-JSON error response
    }

    throw new ApiError(errorMessage, response.status, errorCode);
  }

  return response.json();
}

export const api = {
  async analyzeUrl(url: string): Promise<MediaInfo> {
    return request<MediaInfo>("/api/v1/analyze", {
      method: "POST",
      body: JSON.stringify({ url }),
    });
  },

  async startDownload(
    url: string,
    format: string,
    quality: string
  ): Promise<{ job_id: string; status: string; message: string }> {
    return request("/api/v1/downloads", {
      method: "POST",
      body: JSON.stringify({ url, format, quality }),
    });
  },

  async getDownloads(limit: number = 20): Promise<DownloadJob[]> {
    return request<DownloadJob[]>(`/api/v1/downloads?limit=${limit}`);
  },

  async getDownload(jobId: string): Promise<DownloadJob> {
    return request<DownloadJob>(`/api/v1/downloads/${jobId}`);
  },

  async cancelDownload(jobId: string): Promise<{ message: string }> {
    return request(`/api/v1/downloads/${jobId}/cancel`, { method: "POST" });
  },

  async retryDownload(jobId: string): Promise<{ job_id: string; status: string }> {
    return request(`/api/v1/downloads/${jobId}/retry`, { method: "POST" });
  },

  async deleteDownload(jobId: string): Promise<{ message: string }> {
    return request(`/api/v1/downloads/${jobId}`, { method: "DELETE" });
  },

  getDownloadFileUrl(jobId: string): string {
    return `${API_BASE_URL}/api/v1/downloads/${jobId}/file`;
  },

  async startConversion(data: {
    job_id?: string;
    input_path?: string;
    output_format: string;
    resolution?: string;
    bitrate?: string;
  }): Promise<{ job_id: string; status: string }> {
    return request("/api/v1/conversions", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async getConversion(jobId: string): Promise<ConversionJob> {
    return request<ConversionJob>(`/api/v1/conversions/${jobId}`);
  },

  async getHealth(): Promise<{ status: string; database: string }> {
    return request("/api/v1/health");
  },

  async getCapabilities(): Promise<SystemCapabilities> {
    return request("/api/v1/capabilities");
  },
};
