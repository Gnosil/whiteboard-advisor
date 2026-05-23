import type { CrossBorderNotesData } from "../lib/types";

export default function CrossBorderNotes({ data }: { data: CrossBorderNotesData }) {
  return (
    <div>
      {(data.notes ?? []).map((n, i) => (
        <div key={i} style={{ padding: "6px 0", borderBottom: "1px solid var(--border)" }}>
          <div style={{ fontSize: 13 }}>
            <span style={{ background: "var(--accent-soft)", color: "var(--accent)", borderRadius: 4, padding: "1px 6px", fontSize: 11 }}>
              {n.jurisdiction}
            </span>{" "}
            <b>{n.topic}</b>
          </div>
          {n.detail && <div style={{ fontSize: 13, color: "var(--muted)", marginTop: 2 }}>{n.detail}</div>}
        </div>
      ))}
      {data.summary && <p style={{ marginTop: 8, marginBottom: 0, color: "var(--muted)", fontSize: 13 }}>{data.summary}</p>}
    </div>
  );
}
