import type { Json } from "@/types/database.types";
import type { Signal } from "@/lib/types/Signal";
import LineChart from "./LineChart";

export function object(value: Json | undefined): Record<string, Json | undefined> {
  return value !== null && typeof value === "object" && !Array.isArray(value) ? value : {};
}
const numbers = (value: Json | undefined): number[] => Array.isArray(value) ? value.filter((item): item is number => typeof item === "number" && Number.isFinite(item)) : [];
const percent = (value: Json | undefined) => typeof value === "number" ? (value * 100).toFixed(2) + "%" : "Unavailable";

export default function QuantResults({ signal }: { signal: Signal }) {
  const model = object(object(signal.analysis).model);
  const features = object(signal.market_snapshot?.feature_data);
  const prices = Array.isArray(features.bars) ? features.bars.map(item => object(item).close).filter((item): item is number => typeof item === "number") : [];
  const counts = numbers(model.histogram_counts), edges = numbers(model.histogram_edges);
  const maximum = Math.max(1, ...counts);
  return <section className="space-y-5 rounded border border-gray-300 p-5">
    <h2 className="text-xl font-semibold">Market analysis</h2>
    <p className="text-sm">Completed sessions through {typeof features.as_of === "string" ? features.as_of : "unavailable"}. Split-adjusted IEX data; benchmark SPY.</p>
    <dl className="grid gap-3 text-sm sm:grid-cols-2">
      <div><dt>Completed-session price change</dt><dd>{percent(signal.market_snapshot?.price_change)}</dd></div>
      <div><dt>Market-adjusted return</dt><dd>{percent(signal.market_snapshot?.market_adjusted_return)}</dd></div>
      <div><dt>Annualized sample volatility</dt><dd>{percent(signal.market_snapshot?.volatility)}</dd></div>
      <div><dt>Completed-session relative volume</dt><dd>{signal.market_snapshot?.relative_volume == null ? "Unavailable" : signal.market_snapshot.relative_volume.toFixed(2) + "x"}</dd></div>
    </dl>
    <LineChart values={prices} label="Completed-session closing prices (USD)" />
    <h3 className="font-semibold">Monte Carlo simulation</h3>
    {typeof model.paths === "number" ? <>
      <p className="text-sm">{model.paths.toLocaleString()} paths · {String(model.horizon_days)} sessions · {String(model.observations)} historical returns</p>
      <p className="text-sm">Terminal return percentiles: 5th {percent(model.p05)} · median {percent(model.median)} · 95th {percent(model.p95)}</p>
      {counts.length > 0 && edges.length === counts.length + 1 && <figure>
        <svg viewBox="0 0 500 180" role="img" aria-label="Simulated terminal return distribution" className="w-full rounded border border-gray-300">
          <title>Simulated terminal return distribution</title>
          {counts.map((count, index) => <rect key={index} x={10 + index * 480 / counts.length} y={160 - count / maximum * 140} width={480 / counts.length - 2} height={count / maximum * 140} fill="currentColor"><title>{percent(edges[index])} to {percent(edges[index + 1])}: {count} paths</title></rect>)}
        </svg>
        <figcaption className="text-xs">Return bins from {percent(edges[0])} to {percent(edges[edges.length - 1])}; bar height is path count.</figcaption>
      </figure>}
      <LineChart values={numbers(model.rolling_5_session_volatility).map(value => value * 100)} label="Rolling five-session annualized volatility (%)" />
      <p className="text-sm">{typeof model.assumptions === "string" ? model.assumptions : "Model assumptions unavailable"}</p>
    </> : <p>Simulation unavailable. The signal remains a baseline watch signal until sufficient valid history is available.</p>}
  </section>;
}
