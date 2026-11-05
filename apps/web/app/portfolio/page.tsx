"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { getPortfolio, getOrders, getTrades } from "@/lib/api/portfolio";
import LineChart from "@/app/components/LineChart";
import { object } from "@/app/components/QuantResults";

const money = (value: number | null | undefined) => value == null ? "Unavailable" : value.toLocaleString(undefined,{style:"currency",currency:"USD"});
const percent = (value: number | null | undefined) => value == null ? "Unavailable" : (value*100).toFixed(2)+"%";

export default function PortfolioPage() {
  const [data,setData]=useState<Awaited<ReturnType<typeof getPortfolio>> | null>(null);
  const [orders,setOrders]=useState<Awaited<ReturnType<typeof getOrders>>>([]);
  const [trades,setTrades]=useState<Awaited<ReturnType<typeof getTrades>>>([]);
  const [error,setError]=useState("");
  const [offset,setOffset]=useState(0);
  useEffect(()=>{
    let active=true;
    async function load() {
      try {
        const [portfolio,orderRows,tradeRows]=await Promise.all([getPortfolio(),getOrders(offset),getTrades(offset)]);
        if(active){setData(portfolio);setOrders(orderRows);setTrades(tradeRows);setError("");}
      } catch(err){if(active)setError(err instanceof Error ? err.message : "Portfolio unavailable");}
    }
    void load(); const timer=setInterval(load,30000);
    return ()=>{active=false;clearInterval(timer);};
  },[offset]);
  const snapshot=data?.snapshot;
  const brokerPositions=Array.isArray(snapshot?.broker_positions)?snapshot.broker_positions:[];
  return <main className="mx-auto w-full max-w-6xl space-y-6 p-6">
    <Link href="/" className="text-blue-600 underline">Back to dashboard</Link>
    <h1 className="text-3xl font-bold">Paper portfolio</h1>
    {error && <p role="alert">{error}. Previously loaded information may be stale.</p>}
    {!data && !error && <p role="status">Loading portfolio…</p>}
    {data && <>
      <p>Automatic paper submissions: {snapshot?.trading_enabled ? "Enabled" : "Disabled"}. Account snapshot: {snapshot ? new Date(snapshot.captured_at).toLocaleString() : "Unavailable; start the worker"}.</p>
      <dl className="grid gap-5 rounded border border-gray-300 p-5 sm:grid-cols-3">
        <div><dt>Paper equity</dt><dd>{money(snapshot?.equity)}</dd></div>
        <div><dt>Cash</dt><dd>{money(snapshot?.cash)}</dd></div>
        <div><dt>Buying power</dt><dd>{money(snapshot?.buying_power)}</dd></div>
        <div><dt>Broker-reported return (1 month)</dt><dd>{percent(data.performance.total_return)}</dd></div>
        <div><dt>Reported performance drawdown (1 month)</dt><dd>{percent(data.performance.max_drawdown)}</dd></div>
        <div><dt>Horizon realized P&amp;L</dt><dd>{money(data.realized_pnl)}</dd></div>
        <div><dt>Horizon closed trades</dt><dd>{data.closed_trades}</dd></div>
        <div><dt>Win rate (closed trades)</dt><dd>{percent(data.win_rate)}</dd></div>
      </dl>
      <p className="text-sm">Account performance uses Alpaca’s daily one-month P&amp;L series. Trade statistics include Horizon-managed closed positions; breakeven trades count in the denominator. Realized P&amp;L is before fees. Account totals may include activity outside Horizon.</p>
      {snapshot?.history_error && <p>Broker history is unavailable; returns are not estimated.</p>}
      <LineChart values={data.performance.equity_curve.map(point=>point.equity)} label="Paper account equity (USD, daily, one month)" />
      {data.performance.equity_curve.length>0 && <p className="text-xs">{new Date(data.performance.equity_curve[0].timestamp*1000).toLocaleDateString()} to {new Date(data.performance.equity_curve[data.performance.equity_curve.length-1].timestamp*1000).toLocaleDateString()}</p>}
      <section className="space-y-3"><h2 className="text-xl font-semibold">Broker open positions</h2>
        {brokerPositions.length===0 ? <p>{snapshot ? "No open positions" : "Positions unavailable"}</p> : <div className="overflow-x-auto"><table className="w-full text-left text-sm"><thead><tr><th>Symbol</th><th>Shares</th><th>Entry price</th><th>Market value</th><th>Unrealized P&amp;L</th></tr></thead><tbody>{brokerPositions.map((item,index)=>{const row=object(item);return <tr className="border-t" key={index}>{["symbol","qty","avg_entry_price","market_value","unrealized_pl"].map(key=><td className="py-2" key={key}>{String(row[key]??"Unavailable")}</td>)}</tr>;})}</tbody></table></div>}
      </section>
      <section className="space-y-3"><h2 className="text-xl font-semibold">Horizon orders</h2>
        {orders.length===0 ? <p>No orders on this page.</p> : <div className="overflow-x-auto"><table className="w-full text-left text-sm"><thead><tr><th>Created</th><th>Ticker</th><th>Side</th><th>Status</th><th>Filled / requested</th><th>Reason / error</th></tr></thead><tbody>{orders.map(order=><tr className="border-t" key={order.id}><td className="py-2">{new Date(order.created_at).toLocaleString()}</td><td>{order.ticker}</td><td>{order.side}</td><td>{order.status}</td><td>{order.filled_quantity} / {order.quantity}</td><td>{order.reason}{order.error && " · "+order.error}</td></tr>)}</tbody></table></div>}
      </section>
      <section className="space-y-3"><h2 className="text-xl font-semibold">Closed trade history</h2>
        {trades.length===0 ? <p>No closed trades on this page.</p> : <div className="overflow-x-auto"><table className="w-full text-left text-sm"><thead><tr><th>Ticker</th><th>Opened</th><th>Closed</th><th>Realized P&amp;L</th></tr></thead><tbody>{trades.map(trade=><tr className="border-t" key={trade.entry_order_id}><td className="py-2">{trade.ticker}</td><td>{new Date(trade.opened_at).toLocaleString()}</td><td>{trade.closed_at ? new Date(trade.closed_at).toLocaleString() : "Open"}</td><td>{money(trade.realized_pnl)}</td></tr>)}</tbody></table></div>}
      </section>
      <nav className="flex gap-4" aria-label="Order and trade pages"><button disabled={offset===0} className="rounded border px-4 py-2 disabled:opacity-40" onClick={()=>setOffset(offset-50)}>Previous</button><button disabled={orders.length<50&&trades.length<50} className="rounded border px-4 py-2 disabled:opacity-40" onClick={()=>setOffset(offset+50)}>Next</button></nav>
    </>}
  </main>;
}
