import { useEffect, useState } from "react";
import Whiteboard from "./components/Whiteboard";
import type { Lang, ZoneMeta, ZoneStateEntry } from "./lib/types";

interface ShareData {
  templateId: string;
  language: Lang;
  zones: ZoneMeta[];
  zoneData: Record<string, { data: Record<string, unknown>; version: number }>;
  dialogue: { role: string; content: string }[];
}

export default function ShareView({ token }: { token: string }) {
  const [data, setData] = useState<ShareData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch(`/api/share/${token}`)
      .then((r) => {
        if (!r.ok) throw new Error(r.status === 410 ? "分享链接已失效或过期" : "加载失败");
        return r.json();
      })
      .then(setData)
      .catch((e) => setError(e.message));
  }, [token]);

  if (error) {
    return <div style={{ padding: 40, color: "var(--muted)" }}>{error}</div>;
  }
  if (!data) {
    return <div style={{ padding: 40, color: "var(--muted)" }}>加载中…</div>;
  }

  const zones: Record<string, ZoneStateEntry> = {};
  for (const [zid, v] of Object.entries(data.zoneData)) {
    zones[zid] = { id: zid, data: v.data, version: v.version };
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%" }}>
      <header style={{ padding: "12px 20px", borderBottom: "1px solid var(--border)", display: "flex", gap: 12, alignItems: "center" }}>
        <strong style={{ fontSize: 18 }}>WhiteboardAdvisor</strong>
        <span style={{ color: "var(--muted)", fontSize: 13 }}>只读分享</span>
      </header>
      <div style={{ flex: 1, display: "flex", minHeight: 0 }}>
        <main style={{ flex: 1, padding: 20, display: "flex", minHeight: 0 }}>
          <Whiteboard meta={data.zones} zones={zones} focus={null} lang={data.language} onRefresh={() => {}} />
        </main>
        <aside style={{ width: 340, borderLeft: "1px solid var(--border)", overflow: "auto", padding: 16 }}>
          {data.dialogue.map((d, i) => (
            <div key={i} style={{ marginBottom: 8, alignSelf: d.role === "user" ? "flex-end" : "flex-start" }}>
              <div style={{ background: d.role === "user" ? "var(--accent)" : "var(--panel)", color: d.role === "user" ? "#fff" : "var(--ink)", padding: "8px 12px", borderRadius: 12, fontSize: 14 }}>
                {d.content}
              </div>
            </div>
          ))}
        </aside>
      </div>
    </div>
  );
}
