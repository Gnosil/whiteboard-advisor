import type { GapItem, ProtectionGapData } from "../lib/types";

function fmt(n?: number | null, unit?: string) {
  if (n === null || n === undefined) return "—";
  const s = n >= 1000 ? n.toLocaleString() : String(n);
  return `${unit ? unit + " " : ""}${s}`;
}

function GapBar({ item }: { item: GapItem }) {
  const rec = item.recommended ?? 0;
  const cur = item.current ?? 0;
  const pct = rec > 0 ? Math.min(100, Math.round((cur / rec) * 100)) : 0;
  return (
    <div style={{ marginBottom: 12 }}>
      <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13, marginBottom: 4 }}>
        <span style={{ fontWeight: 600 }}>{item.category}</span>
        <span style={{ color: "var(--warn)" }}>缺口 {fmt(item.gap, item.unit)}</span>
      </div>
      <div style={{ height: 10, background: "var(--panel-2)", borderRadius: 6, overflow: "hidden" }}>
        <div style={{ width: `${pct}%`, height: "100%", background: "linear-gradient(90deg,#7FC8A6,var(--accent))" }} />
      </div>
      <div style={{ fontSize: 11, color: "var(--muted)", marginTop: 3 }}>
        现有 {fmt(item.current, item.unit)} / 建议 {fmt(item.recommended, item.unit)}
      </div>
    </div>
  );
}

export default function ProtectionGap({ data }: { data: ProtectionGapData }) {
  return (
    <div>
      {(data.items ?? []).map((it, i) => (
        <GapBar key={i} item={it} />
      ))}
      {data.summary && (
        <p style={{ marginTop: 8, marginBottom: 0, color: "var(--muted)", fontSize: 13 }}>{data.summary}</p>
      )}
    </div>
  );
}
