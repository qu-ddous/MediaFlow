# MediaFlow — Production Deployment Guide

MediaFlow is architected with a decoupled frontend (Next.js) and backend (FastAPI + FFmpeg worker), making it straightforward to deploy via Docker, cloud containers (AWS ECS, GCP Cloud Run, Render, Railway), or traditional VPS Linux instances.

---

## 1. Architecture Split

```
Clients (Web Browsers)
          │
          ▼
   [ Nginx Reverse Proxy / Cloudflare ]
     │                              │
     ▼ (Port 3000)                  ▼ (Port 8000)
[ Next.js Frontend ]           [ FastAPI Core & SSE ]
                                    │
                       ┌────────────┴────────────┐
                       ▼                         ▼
               [ PostgreSQL 15+ ]        [ Redis 7+ Broker ]
                                                 │
                                                 ▼
                                        [ Celery Workers + FFmpeg ]
```

---

## 2. Docker Compose Deployment (All-in-One)

The fastest way to deploy the entire production stack is using Docker Compose:

```bash
# Clone the repository
git clone https://github.com/your-org/MediaFlow.git
cd MediaFlow

# Copy environment variables
cp .env.example .env

# Build and start services in background
docker-compose -f docker/docker-compose.yml up --build -d
```

### Verifying deployment:
```bash
docker-compose -f docker/docker-compose.yml ps
docker-compose -f docker/docker-compose.yml logs -f backend
```

---

## 3. Important Production Requirements

### Server-Sent Events (SSE) Buffering
In production reverse proxies (like Nginx, Traefik, or Cloudflare), **response buffering must be disabled** on `/api/v1/events/`:
```nginx
proxy_buffering off;
proxy_cache off;
proxy_read_timeout 3600s;
```
If proxy buffering is enabled, real-time download progress updates will be delayed until the task finishes.

### Temporary File Retention & Disk Volumes
Mount a persistent Docker volume or EFS to `/app/storage`. MediaFlow runs an automated cleanup routine that prunes files older than `FILE_EXPIRY_HOURS` (default: 24h).

---

## 4. Production Checklist

- [ ] Set `DEBUG=false` in `.env`.
- [ ] Generate a secure 32+ character `SECRET_KEY`.
- [ ] Connect production PostgreSQL: `DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/mediaflow`.
- [ ] Run database migrations: `python -m alembic upgrade head`.
- [ ] Ensure FFmpeg 7+ is installed and on system PATH.
- [ ] Configure CORS allowed origins with your actual production domain.

