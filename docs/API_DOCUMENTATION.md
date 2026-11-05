# MediaFlow — API Documentation (v1)

MediaFlow exposes a RESTful API with Server-Sent Events (SSE) for real-time progress streaming.

Base URL: `/api/v1`

---

## 1. System Endpoints

### `GET /health`
Verifies backend connectivity, database status, storage writable status, and FFmpeg binary availability.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "database": "connected",
  "storage": "writable",
  "ffmpeg": "available",
  "ffprobe": "available"
}
```

### `GET /capabilities`
Returns supported video/audio containers, resolutions, max file sizes, and enabled feature flags.

---

## 2. Media Analysis

### `POST /analyze`
Analyzes a media URL, extracts metadata, duration, available resolutions, and stream formats.

**Request:**
```json
{
  "url": "https://example.com/video.mp4"
}
```

**Response (200 OK):**
```json
{
  "url": "https://example.com/video.mp4",
  "title": "Example Video",
  "thumbnail_url": null,
  "duration": 124.5,
  "duration_string": "02:04",
  "source_name": "Direct File",
  "media_type": "video",
  "formats": [
    {
      "format_id": "direct",
      "extension": "mp4",
      "has_video": true,
      "has_audio": true
    }
  ],
  "resolutions": [
    {
      "label": "1080p",
      "width": 1920,
      "height": 1080
    }
  ],
  "audio_streams": [],
  "estimated_sizes": []
}
```

---

## 3. Downloads

### `POST /downloads`
Queues a new download job in the background.

**Request:**
```json
{
  "url": "https://example.com/video.mp4",
  "format": "mp4",
  "quality": "1080p"
}
```

**Response (201 Created):**
```json
{
  "job_id": "b1a5e128-4c12-4876-b9a3-95cf0d082eb4",
  "status": "pending",
  "message": "Download queued successfully"
}
```

### `GET /downloads`
Lists recent download jobs with their progress, status, and metadata.

### `GET /downloads/{job_id}`
Returns details for a specific download job.

### `POST /downloads/{job_id}/cancel`
Cancels an active download or transcoding task.

### `POST /downloads/{job_id}/retry`
Restarts a failed or cancelled task.

### `GET /downloads/{job_id}/file`
Downloads the completed media file with binary `application/octet-stream` streaming.

---

## 4. Real-Time Streaming (SSE)

### `GET /events/{job_id}`
Connect to real-time Server-Sent Events stream.

**Data stream event format:**
```text
data: {"task_id": "...", "progress": 45.2, "speed": 2621440, "status": "downloading", "eta": "00:01:20"}
```

