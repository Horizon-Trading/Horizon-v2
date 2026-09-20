export async function getHealth() {
  const url = new URL(`${process.env.NEXT_PUBLIC_API_URL}/health`);
  const response = await fetch(url);

  if (!response.ok) {
    throw new Error("API is unhealthy");
  }

  return response.json();
}
