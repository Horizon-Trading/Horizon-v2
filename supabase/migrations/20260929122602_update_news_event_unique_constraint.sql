alter table public.news_events
    drop constraint news_events_provider_event_id_unique;

alter table public.news_events
    add constraint news_events_provider_event_id_ticker_unique
    unique (provider, provider_event_id, ticker);
