# ABG Horizon v2

A news-driven quantitative paper-trading monorepo:

```text
Alpaca news → ticker-specific events → snapshots and market features
  → C++ Monte Carlo → signals and revision history
  → guarded paper orders → fills / positions / realized P&L
  → FastAPI → Next.js dashboard
```

Python handles ingestion, persistence and execution; C++20 handles statistics,
rolling volatility and simulation. The dashboard shows news, signal details,
analysis charts, revision history, paper account equity, positions and trades.

## Verification status

Real Alpaca news authentication, stock snapshots, historical bars and paper
account data have been verified with local Supabase and the dashboard.
Paper execution is **disabled by default**. A real market-open entry/fill/exit
lifecycle still awaits an open session and a genuinely qualifying fresh signal.
Mocked broker tests are not evidence of real fills. Hosting and production
Supabase selection are intentionally deferred.

Validation on November 4–5, 2026:

- 33 worker and 8 API tests passed.
- All 11 migrations, seed data and three SQL regression suites passed in a fresh
  disposable database, preserving existing development data.
- C++ Release / CTest passed on Windows MSVC and Linux GCC. Local MSVC benchmark:
  approximately 33 ms for 100,000 paths × 20 sessions (machine-specific).
- ESLint, TypeScript, production webpack build and all three Docker builds passed.
- Runtime npm audit: zero vulnerabilities. Full audit retains eight moderate
  development-only reports from one typescript-eslint/minimatch chain. No
  compatible fix was offered; a forced lint downgrade was avoided.

## Setup

Requires Node.js 22+, Python 3.12, uv, Docker Desktop, CMake 3.20+ and a C++20
compiler (Visual Studio C++ tools on Windows). Docker includes its own compiler.

From the repository root:

```sh
npm ci
npx supabase start
npx supabase migration up --local
```

Copy `.env.example` to `.env`. Fill in the local Supabase URL/server secret key
and Alpaca paper-account credentials with news and IEX stock-data access.
`npx supabase status` supplies local database credentials. Never commit them.
API and workers read root `.env`; `apps/api/.env` may contain optional overrides.
For a new disposable database, `npx supabase db reset` applies migrations and
seeds but **deletes existing local data**. Seed signals cannot qualify for trades.

Build the native engine:

```sh
cmake -S engine -B build/engine
cmake --build build/engine --config Release
ctest --test-dir build/engine -C Release --output-on-failure
```

Start these in separate terminals:

```sh
# From apps/api
uv sync --frozen
uv run uvicorn src.main:app --reload --host 127.0.0.1 --port 8000

# From apps/web
npm ci
# Copy .env.example to .env.local; defaults target localhost:8000.
npm run dev

# From workers
uv sync --frozen
uv run python -m core.run
```

Open <http://localhost:3000>. Browser requests use the Next.js `/api` proxy to
FastAPI, never direct Supabase application access. If configuring an API token
locally, set matching `HORIZON_API_TOKEN` values in root `.env` and web `.env.local`.
The web application does not receive Alpaca credentials or the Supabase secret.

## Paper execution

Set `PAPER_TRADING_ENABLED=true` in root `.env` and restart workers to enable
entries and exits. Run exactly one worker per dedicated paper account. Manual
changes to Horizon-owned positions block trading for that ticker until resolved.

Entries require an open market, tradable US equity, fresh original news and
quotes, and a qualifying native signal. Defaults cap orders at $100, 1% equity,
available cash/buying power, five open tickers and whole shares. Entries use
limit orders with a 1% price allowance. Exits are a 5% loss, 10% gain or five
calendar days held, evaluated during open-market cycles. These are application
rules, not broker-held stops: the worker must run for exits to operate.
All thresholds appear in `.env.example`; live-money broker hosts are rejected.

Persisted intents, deterministic client IDs, lookup before resubmission and
transactional cumulative-fill reconciliation protect against duplicate exposure.
Unknown outcomes are retained for reconciliation. Partial fills and canceled
entries are handled explicitly. Executions represent observed cumulative-fill
deltas, not individual exchange reports; realized P&L excludes fees.

Execution disabled still permits reconciliation and portfolio collection, but
creates no entries/exits. It does not cancel existing orders or liquidate holdings.
News reconnects with backoff. Snapshot recovery is limited to five attempts;
feature enrichment to three. Malformed articles/tickers are isolated. Missing
prices cannot produce snapshots; unavailable metrics remain null. There is no
news polling or backfill.

## Data and model definitions

News uniqueness is `(provider, provider_event_id, ticker)`. Each valid provider
symbol produces a row. Summaries use provider text or a bounded plain-text
fallback; categories use keyword rules. Latency is receipt minus publication
and can show provider clock skew.

Price uses the latest trade; volume uses the current daily bar. Features use
prior completed New York sessions and split-adjusted IEX data: close-to-close
change, stock-minus-SPY return, last full-session volume / preceding 20-session
mean, and sample log-return volatility annualized by sqrt(252). Market cap and
float remain null.

The C++ model fits 20 daily log returns and simulates independent normal returns.
Scores blend 20% keyword attention with 80% simulated profit frequency. Coverage
is history count / 60, **not predictive confidence**. Missing/unsupported history
or native failure produces a watch-only baseline. This is not a causal news
model or calibrated forecast; it omits fees, slippage, liquidity and fat tails.
See [engine/README.md](engine/README.md) for the API, assumptions and benchmark.

Portfolio return/drawdown use broker performance series rather than deposit
changes. Win rate uses closed Horizon trades. Missing statistics remain
unavailable. The equity chart uses actual broker equity.

## API and health

Endpoints: `/news`, `/signals`, `/signals/{id}`, `/signals/{id}/history`,
`/portfolio`, `/portfolio/orders`, `/portfolio/trades`. Feeds use bounded
`limit`/`offset`. `/health` is public liveness; `/ready` checks database access;
`/status` exposes worker status and timestamps. From workers, run
`uv run python -m core.health` to check heartbeats and stream connectivity.

## Tests

```sh
# From workers, after building the engine
uv run python -m unittest discover -s tests -v
# From apps/api
uv run python -m unittest discover -s tests -v
# From apps/web
npm run lint
npm run build -- --webpack
npm audit --omit=dev
# From repository root
ctest --test-dir build/engine -C Release --output-on-failure
```

Rollback-only SQL tests in `supabase/tests` cover snapshot idempotency, signal
relationships/history and partial/duplicate/stale fills with realized P&L.
Run each against local Supabase after migrations, for example in PowerShell:

```powershell
Get-Content -Raw supabase/tests/paper_reconciliation.sql |
  docker exec -i supabase_db_Horizon-v2 psql -U postgres -d postgres -v ON_ERROR_STOP=1
```

After schema changes regenerate types from the root:

```sh
npx supabase gen types typescript --local > apps/web/types/database.types.ts
```

## Docker

Start Supabase, populate root `.env`, and run:

```sh
docker compose up --build -d
docker compose ps
docker compose logs --tail 100 workers
docker compose down
```

Do not also run a native worker against the same account. Set `WEB_PORT` and
`API_PORT` if development servers already occupy 3000/8000. Compose does not
manage or delete Supabase data. See [deployment runbook](docs/deployment.md).

## License

MIT
