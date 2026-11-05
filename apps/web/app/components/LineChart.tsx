export default function LineChart({ values, label }: { values: number[]; label: string }) {
  if (values.length < 2 || values.some(value => !Number.isFinite(value))) return <p>Chart unavailable</p>;
  const low = Math.min(...values), high = Math.max(...values);
  const points = values.map((value, index) => `${10 + index / (values.length - 1) * 480},${150 - (high === low ? .5 : (value - low) / (high - low)) * 130}`).join(" ");
  return <figure className="space-y-1">
    <svg viewBox="0 0 500 170" role="img" aria-label={label} className="w-full rounded border border-gray-300">
      <title>{label}</title><polyline points={points} fill="none" stroke="currentColor" strokeWidth="2" />
    </svg>
    <figcaption className="text-xs">{label} · min {low.toFixed(2)} · max {high.toFixed(2)} · {values.length} observations</figcaption>
  </figure>;
}
