# MediaFlow — Development Setup & Quickstart

MediaFlow is designed for zero-friction local development. No Redis or PostgreSQL containers are required to start working immediately.

---

## Prerequisites
- **Python 3.11+**
- **Node.js 18+** & npm
- **FFmpeg & FFprobe** installed and on system PATH

---

## 1. Backend Setup

```powershell
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Run backend unit & integration tests
python -m pytest tests -v

# Start development server (auto-reloads on port 8000)
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Interactive API documentation will be available at:
- Swagger UI: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/api/v1/health`

---

## 2. Frontend Setup

```powershell
# Navigate to frontend directory
cd frontend

# Install Node dependencies
npm install

# Build for production verification
npm run build

# Start Next.js development server (port 3000)
npm run dev
```

The web application will be accessible at: `http://localhost:3000`

---

## 3. Production Deployment with Docker

To run the complete production stack with Docker Compose:

```bash
docker-compose -f docker/docker-compose.yml up --build -d
```

