import type { CoveragePlanData } from "../lib/types";

function fmt(n?: number | null, unit?: string) {
  if (n === null || n === undefined) return "—";
  const s = n >= 1000 ? n.toLocaleString() : String(n);
  return `${unit ? unit + " " : ""}${s}`;
}

export default function CoveragePlan({ data }: { data: CoveragePlanData }) {
  return (
    <div>
      {(data.products ?? []).map((p, i) => (
        <div
          key={i}
          style={{
            background: "#0f141b",
            border: "1px solid #2a323d",
            borderRadius: 10,
            padding: 12,
            marginBottom: 10,
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
            <span style={{ fontWeight: 600 }}>{p.type}</span>
            <span style={{ fontSize: 13, color: "var(--accent)" }}>{fmt(p.coverage, p.unit)}</span>
          </div>
          <div style={{ fontSize: 12, color: "var(--muted)", marginTop: 2 }}>
            {p.term ? `保障期 ${p.term}` : ""}
            {p.est_premium ? ` · 估算保费 ${fmt(p.est_premium, p.unit)}/年` : ""}
          </div>
          <div style={{ fontSize: 13, marginTop: 6 }}>{p.rationale}</div>
        </div>
      ))}
      {data.total_premium != null && (
        <div style={{ fontSize: 13, fontWeight: 600 }}>合计估算保费:{fmt(data.total_premium)}/年</div>
      )}
      {data.disclaimer && (
        <p style={{ marginTop: 8, marginBottom: 0, color: "#ff9d6b", fontSize: 12 }}>⚠ {data.disclaimer}</p>
      )}
    </div>
  );
}
