alter table public.news_events
    add column provider text not null,
    add column provider_event_id text not null,
    add column source text,
    add column author text,
    add column received_at timestamptz not null default now();

alter table public.news_events
    add constraint news_events_provider_event_id_unique
    unique (provider, provider_event_id);
