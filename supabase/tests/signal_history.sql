begin;
do $$
declare
    event_id uuid;
    snapshot_id uuid;
    test_signal_id uuid;
begin
    insert into public.news_events(provider, provider_event_id, ticker, title, url, published_at)
    values ('alpaca', 'signal-transaction-test', 'TEST', 'Test', 'https://example.invalid', now()) returning id into event_id;
    insert into public.market_snapshots(news_event_id, ticker, price)
    values(event_id, 'TEST', 10) returning id into snapshot_id;
    insert into public.signals(news_event_id, market_snapshot_id, ticker, score)
    values(event_id, snapshot_id, 'TEST', 30) returning id into test_signal_id;
    update public.signals set score=30, updated_at=now() where id=test_signal_id;
    if (select count(*) from public.signal_history h where h.signal_id=test_signal_id) <> 1 then
        raise exception 'unchanged signal created extra history';
    end if;
    update public.signals set score=40 where id=test_signal_id;
    if (select count(*) from public.signal_history h where h.signal_id=test_signal_id) <> 2 then
        raise exception 'changed score not tracked';
    end if;
    begin
        update public.signals set ticker='WRONG' where id=test_signal_id;
        raise exception 'inconsistent ticker allowed';
    exception when foreign_key_violation then null;
    end;
end $$;
rollback;

