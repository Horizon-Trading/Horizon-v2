"use client";

import { useState, useEffect } from "react";
import { getHealth } from "@/lib/api/health";

export default function Home() {
  const [health, setHealth] = useState("undefined");

  useEffect(() => {
    getHealth().then((data) => {
      setHealth(data.status);
    });
  }, []);

  return <>{health}</>;
}
