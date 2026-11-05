export async function getJson<T>(path: string): Promise<T> {
  const base = "/api";
  const response = await fetch(base.replace(/\/$/, "") + path, { cache: "no-store", signal: AbortSignal.timeout(15000) });
  if (!response.ok) throw new Error(response.status === 404 ? "Not found" : "API request failed (" + response.status + ")");
  return response.json() as Promise<T>;
}
