create table public.portfolio_snapshots (
    id uuid primary key default gen_random_uuid(),
    captured_at timestamptz not null default now(),
    equity numeric not null,
    cash numeric not null,
    buying_power numeric not null,
    trading_enabled boolean not null,
    broker_positions jsonb not null default '[]'::jsonb,
    history jsonb,
    history_error text
);
create index portfolio_snapshots_time_idx on public.portfolio_snapshots(captured_at desc);
alter table public.portfolio_snapshots enable row level security;

create function public.portfolio_trade_stats() returns jsonb
language sql stable security invoker set search_path=public as $$
    select jsonb_build_object(
        'closed_trades',count(*) filter(where closed_at is not null),
        'winning_trades',count(*) filter(where closed_at is not null and realized_pnl>0),
        'realized_pnl',coalesce(sum(realized_pnl),0)) from public.positions;
$$;
revoke execute on function public.portfolio_trade_stats() from public,anon,authenticated;
grant execute on function public.portfolio_trade_stats() to service_role;
