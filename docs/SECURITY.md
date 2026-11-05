# MediaFlow — Security Architecture & Protections

Security is treated as a foundational requirement in MediaFlow. Below is the technical breakdown of mitigations implemented across the platform.

---

## 1. Server-Side Request Forgery (SSRF) Defense

Every user-submitted URL passes through `app.services.security`:
- **Protocol Whitelist:** Strictly `http://` and `https://`. File (`file://`), gopher, ftp, and ldap schemes are blocked before resolution.
- **DNS Resolution & Private IP Blacklisting:** Prior to issuing any network request, MediaFlow resolves the destination hostname via standard DNS and checks the resulting IP addresses against standard reserved and loopback ranges:
  - `127.0.0.0/8` (IPv4 loopback) and `::1` (IPv6 loopback)
  - `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16` (RFC 1918 Private networks)
  - `169.254.0.0/16` (Cloud metadata link-local)
- **Redirect Re-validation:** HTTP redirects are checked on every hop so requests cannot bounce into private subnets.

---

## 2. Command Injection Prevention

- MediaFlow executes external binaries (FFmpeg, FFprobe, yt-dlp) exclusively using **argument arrays** via `asyncio.create_subprocess_exec(*args)` or `subprocess.run(args)`.
- `shell=True` and string shell interpolation are strictly prohibited anywhere in the codebase.

---

## 3. Path Traversal & File Sanitization

- User-controlled titles or filenames are sanitized via regex `re.sub(r'[\\/*?:"<>|]', "", title)`.
- Files on disk are nested under cryptographically unique UUID subdirectories: `storage/{job_id}/filename.ext`.
- No user-supplied path can navigate outside the designated storage root.

---

## 4. Resource & DoS Safeguards

- **Timeout Boundaries:** Download tasks time out at 3,600s; conversions at 7,200s.
- **File Size Caps:** Hard ceiling of 2,048 MB (2 GB) on file streams.
- **Rate Limiting:** Global rate limiting enforced via `slowapi` on `/analyze` and `/downloads`.
- **Security Headers:** HTTP responses enforce `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `X-XSS-Protection`, and `Referrer-Policy`.

