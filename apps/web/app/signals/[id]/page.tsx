"use client";
import { use, useEffect, useState } from "react";
import Link from "next/link";
import { getSignal, getSignalHistory } from "@/lib/api/signals";
import type { Signal } from "@/lib/types/Signal";
import SignalCard from "@/app/components/SignalCard";
import QuantResults, { object } from "@/app/components/QuantResults";
export default function SignalPage({ params }: { params: Promise<{id: string}> }) {
  const { id } = use(params);
  const [signal, setSignal] = useState<Signal | null>(null);
  const [error, setError] = useState("");
  const [history, setHistory] = useState<Awaited<ReturnType<typeof getSignalHistory>>>([]);
  useEffect(() => {
    let active = true;
    Promise.all([getSignal(id), getSignalHistory(id)]).then(([value, revisions]) => { if (active) { setSignal(value); setHistory(revisions); } })
      .catch(err => { if (active) setError(err instanceof Error ? err.message : "Unable to load signal"); });
    return () => { active = false; };
  }, [id]);
  return <main className="mx-auto w-full max-w-4xl space-y-6 p-6">
    <Link className="text-blue-600 underline" href="/">Back to dashboard</Link>
    <h1 className="text-2xl font-bold">Signal detail</h1>
    {error ? <p role="alert">{error}</p> : signal ? <>
      <SignalCard signal={signal} detail />
      <QuantResults signal={signal} />
      <section className="space-y-3"><h2 className="text-xl font-semibold">Analysis history</h2>
        <p className="text-sm">Latest 50 recorded changes. Reanalysis does not make the original news or quote fresh.</p>
        <div className="overflow-x-auto"><table className="w-full text-left text-sm">
          <thead><tr><th className="p-2">Recorded</th><th className="p-2">Model</th><th className="p-2">Score</th><th className="p-2">Expected return</th></tr></thead>
          <tbody>{history.map(revision => { const row = object(revision.data); return <tr className="border-t" key={revision.id}>
            <td className="p-2">{new Date(revision.recorded_at).toLocaleString()}</td><td className="p-2">{String(row.model_version ?? "Unknown")}</td>
            <td className="p-2">{typeof row.score === "number" ? row.score.toFixed(2) : "Unavailable"}</td><td className="p-2">{typeof row.expected_return === "number" ? (row.expected_return * 100).toFixed(2) + "%" : "Unavailable"}</td>
          </tr>; })}</tbody>
        </table></div>
      </section>
    </> : <p role="status">Loading signal…</p>}
  </main>;
}
