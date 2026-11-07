# Vercel deployment

Root `vercel.json` is prepared for confirmation before deployment. Import the
repository root as one project, not `apps/web` alone. Target domain:
`horizon.yousefkart.com`.

## Components and routing

| Name | Kind | Source | Access |
| --- | --- | --- | --- |
| `web` | Next.js service | `apps/web` | Public `/(.*)`, with existing dashboard authentication |
| `api` | FastAPI service | `apps/api`, `src.main:app` | Internal only |
| `workers` | Container daemon | root `Dockerfile.worker` | No ingress; one instance in `iad1` |

The only binding is on `web`: `api` supplies `HORIZON_API_URL` at function
runtime. Do not configure that variable manually. The route handler reads it
per request, preserving any base path; builds, browser code and middleware do
not use it. `/api/signals?limit=20` reaches the authenticated Next.js handler,
which calls bound FastAPI `/signals?limit=20` with the server API token.
FastAPI routes have no `/api` prefix. A direct top-level `/api` rewrite would
bypass that existing proxy/authentication flow, so only `web` is exposed.
Workers call Supabase and Alpaca directly and need no service binding.

## Continuous worker

Horizon's continuous WebSocket/trading loops use a Daemon, not a request-driven
Python service. The root Dockerfile includes both `engine/` and `workers/` in
its build context and compiles/tests the Linux native executable. Compose uses
the same Dockerfile. No new queue, polling source or worker host is introduced.

Daemons currently run only in production; `vercel dev` does not start them.
One instance in `iad1` is proposed and requires confirmation. Continuous daemons
consume provisioned-memory quota while idle; check your plan before activating.
Do not scale beyond one instance or add regions.

Before promotion/redeployment with trading enabled, scale the old daemon to
zero and wait for it to stop, then deploy/start exactly one instance. Stop any
local worker using the same account. Rolling deployments can overlap old/new
instances; Horizon has no distributed coordinator lock. Scaling overrides may
persist: clear the zero-instance override when ready to start the new version.
Existing broker orders can fill while stopped; reconciliation runs on restart.

No Vercel HTTP liveness probe is configured because the worker has no HTTP
server. Monitor `/api/status` timestamps and daemon logs. Docker HEALTHCHECK
is useful locally but is not a Vercel HTTP probe. Vercel restarts exited/crashed
daemons; a stale running process requires intervention.

## Environment and database

Apply migrations to hosted Supabase first, without demonstration seeds.
Configure values in Vercel project settings, never committed `.env` files:

| Variable | Purpose |
| --- | --- |
| `APP_ENV` | `production` for deployed environments, including previews |
| `SUPABASE_URL` | Hosted project URL, not localhost/Docker hostname |
| `SUPABASE_SECRET_KEY` | Server-side Supabase secret |
| `HORIZON_API_TOKEN` | Shared API/web token, at least 32 random characters |
| `DASHBOARD_USER` | Login name; defaults to `horizon` |
| `DASHBOARD_PASSWORD` | Dashboard password, at least 16 random characters |
| `ALPACA_API_KEY_ID`, `ALPACA_API_SECRET_KEY` | Dedicated paper-account credentials for production daemon |
| `PAPER_TRADING_ENABLED` | `false` during setup and verification |

See `.env.example` for optional provider/risk/model settings. Do not set
`HORIZON_API_URL`, `API_INTERNAL_URL`, `NEXT_PUBLIC_API_URL`,
`SUPABASE_DOCKER_URL`, or `QUANT_ENGINE_PATH` in Vercel: the binding supplies the
API address and the daemon image supplies the native path. No secret belongs
in a `NEXT_PUBLIC_*` variable. Vercel project variables are shared by services;
they stay server-side but this configuration does not isolate them per service.
Use a separate database for previews; do not use live-money Alpaca credentials.

## Validation and launch

1. Confirm names, routing, binding, daemon choice and region with the user.
2. Run current `vercel dev --local` from the repository root to test services/bindings
   without cloud deployment. Configure local API credentials separately. Run
   workers locally with Docker only when needed; never duplicate a worker.
3. Run frontend lint/build and proxy regression checks:
   `node --experimental-strip-types --test apps/web/tests/api-proxy.test.mjs`.
   Build native workers: `docker build -f Dockerfile.worker -t horizon-worker .`.
4. Create a preview; verify login, `/api/ready`, feeds and portfolio. Preview
   cannot prove daemon operation. Stop duplicate workers before production.
5. Deploy production with execution disabled. Check stream/worker status,
   native analysis, fresh news/signals and portfolio updates.
6. Add `horizon.yousefkart.com` in project Domains and apply Vercel's exact DNS
   instructions at your DNS host. Verify HTTPS and login.
7. Enable paper execution after checking account, exposure and risk settings;
   verify a genuine market-open entry/fill/exit. That remains outstanding.

## Preparation checks

The config validates against the official Vercel schema and CLI 65.12.1 detects
the two services plus daemon. Proxy regression tests, ESLint and a local
production build pass. Local `vercel dev -L` startup was blocked by Windows
symlink permissions in Vercel's builder cache (the CLI prefers `--local` now).
Thus binding routing has unit coverage but is not yet verified through Vercel.
Docker Desktop was unavailable; the relocated Dockerfile is unchanged from
the previously tested image, but its new build invocation still needs a rerun.
No cloud deployment, domain change or paper execution occurred during preparation.

References: [Services](https://vercel.com/docs/services),
[bindings](https://vercel.com/docs/services/bindings),
[Daemons](https://vercel.com/docs/daemons),
[daemon configuration](https://vercel.com/docs/daemons/config-reference).
