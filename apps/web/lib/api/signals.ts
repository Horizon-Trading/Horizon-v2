export async function getSignals() {
  const url = new URL(`${process.env.NEXT_PUBLIC_API_URL}/signals`);
  const response = await fetch(url);

  if (!response.ok) {
    throw new Error("Failed to fetch signals");
  }

  return response.json();
}
