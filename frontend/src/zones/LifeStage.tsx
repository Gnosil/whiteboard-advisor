import type { LifeStageData } from "../lib/types";

const CAT_COLOR: Record<string, string> = {
  保险: "var(--accent)",
  资产配置: "#2F6FB0",
  教育金: "#8A6D1F",
  退休: "#6B4FA0",
  传承: "#9A6B12",
  现金流: "#1F7A5C",
  税务: "#B4552F",
};

function PriorityDot({ p }: { p?: string | null }) {
  if (!p) return null;
  const color = p.includes("高") ? "var(--warn)" : p.includes("低") ? "var(--muted)" : "var(--amber)";
  return <span style={{ fontSize: 11, color }}>· {p}</span>;
}

export default function LifeStage({ data }: { data: LifeStageData }) {
  return (
    <div>
      {(data.age_range || data.focus) && (
        <div style={{ marginBottom: 10, fontSize: 13, color: "var(--muted)" }}>
          {data.age_range ? <b style={{ color: "var(--ink)" }}>{data.age_range}</b> : null}
          {data.age_range && data.focus ? " · " : ""}
          {data.focus}
        </div>
      )}
      {(data.items ?? []).map((it, i) => (
        <div
          key={i}
          style={{
            display: "flex",
            gap: 8,
            alignItems: "baseline",
            padding: "7px 0",
            borderBottom: "1px solid var(--border)",
          }}
        >
          <span
            style={{
              flexShrink: 0,
              fontSize: 11,
              background: "var(--accent-soft)",
              color: CAT_COLOR[it.category] || "var(--accent)",
              borderRadius: 6,
              padding: "2px 8px",
              fontWeight: 600,
            }}
          >
            {it.category}
          </span>
          <div style={{ flex: 1 }}>
            <div style={{ fontSize: 14 }}>
              {it.action} <PriorityDot p={it.priority} />
            </div>
            {it.note && <div style={{ fontSize: 12, color: "var(--muted)", marginTop: 2 }}>{it.note}</div>}
          </div>
        </div>
      ))}
      {data.summary && (
        <p style={{ marginTop: 10, marginBottom: 0, color: "var(--muted)", fontSize: 13 }}>{data.summary}</p>
      )}
    </div>
  );
}
