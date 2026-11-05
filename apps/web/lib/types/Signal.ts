import type { Database } from "@/types/database.types";
import type { NewsEvent } from "./NewsEvent";
import type { MarketSnapshot } from "./MarketSnapshot";
export type Signal = Database["public"]["Tables"]["signals"]["Row"] & { news_event: NewsEvent | null; market_snapshot: MarketSnapshot | null };
