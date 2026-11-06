# MediaFlow — Testing Guide

MediaFlow maintains an automated test suite verifying security controls, SSRF protections, API contracts, and media workflows.

---

## 1. Running Backend Tests

Backend tests are executed via `pytest` with `pytest-asyncio` against an in-memory SQLite database:

```powershell
# Navigate to backend directory
cd backend

# Execute all tests with verbose output
python -m pytest tests -v
```

### Test Coverage Highlights:
- **`tests/test_security.py`**:
  - Validates `http://` and `https://` schemas.
  - Blocks dangerous schemes (`file://`, `gopher://`, `ftp://`).
  - Verifies loopback (`127.0.0.1`), private RFC 1918 subnets (`10.0.0.1`, `192.168.1.1`, `172.16.0.1`), and cloud metadata (`169.254.169.254`).
  - Tests directory traversal prevention (`../../../etc/passwd`).
  - Tests allowed file extensions whitelist.
- **`tests/test_api.py`**:
  - Validates `/` root, `/api/v1/health`, and `/api/v1/capabilities`.
  - Tests download job creation, retrieval, cancellation, and status lifecycle.
- **`tests/test_analyzer.py`**:
  - Tests SSRF rejection on `/analyze`.
  - Tests direct stream inspection and response structures.

---

## 2. Running Frontend Builds

```powershell
cd frontend

# Verify TypeScript types and production Next.js compilation:
npm run build
```
All routes are verified as static or dynamic prerenders with zero build warnings.

