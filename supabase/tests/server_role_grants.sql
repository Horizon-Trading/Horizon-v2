begin;
set local role service_role;
-- Reproduces the deployed readiness query under the actual API role.
select id from public.signals limit 1;
do $$
declare table_name text;
begin
    foreach table_name in array array[
        'news_events', 'market_snapshots', 'signals', 'signal_history',
        'orders', 'executions', 'positions', 'portfolio_snapshots', 'worker_status'
    ] loop
        if not has_table_privilege(current_user, 'public.' || table_name, 'SELECT')
           or not has_table_privilege(current_user, 'public.' || table_name, 'INSERT')
           or not has_table_privilege(current_user, 'public.' || table_name, 'UPDATE') then
            raise exception 'Missing server privileges on %', table_name;
        end if;
    end loop;
    if not has_sequence_privilege(current_user, 'public.signal_history_id_seq', 'USAGE')
       or not has_sequence_privilege(current_user, 'public.executions_id_seq', 'USAGE') then
        raise exception 'Missing server sequence privileges';
    end if;
end;
$$;
rollback;
