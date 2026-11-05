-- Run with psql -v ON_ERROR_STOP=1. All test data rolls back.
begin;
do $$
declare
    event_id uuid;
    snapshot_id uuid;
begin
    insert into public.news_events(provider, provider_event_id, ticker, title, url, published_at)
    values ('alpaca', 'horizon-transaction-test', 'TEST', 'Test', 'https://example.invalid', now())
    returning id into event_id;
    if not exists (select 1 from public.pending_snapshot_events(100) where id = event_id) then
        raise exception 'missing event not recoverable';
    end if;
    insert into public.market_snapshots(news_event_id, ticker, price)
    values (event_id, 'TEST', 10) returning id into snapshot_id;
    insert into public.market_snapshots(news_event_id, ticker, price)
    values (event_id, 'TEST', 20) on conflict (news_event_id) do nothing;
    if (select count(*) from public.market_snapshots where news_event_id = event_id) <> 1
       or (select price from public.market_snapshots where id = snapshot_id) <> 10 then
        raise exception 'original snapshot not preserved';
    end if;
    if exists (select 1 from public.pending_snapshot_events(100) where id = event_id) then
        raise exception 'completed event still pending';
    end if;
    delete from public.market_snapshots where id = snapshot_id;
    update public.news_events set snapshot_attempts = 5 where id = event_id;
    if exists (select 1 from public.pending_snapshot_events(100) where id = event_id) then
        raise exception 'exhausted event still pending';
    end if;
end $$;
rollback;
