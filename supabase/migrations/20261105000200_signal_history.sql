alter table public.signals
    add column model_version text not null default 'baseline-v1',
    add column analysis jsonb not null default '{}'::jsonb,
    add column updated_at timestamptz not null default now();

update public.signals set model_version = 'seed'
where news_event_id in (select id from public.news_events where provider = 'seed');

-- Keep the most recent signal if a local development database has duplicates.
delete from public.signals older using public.signals newer
where older.news_event_id = newer.news_event_id
  and (older.created_at, older.id) < (newer.created_at, newer.id);
alter table public.signals add constraint signals_news_event_unique unique(news_event_id);

-- A signal must reference a snapshot belonging to the same news event and ticker.
alter table public.market_snapshots add constraint snapshot_event_ticker_unique unique(id, news_event_id, ticker);
alter table public.signals add constraint signals_matching_snapshot_fk
    foreign key (market_snapshot_id, news_event_id, ticker)
    references public.market_snapshots(id, news_event_id, ticker) on delete cascade;

create table public.signal_history (
    id bigint generated always as identity primary key,
    signal_id uuid not null references public.signals(id) on delete cascade,
    recorded_at timestamptz not null default now(),
    data jsonb not null
);
create index signal_history_signal_time_idx on public.signal_history(signal_id, recorded_at desc);

create function public.record_signal_history() returns trigger
language plpgsql set search_path = public as $$
begin
    if tg_op = 'INSERT' then
        insert into public.signal_history(signal_id, data) values (new.id, to_jsonb(new));
    elsif (to_jsonb(new) - 'updated_at') is distinct from (to_jsonb(old) - 'updated_at') then
        insert into public.signal_history(signal_id, data) values (new.id, to_jsonb(new));
    end if;
    return new;
end $$;
create trigger signal_history_after_write after insert or update on public.signals
for each row execute function public.record_signal_history();
insert into public.signal_history(signal_id, data) select id, to_jsonb(s) from public.signals s;

create function public.pending_signal_events(batch_size integer default 20)
returns setof public.news_events language sql stable security invoker set search_path = public as $$
    select n.* from public.news_events n
    where n.provider = 'alpaca'
      and exists(select 1 from public.market_snapshots m where m.news_event_id = n.id)
      and not exists(select 1 from public.signals s where s.news_event_id = n.id)
    order by n.received_at, n.id limit greatest(1, least(batch_size, 100));
$$;
revoke execute on function public.pending_signal_events(integer) from public, anon, authenticated;
grant execute on function public.pending_signal_events(integer) to service_role;
