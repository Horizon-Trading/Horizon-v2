"use client";

import { useState, useEffect } from "react";
import { getHealth } from "@/lib/api/health";
import { getNews } from "@/lib/api/news";

export default function Home() {
  const [health, setHealth] = useState("undefined");
  const [news, setNews] = useState<any[]>([]);

  useEffect(() => {
    getHealth().then((data) => {
      setHealth(data.status);
    });

    getNews().then(setNews).catch(console.error);
  }, []);

  return (
    <main className="flex flex-col gap-4">
      <h1>{health}</h1>

      {news.map((event) => (
        <div key={event.id}>
          <p>{event.published_at}</p>
          <strong>{event.ticker}</strong>
          <p>{event.title}</p>
          <a>{event.url}</a>
        </div>
      ))}
    </main>
  );
}
