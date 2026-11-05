"use client";
import { use, useEffect, useState } from "react";
import Link from "next/link";
import { getSignal } from "@/lib/api/signals";
import type { Signal } from "@/lib/types/Signal";
import SignalCard from "@/app/components/SignalCard";
export default function SignalPage({ params }: { params: Promise<{id: string}> }) {
  const { id } = use(params);
  const [signal, setSignal] = useState<Signal | null>(null);
  const [error, setError] = useState("");
  useEffect(() => {
    let active = true;
    getSignal(id).then(value => { if (active) setSignal(value); })
      .catch(err => { if (active) setError(err instanceof Error ? err.message : "Unable to load signal"); });
    return () => { active = false; };
  }, [id]);
  return <main className="mx-auto w-full max-w-4xl space-y-6 p-6">
    <Link className="text-blue-600 underline" href="/">Back to dashboard</Link>
    <h1 className="text-2xl font-bold">Signal detail</h1>
    {error ? <p role="alert">{error}</p> : signal ? <SignalCard signal={signal} detail /> : <p role="status">Loading signal…</p>}
  </main>;
}
