# Horizon dashboard

See the [root runbook](../../README.md) for setup and validation status and
[deployment instructions](../../docs/deployment.md) for authentication.

Run `npm ci` then `npm run dev` from this directory. Copy `.env.example` to
`.env.local` for server API configuration. Application data flows through the
Next.js `/api` proxy to FastAPI. Never put a Supabase server secret in web config.
Validate with `npm run lint` and `npm run build -- --webpack`.
