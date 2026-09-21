import { Database } from "@/types/database.types";
import { NewsEvent } from "./NewsEvent";

export type MarketSnapshot =
  Database["public"]["Tables"]["market_snapshots"]["Row"] & {
    news_event: NewsEvent;
  };
