import type { IncomeAssetsData } from "../lib/types";
import { fmtMoney } from "../lib/format";

export default function IncomeAssets({ data }: { data: IncomeAssetsData }) {
  return (
    <div>
      {(data.accounts ?? []).map((a, i) => (
        <div
          key={i}
          style={{ display: "flex", justifyContent: "space-between", padding: "6px 0", borderBottom: "1px solid #1d242c", fontSize: 14 }}
        >
          <span>{a.type}{a.note ? ` · ${a.note}` : ""}</span>
          <span style={{ color: "var(--accent)" }}>{fmtMoney(a.value, a.unit || data.unit)}</span>
        </div>
      ))}
      {data.total_investable != null && (
        <div style={{ marginTop: 8, fontWeight: 600 }}>可投资总额:{fmtMoney(data.total_investable, data.unit)}</div>
      )}
      {data.summary && <p style={{ marginTop: 8, marginBottom: 0, color: "var(--muted)", fontSize: 13 }}>{data.summary}</p>}
    </div>
  );
}
