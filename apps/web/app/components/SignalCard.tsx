import Link from "next/link";
import type { Signal } from "@/lib/types/Signal";
import NewsCard from "./NewsCard";
const percent = (value: number | null) => value == null ? "Unavailable" : (value * 100).toFixed(2) + "%";
export default function SignalCard({ signal, detail = false }: { signal: Signal; detail?: boolean }) {
  const snapshot = signal.market_snapshot;
  return <article className="space-y-4 rounded-lg border border-gray-300 p-5">
    <header className="flex flex-wrap items-center justify-between gap-3">
      <h2 className="text-xl font-semibold"><Link className="underline" href={"/signals/" + signal.id}>{signal.ticker}</Link></h2>
      <span>Score {signal.score ?? "Unavailable"} / 100</span>
    </header>
    <p className="text-sm">{signal.model_version === "seed" ? "Demo seed" : signal.model_version} · {new Date(signal.created_at).toLocaleString()}</p>
    <dl className="grid gap-3 text-sm sm:grid-cols-3">
      <div><dt>{signal.model_version === "baseline-v1" ? "Data coverage" : signal.model_version === "normal-log-returns-v1" ? "History coverage" : "Confidence"}</dt><dd>{percent(signal.confidence)}</dd></div>
      <div><dt>Expected return</dt><dd>{percent(signal.expected_return)}</dd></div>
      <div><dt>Model profit probability</dt><dd>{percent(signal.probability_profit)}</dd></div>
    </dl>
    {signal.model_version === "baseline-v1" && <p className="text-sm">Attention score only. Watch signal; no directional forecast.</p>}
    {snapshot ? <dl className="grid gap-3 text-sm sm:grid-cols-3">
      <div><dt>Observed price</dt><dd>${snapshot.price.toFixed(2)}</dd></div>
      <div><dt>Session volume (IEX)</dt><dd>{snapshot.volume?.toLocaleString() ?? "Unavailable"}</dd></div>
      <div><dt>Relative volume</dt><dd>{snapshot.relative_volume == null ? "Unavailable" : snapshot.relative_volume.toFixed(2) + "x"}</dd></div>
      {detail && <>
        <div><dt>Market cap</dt><dd>{snapshot.market_cap?.toLocaleString() ?? "Unavailable"}</dd></div>
        <div><dt>Float shares</dt><dd>{snapshot.float_shares?.toLocaleString() ?? "Unavailable"}</dd></div>
        <div><dt>Captured</dt><dd>{new Date(snapshot.captured_at).toLocaleString()}</dd></div>
      </>}
    </dl> : <p>Snapshot unavailable</p>}
    {signal.news_event ? (detail ? <NewsCard news={signal.news_event} /> : <p>{signal.news_event.title}</p>) : <p>Related news unavailable</p>}
    {!detail && <Link className="text-blue-600 underline" href={"/signals/" + signal.id}>Signal details</Link>}
  </article>;
}
