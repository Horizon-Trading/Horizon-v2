-- Retain the first snapshot for each event, preserving existing signal links.
update public.signals s
set market_snapshot_id = first_snapshot.id
from public.market_snapshots old_snapshot,
     lateral (
         select id from public.market_snapshots
         where news_event_id = old_snapshot.news_event_id
         order by captured_at, id limit 1
     ) first_snapshot
where s.market_snapshot_id = old_snapshot.id
  and old_snapshot.id <> first_snapshot.id;

delete from public.market_snapshots later
using public.market_snapshots earlier
where later.news_event_id = earlier.news_event_id
  and (later.captured_at, later.id) > (earlier.captured_at, earlier.id);

alter table public.market_snapshots
    add constraint market_snapshots_news_event_unique unique (news_event_id);

alter table public.news_events
    add column snapshot_attempts integer not null default 0 check (snapshot_attempts >= 0),
    add column next_snapshot_attempt_at timestamptz not null default now(),
    add column snapshot_error text;

create index news_events_snapshot_retry_idx
    on public.news_events (next_snapshot_attempt_at)
    where snapshot_attempts < 5;

-- Recovery scans persisted events only, never the provider's historical news API.
create function public.pending_snapshot_events(batch_size integer default 20)
returns setof public.news_events
language sql stable security invoker set search_path = public
as $$
    select n.* from public.news_events n
    where n.provider = 'alpaca'
      and n.snapshot_attempts < 5
      and n.next_snapshot_attempt_at <= now()
      and not exists (select 1 from public.market_snapshots m where m.news_event_id = n.id)
    order by n.next_snapshot_attempt_at, n.id
    limit greatest(1, least(batch_size, 100));
$$;
revoke execute on function public.pending_snapshot_events(integer) from public, anon, authenticated;
grant execute on function public.pending_snapshot_events(integer) to service_role;
