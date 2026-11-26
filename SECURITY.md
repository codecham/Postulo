# Security policy

## Reporting a vulnerability

Please do not open a public issue for security problems. Email **59926750+codecham@users.noreply.github.com** with a description, the steps to reproduce and the impact. You will get an answer within a few days.

## Built-in protections

- Passwords are hashed with Argon2; failed logins take the same time whether the account exists or not.
- Access tokens are signed JWTs with an expiry; the signing key is generated per environment and must be at least 32 characters.
- In the browser, the token lives in an httpOnly, SameSite=Lax cookie (Secure in production), unreadable by JavaScript.
- Secrets are only read from the environment; `.env` is never committed and `make setup` generates new random secrets.
- Containers run as non-root users and ports are published on `127.0.0.1` only.
- Security headers on every page (`Content-Security-Policy` in production, `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy`) and on every API response; HSTS from the Caddy reverse proxy.
- Brute-force protection: login attempts are limited per client IP and failed logins per email; sign-ups are limited per IP. Sign-up can be closed (`REGISTRATION_OPEN=false`).
- Paid AI features (CV import, tailored applications) and manual job searches are limited per user.
- Request bodies are capped (413 above the CV upload size), and every text field has a maximum length.
- Every query on user data filters on the logged-in user; another user's id answers 404, never 403.
- Links from job boards are kept only when they are `http(s)`; text written into PDFs is escaped.
- In production the API docs (`/docs`, `/openapi.json`) are off, only Caddy publishes ports, and containers are read-only with no Linux capabilities.

## Not included (add them before going to production if you need them)

- Email verification and password reset.
- Rate limits shared between several API processes (the counters live in memory: run one API container, see [DEPLOY.md](DEPLOY.md)).
- Token revocation (logging out deletes the cookie; the token itself stays valid until it expires).
