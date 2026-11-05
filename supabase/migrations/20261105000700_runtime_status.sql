create table public.worker_status (
    component text primary key,
    status text not null,
    error text,
    updated_at timestamptz not null default now()
);
alter table public.worker_status enable row level security;
alter table public.market_snapshots add column feature_attempts integer not null default 0;
alter table public.market_snapshots add column next_feature_attempt_at timestamptz not null default now();
alter table public.news_events enable row level security;
alter table public.market_snapshots enable row level security;
alter table public.signals enable row level security;
alter table public.signal_history enable row level security;
