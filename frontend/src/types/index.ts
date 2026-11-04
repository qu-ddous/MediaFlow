export type JobStatus =
  | "pending"
  | "analyzing"
  | "downloading"
  | "processing"
  | "completed"
  | "failed"
  | "cancelled";

export interface FormatOption {
  format_id: string;
  extension: string;
  format_note?: string | null;
  filesize?: number | null;
  filesize_approx?: number | null;
  video_codec?: string | null;
  audio_codec?: string | null;
  quality?: string | null;
  has_video: boolean;
  has_audio: boolean;
}

export interface ResolutionOption {
  label: string;
  width?: number | null;
  height: number;
  fps?: number | null;
}

export interface AudioOption {
  format_id: string;
  codec?: string | null;
  bitrate?: number | null;
  sample_rate?: number | null;
  language?: string | null;
}

export interface EstimatedSize {
  format_id: string;
  quality: string;
  size_bytes?: number | null;
  size_label?: string | null;
}

export interface MediaInfo {
  url: string;
  title: string;
  thumbnail_url?: string | null;
  duration?: number | null;
  duration_string?: string | null;
  source_name: string;
  media_type: "video" | "audio" | "direct_file" | "unknown";
  formats: FormatOption[];
  resolutions: ResolutionOption[];
  audio_streams: AudioOption[];
  estimated_sizes: EstimatedSize[];
  original_format?: string | null;
}

export interface DownloadJob {
  job_id: string;
  source_url: string;
  source_type?: string | null;
  status: JobStatus;
  title?: string | null;
  thumbnail_url?: string | null;
  duration?: number | null;
  requested_format?: string | null;
  requested_quality?: string | null;
  file_size?: number | null;
  progress: number;
  download_speed?: string | null;
  error_message?: string | null;
  created_at: string;
  updated_at: string;
}

export interface DownloadProgressEvent {
  task_id: string;
  progress: number;
  speed: number;
  status: JobStatus;
  eta: string;
  speed_str?: string;
  filename?: string;
  file_size?: number;
  error?: string;
}

export interface ConversionJob {
  job_id: string;
  status: JobStatus;
  progress: number;
  input_format?: string | null;
  output_format?: string | null;
  error_message?: string | null;
}

export interface SystemCapabilities {
  app_name: string;
  max_file_size_mb: number;
  supported_video_formats: string[];
  supported_audio_formats: string[];
  supported_resolutions: string[];
  features: {
    real_time_sse: boolean;
    direct_stream_download: boolean;
    format_conversion: boolean;
    audio_extraction: boolean;
    video_resizing: boolean;
  };
}
