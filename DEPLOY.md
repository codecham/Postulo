# Deploying Postulo

Postulo is not deployed yet. This guide is the plan for when it is: what runs in production, where to host it for little or no money, and how to run it day to day.

## What runs in production

```
Internet ──443/80──► caddy ──► web (Next.js) ──► api (FastAPI) ──► db (PostgreSQL + pgvector)
                                                  worker (job search) ──┘
```

Everything is in [compose.prod.yaml](compose.prod.yaml):

| Service   | Role                                                                    | Exposed            |
| --------- | ----------------------------------------------------------------------- | ------------------ |
| `caddy`   | HTTPS (Let's Encrypt, renewed automatically), HTTP→HTTPS, HSTS, gzip    | ports 80 and 443   |
| `web`     | Next.js standalone server, the only thing browsers talk to             | internal only      |
| `api`     | FastAPI, one Uvicorn process, JSON logs, docs turned off                | internal only      |
| `worker`  | Daily job searches and scoring (downloads a ~500 MB model once)         | internal only      |
| `migrate` | Applies the Alembic migrations, then exits                              | none               |
| `db`      | PostgreSQL 18 with pgvector                                             | internal only      |

Every container except the database runs read-only, as a non-root user (Caddy excepted), with no Linux capabilities and `no-new-privileges`. Logs are rotated (5 × 10 MB per service).

### Resources

About **2 GB of RAM** is enough for a handful of users; **4 GB** leaves room for the worker's embedding model, PostgreSQL's cache and the builds. The images build on the server, so plan 5 GB of disk for images plus the database.

## Hosting options

Prices and free tiers change often: check them before choosing. Figures below are orders of magnitude (end of 2026).

| Option                                                       | Cost              | Runs the stack as is?                                       | Good for                          | Watch out for                                                                                                   |
| ------------------------------------------------------------ | ----------------- | ----------------------------------------------------------- | --------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| **Small VPS** (Hetzner, OVHcloud, Scaleway, Netcup...)       | ~4-7 €/month      | Yes: `make prod-up`                                         | The recommended path              | You patch the OS yourself (unattended-upgrades), and take care of backups                                       |
| **Oracle Cloud "Always Free"** (ARM VM, up to 4 cores/24 GB) | Free              | Yes (all images exist for ARM64)                            | Free hosting with real resources  | Free capacity is often unavailable in popular regions; idle free VMs can be reclaimed; needs a card to sign up  |
| **Home server / Raspberry Pi 5 + Cloudflare Tunnel**         | Free (electricity) | Yes, with the tunnel instead of Caddy's public ports       | Learning, no open router ports    | Your upload speed and uptime; keep backups off the device                                                       |
| **PaaS** (Render, Railway, Fly.io, Koyeb...)                 | Free trial, then ~5-25 $/month | No: one service per app (web, api, worker) + managed Postgres with pgvector (Neon, Supabase) | No server to maintain | Free web services sleep when idle (slow first request); the always-on worker is rarely free; several bills  |

**Recommendation**: a 4 GB VPS at a European provider. It runs this exact stack, costs about the price of a coffee per month, keeps the data in the EU (personal data: CVs), and is the most instructive to run. If it must be free, try Oracle's ARM VM first, then a home server with Cloudflare Tunnel.

## First deployment on a VPS

1. **Server**: Ubuntu or Debian LTS, 2-4 GB of RAM. Log in with an SSH key, disable password login, enable the firewall for SSH, 80 and 443 only (`ufw allow OpenSSH 80/tcp 443/tcp 443/udp`), and turn on automatic security updates (`unattended-upgrades`).
2. **Docker**: install Docker Engine and the Compose plugin from docs.docker.com.
3. **DNS**: create an `A` (and `AAAA`) record for your domain pointing to the server. A free subdomain works too (DuckDNS, or a domain you already own).
4. **Code and settings**:
   ```bash
   git clone https://github.com/codecham/Postulo.git /srv/postulo && cd /srv/postulo
   make prod-env          # creates .env.prod with random secrets
   nano .env.prod         # set DOMAIN, and the optional keys (ANTHROPIC_API_KEY...)
   ```
5. **Start**: `make prod-up`. The first build takes a few minutes; Caddy gets the certificate on the first request. Check with `make prod-ps` (every service `healthy`) and open `https://<your domain>`.
6. **Your account**: sign up in the app, or, for a private instance, set `REGISTRATION_OPEN=false` and run `docker compose -f compose.prod.yaml --env-file .env.prod exec api python -m scripts.create_user you@example.com`.

## Environment variables

Documented in [.env.prod.example](.env.prod.example). Required: `DOMAIN`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `JWT_SECRET_KEY` (≥ 32 characters). The stack refuses to start when one is missing, and the API refuses a short JWT key.

Everything else has a safe default: `REGISTRATION_OPEN`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `LOG_LEVEL`, the optional AI and Adzuna keys. The per-user limits of the paid AI features and the login limits are in [apps/api/app/core/config.py](apps/api/app/core/config.py) and can be overridden by environment variables of the same name: add them to the `x-api-environment` block of `compose.prod.yaml`.

## Updates

```bash
cd /srv/postulo
make backup            # always, before an update
git pull
make prod-up           # rebuilds the images, applies the migrations, restarts what changed
docker image prune -f  # removes the old images
```

Migrations run automatically (`migrate` service) before the API and the worker start. If something goes wrong, check out the previous commit, `make prod-up`, and restore the backup if a migration changed the data.

## Backups

`make backup` (or `scripts/backup-db.sh`) writes a compressed `pg_dump` to `backups/` and keeps the 14 most recent dumps. Run it every night with cron:

```cron
0 3 * * * cd /srv/postulo && scripts/backup-db.sh >> backups/backup.log 2>&1
```

A backup on the same disk does not survive the loss of the server: copy `backups/` elsewhere, for example with `rclone` to an object storage bucket (Backblaze B2, Cloudflare R2 and Scaleway all have free or almost free tiers for a few GB). The dumps hold personal data: keep the bucket private and, ideally, encrypt them (`rclone crypt`).

Test a restore from time to time: `make restore file=backups/postulo-<date>.dump` (it stops the API and the worker, replaces the data, and starts them again).

## Monitoring

- **Health**: `GET /health` (process up) and `GET /health/db` (database reachable) on the API; Docker restarts a service whose health check keeps failing. The worker's health check fails when its loop has not turned for 30 minutes.
- **Uptime**: point a free external monitor (UptimeRobot, Better Stack...) at `https://<your domain>/` to get an email when the site is down.
- **Logs**: `make prod-logs`. The API writes one JSON object per line, with a `request_id` that is also returned in the `X-Request-ID` header: ask a user for it to find their failing request. Ship them to a log platform later if needed (Grafana Loki, Better Stack).

## Before opening it to other users

- [ ] HTTPS works and `http://` redirects to `https://`.
- [ ] `.env.prod` has fresh secrets and is readable by root only (`chmod 600`, done by `make prod-env`).
- [ ] Nightly backups run and are copied off the server; one restore was tested.
- [ ] The Claude API key has a monthly spend limit set in the Claude Console (the app also limits each user per hour).
- [ ] `REGISTRATION_OPEN` is what you want: `false` for a private instance.
- [ ] A privacy notice says what is stored (profile, CV data, applications) and that users can ask for deletion (GDPR).
- [ ] An external uptime monitor is set up.

## Scaling notes

The stack is sized for one server, and that is deliberate. Before running several API replicas:

- The login and sign-up limits are counted **in memory** in the API process ([app/core/rate_limit.py](apps/api/app/core/rate_limit.py)). With several processes, each would count separately: move the counters to PostgreSQL or Redis first.
- Run **one** worker: it claims searches from the database queue, but one is plenty for the job boards' rate limits.
- The client IP used by the limits comes from Caddy (`X-Forwarded-For`, which Caddy overwrites so a client cannot fake it), forwarded by the web server. With another reverse proxy or a CDN, make sure it also overwrites that header.
