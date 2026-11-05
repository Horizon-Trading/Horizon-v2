import type { Database } from "@/types/database.types";
export type NewsEvent = Omit<Database["public"]["Tables"]["news_events"]["Row"], "raw_data"> & { ingestion_latency_seconds: number | null };
