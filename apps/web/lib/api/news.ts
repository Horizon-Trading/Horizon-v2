export async function getNews() {
  const url = new URL(`${process.env.NEXT_PUBLIC_API_URL}/news`);
  const response = await fetch(url);

  if (!response.ok) {
    throw new Error("Failed to fetch news");
  }

  return response.json();
}
