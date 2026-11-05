"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { getHealth } from "@/lib/api/health";
import { getSignals } from "@/lib/api/signals";
import { getNews } from "@/lib/api/news";
import type { Signal } from "@/lib/types/Signal";
import type { NewsEvent } from "@/lib/types/NewsEvent";
import SignalCard from "./components/SignalCard";
import NewsCard from "./components/NewsCard";

export default function Home() {
  const [data, setData] = useState<{signals: Signal[]; news: NewsEvent[]; health: string} | null>(null);
  const [error, setError] = useState("");
  const [offset, setOffset] = useState(0);
  const [revision, setRevision] = useState(0);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    let active = true;
    async function load() {
      try {
        const [signals, news, health] = await Promise.all([getSignals(offset), getNews(offset), getHealth()]);
        if (active) { setData({signals, news, health: health.status}); setError(""); }
      } catch (err) { if (active) setError(err instanceof Error ? err.message : "Unable to load dashboard"); }
      finally { if (active) setLoading(false); }
    }
    void load();
    const timer = setInterval(load, 30000);
    return () => { active = false; clearInterval(timer); };
  }, [offset, revision]);
  function navigate(next: number) { setLoading(true); setOffset(next); }
  return <main className="mx-auto w-full max-w-6xl space-y-6 p-6">
    <header className="flex flex-wrap items-center justify-between gap-4">
      <div><h1 className="text-3xl font-bold">Horizon 2.0</h1><p>News-driven research and paper trading</p></div>
      <button className="rounded border px-4 py-2" disabled={loading} onClick={() => { setLoading(true); setRevision(revision + 1); }}>Refresh</button>
    </header>
    <Link className="inline-block text-blue-600 underline" href="/portfolio">Paper portfolio, positions and trade history</Link>
    <p className="text-sm">API: {error ? "Unavailable" : data?.health ?? "Connecting"} · Updates every 30 seconds · Page {offset / 20 + 1}</p>
    {loading && <p role="status">Loading dashboard…</p>}
    {error && <p role="alert" className="rounded border border-red-500 p-3">{error}. Check the API connection and refresh. Previously loaded data may be stale.</p>}
    <div className="grid gap-6 lg:grid-cols-2">
      <section className="space-y-4"><h2 className="text-2xl font-semibold">Signals</h2>
        {data?.signals.map(signal => <SignalCard key={signal.id} signal={signal} />)}
        {data?.signals.length === 0 && <p>No signals on this page. Processed news with market snapshots will appear here.</p>}
      </section>
      <section className="space-y-4"><h2 className="text-2xl font-semibold">News events</h2>
        {data?.news.map(news => <NewsCard key={news.id} news={news} />)}
        {data?.news.length === 0 && <p>No news on this page. Start the news worker to receive articles.</p>}
      </section>
    </div>
    <nav className="flex gap-4" aria-label="Feed pages">
      <button className="rounded border px-4 py-2 disabled:opacity-40" disabled={loading || offset === 0} onClick={() => navigate(offset - 20)}>Previous</button>
      <button className="rounded border px-4 py-2 disabled:opacity-40" disabled={loading || !data || (data.signals.length < 20 && data.news.length < 20)} onClick={() => navigate(offset + 20)}>Next</button>
    </nav>
  </main>;
}
