create table public.orders (
    id uuid primary key default gen_random_uuid(),
    signal_id uuid references public.signals(id),
    entry_order_id uuid references public.orders(id),
    client_order_id text not null unique,
    broker_order_id text unique,
    ticker text not null,
    purpose text not null check (purpose in ('entry','exit')),
    side text not null check (side in ('buy','sell')),
    quantity numeric not null check (quantity > 0),
    status text not null default 'pending_submit',
    filled_quantity numeric not null default 0 check (filled_quantity >= 0),
    filled_avg_price numeric,
    broker_updated_at timestamptz,
    exposure_closed boolean not null default false,
    reason text not null,
    error text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    check ((purpose='entry' and side='buy' and entry_order_id is null and signal_id is not null)
        or (purpose='exit' and side='sell' and entry_order_id is not null)),
    check (filled_quantity <= quantity),
    check (filled_quantity = 0 or filled_avg_price > 0)
);
create unique index orders_one_entry_per_signal on public.orders(signal_id) where purpose='entry';
create unique index orders_one_active_exposure on public.orders(ticker) where purpose='entry' and not exposure_closed;
create unique index orders_one_active_exit on public.orders(entry_order_id)
    where purpose='exit' and status not in ('filled','canceled','expired','rejected');
create index orders_created_idx on public.orders(created_at desc);

-- Executions are observed fill deltas from broker cumulative quantities/notional.
-- They are not claimed to be individual exchange execution reports.
create table public.executions (
    id bigint generated always as identity primary key,
    order_id uuid not null references public.orders(id),
    cumulative_quantity numeric not null,
    quantity numeric not null check(quantity > 0),
    price numeric not null check(price > 0),
    source text not null default 'broker_cumulative_fill_delta',
    observed_at timestamptz not null default now(),
    unique(order_id,cumulative_quantity)
);

create table public.positions (
    entry_order_id uuid primary key references public.orders(id),
    ticker text not null,
    quantity numeric not null check(quantity >= 0),
    avg_entry_price numeric not null check(avg_entry_price > 0),
    realized_pnl numeric not null default 0,
    opened_at timestamptz not null,
    closed_at timestamptz,
    updated_at timestamptz not null default now()
);
create unique index positions_one_open_ticker on public.positions(ticker) where quantity>0;

create or replace function public.apply_paper_order_state(
    local_order_id uuid, broker_id text, broker_status text,
    cumulative_quantity numeric, average_price numeric, broker_timestamp timestamptz
) returns void language plpgsql set search_path=public as $$
declare
    previous public.orders;
    entry public.orders;
    entry_id uuid;
    sold numeric;
    proceeds numeric;
    remaining numeric;
    delta_qty numeric;
    delta_notional numeric;
begin
    select * into strict previous from public.orders where id=local_order_id for update;
    entry_id := case when previous.purpose='entry' then previous.id else previous.entry_order_id end;
    perform 1 from public.orders where id=entry_id for update;
    if cumulative_quantity is null or cumulative_quantity<0 or cumulative_quantity::text in ('NaN','Infinity','-Infinity')
       or broker_timestamp is null then raise exception 'invalid broker state'; end if;
    if previous.broker_updated_at is not null and broker_timestamp < previous.broker_updated_at then return; end if;
    if previous.broker_order_id is not null and previous.broker_order_id<>broker_id then raise exception 'broker order identity changed'; end if;
    if cumulative_quantity < previous.filled_quantity or cumulative_quantity > previous.quantity then raise exception 'invalid cumulative fill'; end if;
    if cumulative_quantity > 0 and (average_price is null or average_price<=0) then raise exception 'missing fill price'; end if;
    delta_qty := cumulative_quantity-previous.filled_quantity;
    if delta_qty>0 then
        delta_notional := cumulative_quantity*average_price-previous.filled_quantity*coalesce(previous.filled_avg_price,0);
        if delta_notional<=0 then raise exception 'invalid fill notional'; end if;
        insert into public.executions(order_id,cumulative_quantity,quantity,price)
        values(local_order_id,cumulative_quantity,delta_qty,delta_notional/delta_qty)
        on conflict on constraint executions_order_id_cumulative_quantity_key do nothing;
    end if;
    update public.orders set broker_order_id=broker_id,status=broker_status,
        filled_quantity=cumulative_quantity,filled_avg_price=average_price,
        broker_updated_at=broker_timestamp,error=null,updated_at=now(),
        exposure_closed=case when purpose='exit' then broker_status in ('filled','canceled','expired','rejected') else exposure_closed end
        where id=local_order_id;
    select * into strict entry from public.orders where id=entry_id;
    select coalesce(sum(filled_quantity),0),coalesce(sum(filled_quantity*filled_avg_price),0)
        into sold,proceeds from public.orders where entry_order_id=entry_id and purpose='exit';
    remaining := entry.filled_quantity-sold;
    if remaining<0 then raise exception 'exit fills exceed entry fills'; end if;
    if entry.filled_quantity>0 then
        insert into public.positions(entry_order_id,ticker,quantity,avg_entry_price,realized_pnl,opened_at,closed_at)
        values(entry_id,entry.ticker,remaining,entry.filled_avg_price,
            proceeds-sold*entry.filled_avg_price,coalesce(entry.broker_updated_at,entry.created_at),
            case when remaining=0 then now() else null end)
        on conflict(entry_order_id) do update set quantity=excluded.quantity,
            avg_entry_price=excluded.avg_entry_price,realized_pnl=excluded.realized_pnl,
            closed_at=case when excluded.quantity=0 then coalesce(positions.closed_at,excluded.closed_at) else null end,
            updated_at=now();
    end if;
    update public.orders set exposure_closed=(remaining=0 and entry.status in ('filled','canceled','expired','rejected')) where id=entry_id;
end $$;
revoke execute on function public.apply_paper_order_state(uuid,text,text,numeric,numeric,timestamptz) from public,anon,authenticated;
grant execute on function public.apply_paper_order_state(uuid,text,text,numeric,numeric,timestamptz) to service_role;
alter table public.orders enable row level security;
alter table public.executions enable row level security;
alter table public.positions enable row level security;
