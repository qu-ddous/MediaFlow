# MediaFlow — Environment Variables Reference

All runtime configuration is managed through environment variables and loaded by `pydantic-settings` from the environment or `.env` file.

---

## 1. Core Server Configuration

| Variable | Type | Default | Description |
|---|---|---|---|
| `APP_NAME` | string | `MediaFlow` | Application display name |
| `APP_VERSION` | string | `1.0.0` | Semantic platform version |
| `DEBUG` | boolean | `false` | Enable Swagger `/docs` and verbose error stack traces |
| `LOG_LEVEL` | string | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `HOST` | string | `0.0.0.0` | Server bind IP address |
| `PORT` | integer | `8000` | Server bind port |
| `SECRET_KEY` | string | `change-me` | Secret key used for cryptographic session signing |

---

## 2. Database & Cache

| Variable | Type | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | string | `sqlite+aiosqlite:///./mediaflow.db` | Async SQLAlchemy database connection string (SQLite for dev, PostgreSQL for prod) |
| `DATABASE_ECHO` | boolean | `false` | Print raw SQL statements to console |
| `REDIS_URL` | string | `redis://localhost:6379/0` | Optional Redis broker URL for production Celery task queue |

---

## 3. Storage & Processing Limits

| Variable | Type | Default | Description |
|---|---|---|---|
| `STORAGE_PATH` | string | `./storage` | Absolute or relative path to media workspace |
| `MAX_FILE_SIZE_MB` | integer | `2048` | Maximum permissible download/upload file size (in MB) |
| `FILE_EXPIRY_HOURS` | integer | `24` | Automated retention window before temporary media files are deleted |
| `MAX_CONCURRENT_DOWNLOADS` | integer | `5` | Maximum simultaneous download operations |
| `MAX_CONCURRENT_CONVERSIONS` | integer | `3` | Maximum simultaneous FFmpeg transcoding tasks |
| `DOWNLOAD_TIMEOUT_SECONDS` | integer | `3600` | Maximum execution duration before timing out a download |
| `CONVERSION_TIMEOUT_SECONDS` | integer | `7200` | Maximum execution duration before timing out a transcode |

---

## 4. Security & CORS

| Variable | Type | Default | Description |
|---|---|---|---|
| `CORS_ORIGINS` | string/list | `["http://localhost:3000"]` | Comma-separated list of allowed frontend origins |
| `RATE_LIMIT_DEFAULT` | string | `60/minute` | Global API rate limit per client IP |
| `RATE_LIMIT_ANALYZE` | string | `20/minute` | Rate limit for `/api/v1/analyze` |
| `RATE_LIMIT_DOWNLOAD` | string | `10/minute` | Rate limit for `/api/v1/downloads` |

---

## 5. Frontend Client

| Variable | Type | Default | Description |
|---|---|---|---|
| `NEXT_PUBLIC_API_URL` | string | `http://localhost:8000` | Base URL of the FastAPI backend for browser API calls |

