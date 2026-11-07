# Deployment runbook

Vercel is selected; remote deployment is not yet verified. See
[Vercel setup](vercel.md) for services, bindings, daemon and domain configuration.
The alternative Compose deployment unit is three
Docker images in this monorepo: web, API and one long-running worker. The worker
needs persistent execution, outbound WebSocket/HTTPS and its native binary;
it is not a short-lived serverless job.

1. Select container hosting with HTTPS termination and a Supabase project.
2. Apply checked-in migrations using the Supabase CLI. Do not load demonstration
   seeds into production. Verify `/ready` after migration.
3. Supply Supabase server and Alpaca paper credentials as runtime secrets to
   API/workers. Set `SUPABASE_DOCKER_URL` to the actual project URL. Build contexts
   exclude `.env` files.
4. Set `APP_ENV=production`, random `HORIZON_API_TOKEN` (at least 32 characters),
   `DASHBOARD_PASSWORD` (at least 16 characters), and optional `DASHBOARD_USER`.
   Supply matching API tokens to API and web. Production API startup fails
   without a token; web refuses access without its protection configuration.
   Dashboard HTTP Basic authentication requires HTTPS outside localhost.
5. Keep API internal and route HTTPS to web. Compose publishes only on loopback
   for a host reverse proxy; adapt networking to the chosen host. The web server
   proxies to `API_INTERNAL_URL`; its token stays server-only. Application tables
   have RLS enabled; the frontend never uses a database server secret.
6. Run `docker compose up --build -d`. Verify authenticated dashboard access,
   `/api/ready`, news/signals, portfolio and worker timestamps at `/api/status`.
   Run one worker. Docker health checks report unhealthy processes but do not
   restart them automatically; configure host alerts for stale/unhealthy workers.
   Restart policies handle exited processes.
7. Keep execution disabled until credentials, dedicated account, fresh signals,
   risk limits and broker exposure have been checked. Disabling execution does
   not cancel orders or close positions; inspect existing exposure explicitly.
8. Re-run audits/tests before publication. Verify an actual fresh-signal paper
   entry/fill/exit and matching database/dashboard state. This external-session
   verification remains outstanding as of November 5, 2026 UTC.

For local operation leave `APP_ENV=development`; access protection is optional
unless credentials are configured. Production-mode smoke tests use temporary
credentials on alternate local ports and do not publish anything.

Known dependency limitation: runtime npm audit passed with zero findings on
November 5, 2026. Eight moderate development-only reports remain in one
minimatch/typescript-eslint chain. Track compatible upstream fixes rather than
forcing a mismatched Next lint configuration.

Back up the chosen database before migration. Stop/restart Compose services
without resetting Supabase. Migrations remain the schema source of truth.
