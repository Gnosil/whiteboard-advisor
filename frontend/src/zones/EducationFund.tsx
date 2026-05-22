import type { EducationFundData } from "../lib/types";
import { fmtMoney } from "../lib/format";

export default function EducationFund({ data }: { data: EducationFundData }) {
  return (
    <div>
      {(data.children ?? []).map((c, i) => (
        <div key={i} style={{ background: "#0f141b", border: "1px solid #2a323d", borderRadius: 10, padding: 10, marginBottom: 8 }}>
          <div style={{ display: "flex", justifyContent: "space-between" }}>
            <span style={{ fontWeight: 600 }}>{c.name}{c.location ? ` · ${c.location}` : ""}</span>
            <span style={{ color: "var(--accent)" }}>{fmtMoney(c.annual_cost, c.unit || data.unit)}/年</span>
          </div>
          <div style={{ fontSize: 12, color: "var(--muted)", marginTop: 2 }}>
            {c.start_year ? `${c.start_year} 年起` : ""}{c.years ? ` · 共 ${c.years} 年` : ""}
          </div>
        </div>
      ))}
      <div style={{ display: "flex", gap: 16, fontSize: 13, marginTop: 6 }}>
        {data.total_need != null && <span>总需求 <b>{fmtMoney(data.total_need, data.unit)}</b></span>}
        {data.funding_gap != null && <span style={{ color: "#ff9d6b" }}>缺口 <b>{fmtMoney(data.funding_gap, data.unit)}</b></span>}
      </div>
      {data.summary && <p style={{ marginTop: 8, marginBottom: 0, color: "var(--muted)", fontSize: 13 }}>{data.summary}</p>}
    </div>
  );
}
