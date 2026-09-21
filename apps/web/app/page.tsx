"use client";

import type { Signal } from "@/lib/types/Signal";
import { useState, useEffect } from "react";
import { getHealth } from "@/lib/api/health";
import { getSignals } from "@/lib/api/signals";

export default function Home() {
  const [health, setHealth] = useState("undefined");
  const [signals, setSignals] = useState<Signal[]>([]);

  useEffect(() => {
    getHealth().then((data) => {
      setHealth(data.status);
    });

    getSignals().then(setSignals).catch(console.error);
  }, []);

  return (
    <main className="mx-auto flex max-w-5xl flex-col gap-6 p-6">
      <div>
        <h1 className="text-2xl font-bold">ABG Horizon</h1>
        <p className="text-sm text-gray-500">
          API Status: <span className="font-medium">{health}</span>
        </p>
      </div>

      {signals.map((signal) => (
        <div
          key={signal.id}
          className="rounded-lg border border-gray-200 p-5 shadow-sm"
        >
          <div className="mb-4 flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold">{signal.ticker}</h2>
              <p className="text-xs text-gray-400">{signal.id}</p>
            </div>

            <div className="text-right">
              <p className="text-sm text-gray-500">Score</p>
              <p className="text-2xl font-bold">{signal.score ?? "—"}</p>
            </div>
          </div>

          <div className="grid gap-6 md:grid-cols-3">
            {/* Signal */}
            <section>
              <h3 className="mb-2 font-semibold">Signal</h3>

              <div className="space-y-1 text-sm">
                <p>
                  <span className="text-gray-500">Confidence:</span>{" "}
                  {signal.confidence != null
                    ? `${(signal.confidence * 100).toFixed(1)}%`
                    : "—"}
                </p>

                <p>
                  <span className="text-gray-500">Expected Return:</span>{" "}
                  {signal.expected_return != null
                    ? `${(signal.expected_return * 100).toFixed(2)}%`
                    : "—"}
                </p>

                <p>
                  <span className="text-gray-500">Probability Profit:</span>{" "}
                  {signal.probability_profit != null
                    ? `${(signal.probability_profit * 100).toFixed(1)}%`
                    : "—"}
                </p>

                <p>
                  <span className="text-gray-500">Created:</span>{" "}
                  {new Date(signal.created_at).toLocaleString()}
                </p>
              </div>
            </section>

            {/* News */}
            <section>
              <h3 className="mb-2 font-semibold">News Event</h3>

              {signal.news_event ? (
                <div className="space-y-1 text-sm">
                  <p className="font-medium">{signal.news_event.title}</p>

                  <p>
                    <span className="text-gray-500">Type:</span>{" "}
                    {signal.news_event.event_type ?? "—"}
                  </p>

                  <p>
                    <span className="text-gray-500">Published:</span>{" "}
                    {new Date(signal.news_event.published_at).toLocaleString()}
                  </p>

                  <p>
                    <span className="text-gray-500">Summary:</span>{" "}
                    {signal.news_event.summary ?? "—"}
                  </p>

                  <a
                    href={signal.news_event.url}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-block text-blue-600 hover:underline"
                  >
                    View article
                  </a>
                </div>
              ) : (
                <p className="text-sm text-gray-400">No news event</p>
              )}
            </section>

            {/* Market snapshot */}
            <section>
              <h3 className="mb-2 font-semibold">Market Snapshot</h3>

              {signal.market_snapshot ? (
                <div className="space-y-1 text-sm">
                  <p>
                    <span className="text-gray-500">Price:</span> $
                    {signal.market_snapshot.price.toFixed(2)}
                  </p>

                  <p>
                    <span className="text-gray-500">Volume:</span>{" "}
                    {signal.market_snapshot.volume?.toLocaleString() ?? "—"}
                  </p>

                  <p>
                    <span className="text-gray-500">Relative Volume:</span>{" "}
                    {signal.market_snapshot.relative_volume?.toFixed(2) ?? "—"}x
                  </p>

                  <p>
                    <span className="text-gray-500">Market Cap:</span>{" "}
                    {signal.market_snapshot.market_cap?.toLocaleString() ?? "—"}
                  </p>

                  <p>
                    <span className="text-gray-500">Float:</span>{" "}
                    {signal.market_snapshot.float_shares?.toLocaleString() ??
                      "—"}
                  </p>

                  <p>
                    <span className="text-gray-500">Captured:</span>{" "}
                    {new Date(
                      signal.market_snapshot.captured_at,
                    ).toLocaleString()}
                  </p>
                </div>
              ) : (
                <p className="text-sm text-gray-400">No market snapshot</p>
              )}
            </section>
          </div>
        </div>
      ))}
    </main>
  );
}
