import type { FamilyProfileData } from "../lib/types";

const ROLE_ICON: Record<string, string> = {
  本人: "👤",
  配偶: "💑",
  子女: "🧒",
  父母: "👴",
};

export default function FamilyProfile({ data }: { data: FamilyProfileData }) {
  const members = data.members ?? [];
  return (
    <div>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 12 }}>
        {members.map((m, i) => (
          <div
            key={i}
            style={{
              background: "#0f141b",
              border: "1px solid #2a323d",
              borderRadius: 10,
              padding: "10px 14px",
              minWidth: 110,
            }}
          >
            <div style={{ fontSize: 22 }}>{ROLE_ICON[m.role] ?? "👤"}</div>
            <div style={{ fontWeight: 600, marginTop: 4 }}>{m.name || m.role}</div>
            <div style={{ fontSize: 12, color: "var(--muted)" }}>
              {m.age ? `${m.age}岁 · ` : ""}
              {m.location || ""}
            </div>
            {m.note && <div style={{ fontSize: 12, color: "var(--muted)", marginTop: 4 }}>{m.note}</div>}
          </div>
        ))}
      </div>
      {data.summary && (
        <p style={{ marginTop: 12, marginBottom: 0, color: "var(--muted)", fontSize: 13 }}>{data.summary}</p>
      )}
    </div>
  );
}
