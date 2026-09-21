"use client";

import type { Signals } from "@/lib/types/Signals";
import { useState, useEffect } from "react";
import { getHealth } from "@/lib/api/health";
import { getSignals } from "@/lib/api/signals";

export default function Home() {
  const [health, setHealth] = useState("undefined");
  const [signals, setSignals] = useState<Signals[]>([]);

  useEffect(() => {
    getHealth().then((data) => {
      setHealth(data.status);
    });

    getSignals().then(setSignals).catch(console.error);
  }, []);

  return (
    <main className="flex flex-col gap-4">
      <h1>{health}</h1>

      {signals.map((signal) => (
        <div key={signal.id}>
          <p>{signal.id}</p>
          <strong>{signal.ticker}</strong>
        </div>
      ))}
    </main>
  );
}
