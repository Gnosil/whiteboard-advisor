import type { SummaryDashboardData } from "../lib/types";

export default function SummaryDashboard({ data }: { data: SummaryDashboardData }) {
  return (
    <div>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 10 }}>
        {(data.highlights ?? []).map((h, i) => (
          <div key={i} style={{ background: "#0f141b", border: "1px solid #2a323d", borderRadius: 10, padding: "8px 12px", minWidth: 100 }}>
            <div style={{ fontSize: 12, color: "var(--muted)" }}>{h.label}</div>
            <div style={{ fontSize: 18, fontWeight: 700, color: "var(--accent)" }}>
              {h.value}
              {h.unit ? <span style={{ fontSize: 12, color: "var(--muted)" }}> {h.unit}</span> : null}
            </div>
          </div>
        ))}
      </div>
      {data.action_items && data.action_items.length > 0 && (
        <ul style={{ marginTop: 12, paddingLeft: 18, fontSize: 13 }}>
          {data.action_items.map((a, i) => (
            <li key={i} style={{ marginBottom: 4 }}>{a}</li>
          ))}
        </ul>
      )}
      {data.summary && <p style={{ marginTop: 8, marginBottom: 0, color: "var(--muted)", fontSize: 13 }}>{data.summary}</p>}
    </div>
  );
}
