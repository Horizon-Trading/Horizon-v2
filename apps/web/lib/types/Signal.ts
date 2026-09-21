import { Database } from "@/types/database.types";
import { NewsEvent } from "./NewsEvent";
import { MarketSnapshot } from "./MarketSnapshot";

export type Signal = Database["public"]["Tables"]["signals"]["Row"] & {
  news_event: NewsEvent;
  market_snapshot: MarketSnapshot;
};
