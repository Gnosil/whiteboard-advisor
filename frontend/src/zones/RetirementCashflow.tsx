import type { RetirementCashflowData } from "../lib/types";
import { fmtMoney } from "../lib/format";

export default function RetirementCashflow({ data }: { data: RetirementCashflowData }) {
  return (
    <div>
      <div style={{ display: "flex", gap: 16, fontSize: 14, marginBottom: 10 }}>
        {data.retire_age != null && <span>退休年龄 <b>{data.retire_age}</b></span>}
        {data.annual_expense != null && <span>年支出 <b>{fmtMoney(data.annual_expense, data.unit)}</b></span>}
        {data.gap_years != null && <span style={{ color: "#ff9d6b" }}>缺口 <b>{data.gap_years}</b> 年</span>}
      </div>
      {(data.income_sources ?? []).map((s, i) => (
        <div key={i} style={{ display: "flex", justifyContent: "space-between", padding: "4px 0", fontSize: 13, borderBottom: "1px solid #1d242c" }}>
          <span>{s.name}{s.from_age ? ` (${s.from_age}岁起)` : ""}</span>
          <span style={{ color: "var(--accent)" }}>{fmtMoney(s.annual, data.unit)}/年</span>
        </div>
      ))}
      {data.summary && <p style={{ marginTop: 8, marginBottom: 0, color: "var(--muted)", fontSize: 13 }}>{data.summary}</p>}
    </div>
  );
}
