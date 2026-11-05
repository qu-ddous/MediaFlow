# MediaFlow — Professional Universal Video & Audio Downloader

> **One Link. Multiple Formats. Seamless Downloads.**

MediaFlow is a high-performance universal media extraction, downloading, and format transcoding platform. Built with a modern Next.js frontend, an asynchronous FastAPI backend, and an FFmpeg 7 processing engine, it delivers stream parsing, real-time download progress tracking via Server-Sent Events (SSE), and enterprise-grade SSRF security.

---

## Key Features

- **Smart URL Analyzer:** Deep inspection of media streams, extracting true resolutions, frame rates, codecs, and audio bitrates without fabricating fake formats.
- **Real-Time Progress Streaming:** True Server-Sent Events (SSE) streaming percentage, transfer speed, and remaining time (ETA). No simulated progress bars.
- **FFmpeg Transcoding Engine:** High-performance video container remuxing (MP4, WebM, MKV, MOV), resolution resizing (4K down to 360p), and high-bitrate audio extraction (MP3, M4A, WAV, FLAC).
- **Security-First Architecture:** Comprehensive protection against Server-Side Request Forgery (SSRF) with DNS pre-resolution, private IP blocking, strictly argument-array subprocess execution (zero shell interpolation), and path traversal prevention.
- **Zero-Friction Local Development:** Runs out-of-the-box using SQLite and asynchronous task workers without requiring external Redis or Docker containers for local dev.

---

## Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | Next.js 14 (App Router), React 18, TypeScript, Tailwind CSS, TanStack Query, Zustand, Lucide Icons |
| **Backend** | Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.0 (async), SlowAPI rate limiting |
| **Media Engine** | FFmpeg 7.x, FFprobe, yt-dlp (compliant sources only), aiohttp streaming |
| **Storage & Real-Time** | UUID storage directories, automated 24h retention cleanup, native Server-Sent Events (SSE) |

---

## Quickstart

### 1. Backend (FastAPI)
```powershell
cd backend
python -m pip install -r requirements.txt
python -m pytest tests -v
python -m uvicorn app.main:app --port 8000 --reload
```

### 2. Frontend (Next.js)
```powershell
cd frontend
npm install
npm run dev
```

Visit `http://localhost:3000` to access the application.

---

## Legal & Compliance

MediaFlow is engineered exclusively for authorized media streams, creative commons materials, and personal user archives. It strictly complies with provider terms and does not circumvent Digital Rights Management (DRM) or access controls.
