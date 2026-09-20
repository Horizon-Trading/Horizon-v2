-- NEWS EVENTS
create table public.news_events (
    id uuid primary key default gen_random_uuid(),

    ticker text not null,
    title text not null,
    url text unique not null,

    published_at timestamptz not null,

    event_type text,
    summary text,

    raw_data jsonb,

    created_at timestamptz not null default now()
);


create index news_events_ticker_idx
    on public.news_events (ticker);

create index news_events_published_at_idx
    on public.news_events (published_at desc);


-- MARKET SNAPSHOTS
create table public.market_snapshots (
    id uuid primary key default gen_random_uuid(),

    news_event_id uuid
        references public.news_events(id)
        on delete cascade,

    ticker text not null,

    price double precision not null,

    volume bigint,
    relative_volume double precision,

    market_cap bigint,
    float_shares bigint,

    captured_at timestamptz not null default now()
);


create index market_snapshots_news_event_id_idx
    on public.market_snapshots (news_event_id);

create index market_snapshots_ticker_idx
    on public.market_snapshots (ticker);


-- SIGNALS
create table public.signals (
    id uuid primary key default gen_random_uuid(),

    news_event_id uuid
        references public.news_events(id)
        on delete cascade,

    market_snapshot_id uuid
        references public.market_snapshots(id)
        on delete set null,

    ticker text not null,

    score double precision,
    confidence double precision,

    expected_return double precision,
    probability_profit double precision,

    created_at timestamptz not null default now()
);


create index signals_news_event_id_idx
    on public.signals (news_event_id);

create index signals_ticker_idx
    on public.signals (ticker);

create index signals_created_at_idx
    on public.signals (created_at desc);
