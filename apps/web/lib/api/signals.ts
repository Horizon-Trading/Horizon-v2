import { getJson } from "./client";
import type { Signal } from "../types/Signal";
import type { Database } from "@/types/database.types";
export const getSignals = (offset = 0) => getJson<Signal[]>("/signals?limit=20&offset=" + offset);
export const getSignal = (id: string) => getJson<Signal>("/signals/" + encodeURIComponent(id));
export const getSignalHistory = (id: string) => getJson<Database["public"]["Tables"]["signal_history"]["Row"][]>("/signals/" + encodeURIComponent(id) + "/history");
