export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const SUPPORTED_VIDEO_FORMATS = [
  { label: "MP4 (Universal)", value: "mp4" },
  { label: "WebM (High Compression)", value: "webm" },
  { label: "MKV (Matroska)", value: "mkv" },
  { label: "MOV (Apple QuickTime)", value: "mov" },
];

export const SUPPORTED_AUDIO_FORMATS = [
  { label: "MP3 (Standard Audio)", value: "mp3" },
  { label: "M4A (AAC Audio)", value: "m4a" },
  { label: "WAV (Uncompressed)", value: "wav" },
  { label: "FLAC (Lossless)", value: "flac" },
];

export const STANDARD_RESOLUTIONS = [
  "2160p (4K UHD)",
  "1440p (QHD)",
  "1080p (Full HD)",
  "720p (HD)",
  "480p (SD)",
  "360p",
];

