import { getJson } from "./client";
import type { Database } from "@/types/database.types";
type Tables = Database["public"]["Tables"];
export type Portfolio = {
  snapshot: Tables["portfolio_snapshots"]["Row"] | null;
  performance: { total_return: number | null; max_drawdown: number | null; period: string; equity_curve: {timestamp:number; equity:number}[] };
  closed_trades: number; win_rate: number | null; realized_pnl: number;
  managed_positions: Tables["positions"]["Row"][];
};
export const getPortfolio = () => getJson<Portfolio>("/portfolio");
export const getOrders = (offset=0) => getJson<Tables["orders"]["Row"][]>("/portfolio/orders?limit=50&offset="+offset);
export const getTrades = (offset=0) => getJson<Tables["positions"]["Row"][]>("/portfolio/trades?limit=50&offset="+offset);
