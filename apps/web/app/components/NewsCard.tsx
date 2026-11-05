import type { NewsEvent } from "@/lib/types/NewsEvent";
export default function NewsCard({ news }: { news: NewsEvent }) {
  return <article className="space-y-2 rounded-lg border border-gray-300 p-4">
    <p className="text-sm">{news.ticker} · {news.event_type ?? "Unclassified"} · {news.provider === "seed" ? "Demo seed" : news.source ?? news.provider}</p>
    <h3 className="font-semibold">{news.title}</h3>
    <p className="text-sm">{news.summary ?? "No summary available"}</p>
    <p className="text-xs">Published {new Date(news.published_at).toLocaleString()} · Ingestion latency: {news.ingestion_latency_seconds == null ? "Unavailable" : news.ingestion_latency_seconds.toFixed(1) + "s"}</p>
    {news.snapshot_error && <p className="text-sm">Snapshot unavailable · attempts {news.snapshot_attempts}/5</p>}
    {/^https?:\/\//i.test(news.url) && <a className="text-blue-600 underline" href={news.url} target="_blank" rel="noreferrer">Read source article</a>}
  </article>;
}
