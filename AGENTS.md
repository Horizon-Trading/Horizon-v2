# ABG Horizon v2 — Agent Context

## Goal

ABG Horizon is an event-driven quantitative paper-trading system.

The intended pipeline is:

News → Market Snapshot → Quant Analysis → Signal → Paper Trade → Portfolio / Dashboard

The project is a hobby/portfolio project. Optimize for a clean, working system rather than enterprise-scale architecture.

## Important Principles

- Keep everything in this monorepo.
- Do not introduce microservices or additional repositories.
- Prefer simple, readable implementations over abstractions.
- Do not create classes where a stateless function is sufficient.
- Do not add infrastructure unless it is needed by the current feature.
- Preserve existing project structure and conventions unless there is a clear technical reason to change them.
- Do not rewrite working code simply to make it stylistically different.
- Complete one coherent task at a time.
- Before modifying something, inspect the relevant existing files.
- After changes, run the relevant tests/type checks/builds where practical.
- If a schema change is required, create a Supabase migration rather than editing an old migration.
- Local development data may be discarded; production migration compatibility is not currently important.

## Repository Structure

```text
Horizon-v2/
├── apps/
│   ├── api/              # FastAPI
│   └── web/              # Next.js / TypeScript
├── engine/               # C++20 quantitative engine
├── workers/
│   ├── core/             # Worker orchestration
│   ├── news/             # News ingestion / processing
│   └── market_data/      # Market data collection
├── supabase/
│   ├── migrations/
│   └── seed.sql
├── .env
└── AGENTS.md
```

Inspect the repository before assuming exact file names or structure.

## Technologies

- Frontend: Next.js / TypeScript
- API: FastAPI / Python
- Workers: Python managed with uv
- Database: Supabase / PostgreSQL
- Quant engine: C++20 / CMake
- News / market data / paper trading: Alpaca
- Local Supabase runs through the Supabase CLI

## Python

The API and workers are separate uv projects with their own `pyproject.toml` and `uv.lock`.

Workers should normally be run from:

```powershell
cd workers
uv run python -m core.run
```

Configuration is centralized through Pydantic Settings.

The workers read shared secrets/configuration from the root `.env`.

Avoid scattering `os.environ` or `load_dotenv()` calls through individual modules.

## Supabase

Database tables currently include:

- `news_events`
- `market_snapshots`
- `signals`

Supabase migrations are the schema source of truth.

For local schema changes:

```powershell
npx supabase migration new <migration_name>
npx supabase db reset
```

The Next.js Supabase types should be regenerated after schema changes.

The API/workers use the Supabase secret key server-side.

Never expose the secret key to the frontend.

## News Pipeline

The primary news source is Alpaca's real-time news WebSocket.

Do not implement polling/backfill unless explicitly requested.

Alpaca already provides ticker symbols in the `symbols` array. Do not reintroduce LLM/manual ticker extraction.

A multi-symbol article is normalized into one `news_events` row per ticker.

News row uniqueness is based on:

```text
(provider, provider_event_id, ticker)
```

A URL is not unique because one article may correspond to multiple ticker-specific rows.

Current conceptual flow:

```text
Alpaca WebSocket
    ↓
stream_news()
    ↓
core orchestration
    ↓
process_news()
    ↓
normalize_article()
    ↓
save_event()
    ↓
news_events
```

`news_events` contains provider metadata, ticker, title, URL, timestamps, summary, raw provider data, etc.

Keep the original provider payload in `raw_data`, but only promote regularly queried/analyzed values to dedicated columns.

## Market Data

After a `news_event` row is saved, Horizon captures a market snapshot for its ticker.

Alpaca's stock snapshot endpoint is being used.

Current intended data includes:

- `news_event_id`
- `ticker`
- `price`
- `volume`
- `relative_volume`
- `market_cap`
- `float_shares`
- `captured_at`

Not all fields are implemented yet.

For the first working version:

- Price can use Alpaca `latestTrade.p`
- Volume can use current session volume
- Do not invent relative volume, market cap, or float values
- Missing values should remain null until implemented correctly

The snapshot must reference the persisted `news_events.id`, not the pre-insert normalized dictionary.

## Signal Engine

The API and frontend already use `signals` as the main joined/displayed domain object.

The intended relationship is:

```text
signal
├── news_event
└── market_snapshot
```

The API should expose domain-oriented routes such as:

```text
GET /signals
GET /signals/{id}
```

rather than generic database-oriented endpoints.

Signal generation has not yet been fully implemented.

The first version does not need a sophisticated quant model. Establish the complete pipeline first, then improve scoring.

## C++ Engine

C++ exists because Horizon should contain meaningful compute-heavy quantitative work, not merely to list C++ as a technology.

Planned areas include:

- Monte Carlo simulation
- volatility/statistical analysis
- risk calculations
- rolling market statistics
- benchmarks

Do not rewrite ingestion, APIs, database access, or ordinary orchestration in C++.

Do not prematurely build the entire C++ engine.

First complete the basic Python end-to-end trading pipeline. Then implement one meaningful C++ quantitative component and integrate it.

## API

FastAPI sits between the frontend and the database/domain data.

The frontend should not bypass FastAPI for Horizon application data merely because Supabase supports direct browser access.

Existing health connectivity has already been tested:

```text
Next.js → FastAPI
FastAPI → Supabase
```

Keep routes thin and move reusable application logic out of route handlers where appropriate.

## Frontend

The web app is currently intentionally simple.

Functionality matters more than design.

Prefer clean basic UI over spending time on styling.

The dashboard should ultimately show:

- signals
- related news
- market snapshot information
- paper trades
- portfolio performance

## Paper Trading

Alpaca paper trading will be used.

Later tables/domain objects will include:

- orders
- executions
- positions
- portfolio snapshots / trade outcomes as needed

Do not begin paper trading until signal creation works end-to-end.

## Current Development State

Already substantially complete:

- monorepo
- Next.js
- FastAPI
- local Supabase
- environment setup
- API ↔ frontend connectivity
- API ↔ Supabase connectivity
- initial database schema
- seed data
- generated TypeScript DB types
- Alpaca real-time news WebSocket
- news normalization
- ticker handling using Alpaca `symbols`
- duplicate protection
- storing live `news_events`

Currently in progress:

```text
news_event
    ↓
capture market snapshot
    ↓
store market_snapshot
```

The current priority is to make that path reliable.

After that:

```text
news_event + market_snapshot
    ↓
signal
    ↓
API
    ↓
dashboard
```

## Priority Order

Work in this order unless explicitly told otherwise.

### P0 — Complete the current vertical slice

1. Verify live news ingestion remains stable.
2. Capture and persist a market snapshot for every ticker-specific news event.
3. Make multi-symbol news events work correctly.
4. Add basic handling so one malformed ticker/article does not kill the long-running stream.
5. Verify relationships in Supabase.

### P1 — Signals

1. Create a simple first-pass signal from a news event + market snapshot.
2. Persist it in `signals`.
3. Return joined signal/news/snapshot data through FastAPI.
4. Display real live signals in Next.js.

Do not block this stage on sophisticated quantitative modeling.

### P2 — Market features

Add correct implementations for:

- price change
- relative volume
- market-adjusted return
- volatility

Do not store fake placeholder metrics.

### P3 — C++ quant engine

Implement one meaningful compute-heavy feature first.

Preferred first candidate:

- Monte Carlo event-response simulation

Add:

- clean C++ API
- Python integration
- benchmarks
- unit tests

Then incorporate its output into signal generation.

### P4 — Paper trading

1. Connect Alpaca paper trading.
2. Add required order/execution/position schema.
3. Execute only qualifying signals.
4. Track open positions.
5. Implement simple explicit exit rules.
6. Persist realized P&L.

### P5 — Portfolio dashboard

Expose and display:

- account equity
- open positions
- trade history
- return
- win rate
- drawdown
- equity curve

### P6 — Hardening / deployment

Only after the full pipeline works:

- retries
- structured logging
- critical tests
- deployment
- production Supabase
- README screenshots/results

## Scope Control

This project needs to reach a finished state quickly.

When choosing between:

A. a sophisticated subsystem that delays the complete pipeline

and

B. a simple correct implementation that allows the next stage to work

prefer B.

Leave obvious extension points, but do not implement hypothetical future requirements.

## Working Style

For each requested task:

1. Inspect the relevant code first.
2. Briefly state what you found.
3. Implement the smallest coherent solution.
4. Update related tests/types/migrations if required.
5. Run appropriate verification.
6. Report:
   - what changed
   - files changed
   - commands/tests run
   - anything still unresolved

Do not automatically continue into the next major checklist item unless asked.
