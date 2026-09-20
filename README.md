# Horizon 2.0

Horizon 2.0 is an event-driven quantitative trading system focused on market news, real-time analysis, trading signals, and paper trading.

This repository is a ground-up rewrite of the original project using a simpler monorepo architecture and a C++ quantitative engine.

## Structure

```text
apps/
  api/        FastAPI backend
  web/        Next.js dashboard

engine/       C++ quantitative engine
workers/      News, market data, and trading workers
supabase/     Database migrations and local configuration
```

## Tech Stack

* Next.js / TypeScript
* FastAPI / Python
* C++20 / CMake
* PostgreSQL / Supabase
* Docker

## Development

Install dependencies:

```bash
npm install

cd apps/web
npm install

cd ../api
uv sync
```

Start Supabase from the project root:

```bash
npx supabase start
```

Environment templates are provided in:

```text
.env.example
apps/api/.env.example
apps/web/.env.example
```

## Status

Early development.

## License

MIT
