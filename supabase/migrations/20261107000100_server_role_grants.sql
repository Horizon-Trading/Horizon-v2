-- Hosted projects need explicit Data API privileges. RLS bypass alone does
-- not grant table access. Only Horizon's server role receives these grants.
grant usage on schema public to service_role;
grant select, insert, update on table
    public.news_events,
    public.market_snapshots,
    public.signals,
    public.signal_history,
    public.orders,
    public.executions,
    public.positions,
    public.portfolio_snapshots,
    public.worker_status
to service_role;
grant usage, select on sequence
    public.signal_history_id_seq,
    public.executions_id_seq
to service_role;
