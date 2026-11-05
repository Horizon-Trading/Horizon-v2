begin;
do $$
declare
    n uuid; m uuid; s uuid; entry_id uuid; exit_id uuid; exit2_id uuid;
    observed timestamptz := now();
begin
    insert into public.news_events(provider,provider_event_id,ticker,title,url,published_at)
    values('test','paper-test','TEST','Test','https://example.invalid',now()) returning id into n;
    insert into public.market_snapshots(news_event_id,ticker,price) values(n,'TEST',100) returning id into m;
    insert into public.signals(news_event_id,market_snapshot_id,ticker) values(n,m,'TEST') returning id into s;
    insert into public.orders(signal_id,client_order_id,ticker,purpose,side,quantity,reason)
    values(s,'hzn-test-entry','TEST','entry','buy',10,'test') returning id into entry_id;
    perform public.apply_paper_order_state(entry_id,'broker-entry','partially_filled',2,100,observed);
    perform public.apply_paper_order_state(entry_id,'broker-entry','partially_filled',2,100,observed);
    if (select count(*) from public.executions where order_id=entry_id)<>1 then raise exception 'duplicate execution'; end if;
    perform public.apply_paper_order_state(entry_id,'broker-entry','partially_filled',5,110,observed+interval '1 second');
    perform public.apply_paper_order_state(entry_id,'broker-entry','new',0,null,observed-interval '1 second');
    if (select quantity from public.positions where entry_order_id=entry_id)<>5 then raise exception 'stale state regressed position'; end if;
    insert into public.orders(signal_id,entry_order_id,client_order_id,ticker,purpose,side,quantity,reason)
    values(s,entry_id,'hzn-test-exit','TEST','exit','sell',2,'test') returning id into exit_id;
    perform public.apply_paper_order_state(exit_id,'broker-exit','filled',2,120,observed+interval '2 seconds');
    if (select realized_pnl from public.positions where entry_order_id=entry_id)<>20 then raise exception 'partial realized pnl incorrect'; end if;
    perform public.apply_paper_order_state(entry_id,'broker-entry','filled',10,110,observed+interval '3 seconds');
    insert into public.orders(signal_id,entry_order_id,client_order_id,ticker,purpose,side,quantity,reason)
    values(s,entry_id,'hzn-test-exit2','TEST','exit','sell',8,'test') returning id into exit2_id;
    perform public.apply_paper_order_state(exit2_id,'broker-exit2','filled',8,90,observed+interval '4 seconds');
    if (select realized_pnl from public.positions where entry_order_id=entry_id)<>-140
       or (select quantity from public.positions where entry_order_id=entry_id)<>0
       or not (select exposure_closed from public.orders where id=entry_id) then
        raise exception 'closed position accounting incorrect';
    end if;
end $$;
rollback;
