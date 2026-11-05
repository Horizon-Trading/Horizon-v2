alter table public.market_snapshots
    add column price_change double precision,
    add column market_adjusted_return double precision,
    add column volatility double precision,
    add column price_observed_at timestamptz,
    add column feature_data jsonb not null default '{}'::jsonb;
