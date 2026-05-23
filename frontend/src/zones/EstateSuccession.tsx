import type { EstateSuccessionData } from "../lib/types";

export default function EstateSuccession({ data }: { data: EstateSuccessionData }) {
  return (
    <div>
      {(data.structures ?? []).map((s, i) => (
        <div key={i} style={{ background: "var(--panel-2)", border: "1px solid var(--border)", borderRadius: 10, padding: 10, marginBottom: 8 }}>
          <div style={{ fontWeight: 600 }}>{s.type}</div>
          <div style={{ fontSize: 12, color: "var(--muted)", marginTop: 2 }}>
            {s.beneficiary ? `受益人 ${s.beneficiary}` : ""}{s.jurisdiction ? ` · ${s.jurisdiction}` : ""}
          </div>
          {s.note && <div style={{ fontSize: 13, marginTop: 4 }}>{s.note}</div>}
        </div>
      ))}
      {data.tax_notes && <p style={{ marginTop: 6, marginBottom: 0, color: "var(--warn)", fontSize: 12 }}>税务:{data.tax_notes}</p>}
      {data.summary && <p style={{ marginTop: 6, marginBottom: 0, color: "var(--muted)", fontSize: 13 }}>{data.summary}</p>}
    </div>
  );
}
