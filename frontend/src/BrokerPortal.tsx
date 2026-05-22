import { useEffect, useState } from "react";

interface Lead {
  id: string;
  tier: string;
  status: string;
  matchedBroker: string | null;
  priceCharged: number | null;
  risky: boolean;
  createdAt: string;
  slaDueAt: string | null;
  contactName: string;
  preference: string;
  zoneData: Record<string, unknown>;
}

export default function BrokerPortal() {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [open, setOpen] = useState<string | null>(null);

  const load = () =>
    fetch("/api/broker/leads")
      .then((r) => r.json())
      .then((d) => setLeads(d.leads));

  useEffect(() => {
    load();
  }, []);

  const claim = async (id: string) => {
    await fetch(`/api/broker/leads/${id}/claim`, { method: "POST" });
    load();
  };

  return (
    <div style={{ padding: 24, maxWidth: 900, margin: "0 auto" }}>
      <h2>Broker Portal · Leads</h2>
      <p style={{ color: "var(--muted)", fontSize: 13 }}>脱敏 lead 列表;claim 后 48h 内需联系客户。</p>
      {leads.length === 0 && <p style={{ color: "var(--muted)" }}>暂无 lead。</p>}
      {leads.map((l) => (
        <div key={l.id} style={{ background: "var(--panel)", borderRadius: 12, padding: 16, marginBottom: 12, border: "1px solid #232a33" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <strong>{l.contactName || "(匿名)"}</strong>
            <span style={{ fontSize: 12, background: "var(--accent-soft)", color: "var(--accent)", padding: "2px 8px", borderRadius: 6 }}>
              {l.tier}
            </span>
            <span style={{ fontSize: 12, color: "var(--muted)" }}>{l.status}</span>
            {l.priceCharged != null && <span style={{ fontSize: 12 }}>${l.priceCharged}</span>}
            {l.risky && <span style={{ fontSize: 12, color: "#ff7a7a" }}>⚠ risky</span>}
            <button
              onClick={() => setOpen(open === l.id ? null : l.id)}
              style={{ marginLeft: "auto", fontSize: 12, padding: "4px 10px", borderRadius: 6, border: "1px solid #2a323d", background: "transparent", color: "var(--ink)" }}
            >
              {open === l.id ? "收起白板" : "看白板"}
            </button>
            <button
              onClick={() => claim(l.id)}
              disabled={l.status === "contacted"}
              style={{ fontSize: 12, padding: "4px 12px", borderRadius: 6, border: "none", background: l.status === "contacted" ? "#2a323d" : "var(--accent)", color: "#fff" }}
            >
              {l.status === "contacted" ? "已 claim" : "Claim"}
            </button>
          </div>
          {l.preference && <div style={{ fontSize: 13, color: "var(--muted)", marginTop: 6 }}>偏好:{l.preference}</div>}
          {l.slaDueAt && <div style={{ fontSize: 12, color: "#e0a84e", marginTop: 4 }}>SLA 截止:{new Date(l.slaDueAt).toLocaleString()}</div>}
          {open === l.id && (
            <pre style={{ marginTop: 10, background: "#0c0f13", padding: 12, borderRadius: 8, fontSize: 12, overflow: "auto" }}>
              {JSON.stringify(l.zoneData, null, 2)}
            </pre>
          )}
        </div>
      ))}
    </div>
  );
}
