export function fmtMoney(n?: number | null, unit?: string): string {
  if (n === null || n === undefined) return "—";
  const s = n >= 1000 ? n.toLocaleString() : String(n);
  return `${unit ? unit + " " : ""}${s}`;
}
