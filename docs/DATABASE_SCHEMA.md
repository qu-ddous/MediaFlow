# MediaFlow — Database Schema & Architecture

MediaFlow utilizes SQLAlchemy 2.0 with asynchronous drivers (`aiosqlite` for local development, `asyncpg` for PostgreSQL in production), managed by Alembic database migrations.

---

## Entity Relationship Overview

```mermaid
erDiagram
    users {
        uuid id PK
        string email
        string hashed_password
        string role
        boolean is_active
        string preferred_format
        string preferred_quality
        timestamp created_at
        timestamp updated_at
    }

    download_jobs {
        uuid id PK
        string source_url
        string source_type
        string status
        string title
        string thumbnail_url
        float duration
        string requested_format
        string requested_quality
        bigint file_size
        string output_path
        text error_message
        float progress
        string download_speed
        timestamp expires_at
        timestamp created_at
        timestamp updated_at
    }

    media_metadata {
        uuid id PK
        uuid job_id FK
        string title
        string thumbnail_url
        float duration
        string source_name
        string media_type
        json available_formats
        json available_resolutions
        json available_audio
        json subtitles
        string original_format
    }

    conversion_jobs {
        uuid id PK
        uuid source_job_id FK
        string status
        string input_format
        string output_format
        string input_codec
        string output_codec
        string resolution
        string bitrate
        string input_path
        string output_path
        float progress
        text error_message
        timestamp created_at
        timestamp updated_at
    }

    download_history {
        uuid id PK
        uuid job_id FK
        string title
        string file_name
        string file_format
        bigint file_size
        string source_url
        string status
        timestamp created_at
    }

    system_settings {
        uuid id PK
        string key
        text value
        string description
        timestamp created_at
        timestamp updated_at
    }

    audit_logs {
        uuid id PK
        string action
        string ip_address
        string user_agent
        json details
        timestamp created_at
    }

    download_jobs ||--o| media_metadata : "stores"
    download_jobs ||--o{ conversion_jobs : "references"
    download_jobs ||--o| download_history : "records"
```

---

## Tables & Column Definitions

### 1. `users`
Stores user profile, authentication, role access control, and user format preferences.
- `id`: UUID (Primary Key)
- `email`: VARCHAR(255), Unique, Indexed
- `hashed_password`: VARCHAR(255)
- `role`: VARCHAR(32) [admin, user, guest]
- `is_active`: BOOLEAN (Default True)
- `preferred_format`: VARCHAR(32) (e.g. mp4, mp3)
- `preferred_quality`: VARCHAR(32) (e.g. 1080p, 320k)
- `created_at`, `updated_at`: TIMESTAMP WITH TIME ZONE

### 2. `download_jobs`
Primary operational table tracking each active and completed media download.
- `id`: UUID (Primary Key)
- `source_url`: VARCHAR(2048)
- `status`: ENUM [pending, analyzing, downloading, processing, completed, failed, cancelled]
- `title`: VARCHAR(512)
- `thumbnail_url`: VARCHAR(2048)
- `duration`: FLOAT (in seconds)
- `requested_format`: VARCHAR(32)
- `requested_quality`: VARCHAR(32)
- `file_size`: BIGINT
- `output_path`: VARCHAR(1024)
- `progress`: FLOAT (0.0 to 100.0)
- `download_speed`: VARCHAR(64)
- `expires_at`: TIMESTAMP WITH TIME ZONE (Default +24 Hours)

### 3. `conversion_jobs`
Tracks media transcoding, container conversion, resolution downscaling, and audio extraction.
- `id`: UUID (Primary Key)
- `source_job_id`: UUID (Foreign Key -> download_jobs.id, Nullable for local uploads)
- `input_path`: VARCHAR(1024)
- `output_path`: VARCHAR(1024)
- `output_format`: VARCHAR(32)
- `resolution`: VARCHAR(32)
- `progress`: FLOAT

### 4. `system_settings`
Dynamic runtime configuration (e.g., max file size limits, banner notices, rate limit overrides).
- `key`: VARCHAR(128), Unique, Indexed
- `value`: TEXT
- `description`: VARCHAR(255)

---

## Migration Commands
```bash
# Generate new migration when models change:
python -m alembic revision --autogenerate -m "description"

# Apply pending migrations:
python -m alembic upgrade head
```

