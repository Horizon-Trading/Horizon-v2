import { getJson } from "./client";
import type { NewsEvent } from "../types/NewsEvent";
export const getNews = (offset = 0) => getJson<NewsEvent[]>("/news?limit=20&offset=" + offset);
