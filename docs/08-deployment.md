# 08 — Deployment

> **Decision pending; nothing is deployed.** No live URL exists yet. The application
> will not be described as "deployed" anywhere until a deployment succeeds and its URL
> is verified in a fresh incognito session.

## What the brief allows

The brief permits **Vercel or Heroku**. Docker is required for reproducible local development, and the backend is a Dockerized Python service — so the production backend host must support either a container or a standard Python web process.

## Planned architecture: split frontend / backend

- **Frontend → Vercel.** The React app builds to static assets; Vercel serves them well and cheaply. The backend base URL is injected at build time via `VITE_API_URL`.
- **Backend → a Docker-capable host.** The service is containerized; the specific host is **being finalized**. Candidates and trade-offs:

| Host | Cost | Cold start | Docker | Notes |
|---|---|---|---|---|
| Render (free) | $0 | ~30–60s after idle | ✅ | Simplest; warm before demo recording |
| Fly.io (1 always-on machine) | $0 within allowance | **None** | ✅ | Free + no cold start; a little more CLI setup |
| Heroku Eco | $5/mo | sleeps after 30 min | ✅ | Named in brief, but paid *and* still sleeps |
| Heroku Basic | $7/mo | none | ✅ | Named in brief, always-on |

A single-platform alternative (**whole app on Heroku**) is also viable and maps most literally to the brief; it trades the modern split architecture for one platform and one URL.

The chosen option, and the reasons, will be recorded here once committed, along with any platform limitations relevant to Python/Docker.

## Environment variables

| Variable | Side | Purpose |
|---|---|---|
| `VITE_API_URL` | frontend (build) | Base URL of the backend API |
| `ELEXON_BASE_URL` | backend | Elexon API base (overridable for tests) |
| `PURCHASE_CUTOFF_*` | backend | Configurable purchasing cutoff (see [04 — Methodology](04-methodology.md)) |
| `CORS_ALLOWED_ORIGINS` | backend | Must include the deployed frontend origin |
| `PORT` | backend | Provided by the host |

No secrets are committed; `.env.example` documents the variables without values.

## Deployment steps (to be finalized)

1. Build and push the backend container to the chosen host; set backend env vars; confirm `/api/health` returns `ok`.
2. Set `CORS_ALLOWED_ORIGINS` to the Vercel frontend origin.
3. Deploy the frontend to Vercel with `VITE_API_URL` pointing at the live backend.
4. If the backend host cold-starts, **warm it** before recording the demo.
5. **Verify in incognito**: frontend loads, calls succeed, no auth/access gaps. Only then record the live URL in the README and here.

## Frontend ↔ backend connection

The frontend only ever talks to the backend API (never Elexon directly). CORS on the backend is restricted to the known frontend origin.
