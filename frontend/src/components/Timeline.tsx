import { AnimatePresence, motion } from "framer-motion";
import type { Lang, ZoneMeta, ZoneStateEntry } from "../lib/types";
import { ZONE_RENDERERS } from "../zones";

interface Props {
  meta: ZoneMeta[];
  zones: Record<string, ZoneStateEntry>;
  focus: string | null;
  lang: Lang;
  onRefresh: (zoneId: string, title: string) => void;
}

// 竖向时间轴布局:用于"人生阶段规划"——表达 现在 → 未来 → 退休 的推进感
export default function Timeline({ meta, zones, focus, lang, onRefresh }: Props) {
  const ordered = [...meta].sort((a, b) => a.order - b.order);
  const last = ordered.length - 1;

  return (
    <div style={{ position: "relative", width: "100%", maxWidth: 720, margin: "0 auto", overflow: "auto" }}>
      {ordered.map((z, idx) => {
        const entry = zones[z.id];
        const Renderer = ZONE_RENDERERS[z.id];
        const isFocus = focus === z.id;
        const filled = !!entry?.data && Object.keys(entry.data).length > 0;
        const ageRange = (entry?.data?.age_range as string) || "";

        return (
          <div key={z.id} style={{ display: "flex", gap: 16, alignItems: "stretch" }}>
            {/* 时间轴轨道:连线 + 节点圆点 */}
            <div style={{ position: "relative", width: 24, flexShrink: 0 }}>
              {idx !== 0 && (
                <div style={{ position: "absolute", left: 11, top: 0, height: 16, width: 2, background: "var(--border-strong)" }} />
              )}
              <div
                style={{
                  position: "absolute",
                  left: 4,
                  top: 16,
                  width: 14,
                  height: 14,
                  borderRadius: "50%",
                  background: filled ? "var(--accent)" : "var(--panel)",
                  border: "2px solid var(--accent)",
                  boxShadow: isFocus ? "0 0 0 4px var(--accent-soft)" : "none",
                }}
              />
              {idx !== last && (
                <div style={{ position: "absolute", left: 11, top: 30, bottom: 0, width: 2, background: "var(--border-strong)" }} />
              )}
            </div>

            {/* 节点卡片 */}
            <motion.section
              layout
              initial={{ opacity: 0, y: 8 }}
              animate={{
                opacity: 1,
                y: 0,
                boxShadow: isFocus ? "0 0 0 2px var(--accent), 0 0 24px var(--accent-soft)" : "var(--shadow)",
              }}
              transition={{ type: "spring", stiffness: 220, damping: 24 }}
              style={{
                flex: 1,
                background: "var(--panel)",
                borderRadius: 14,
                padding: 16,
                border: "1px solid var(--border)",
                marginBottom: 18,
                minHeight: 64,
              }}
            >
              <div style={{ display: "flex", alignItems: "baseline", gap: 8, marginBottom: filled ? 12 : 0 }}>
                <span style={{ fontWeight: 700, fontSize: 16 }}>{z.title[lang]}</span>
                {ageRange && <span style={{ fontSize: 13, color: "var(--accent)" }}>{ageRange}</span>}
                {!filled && <span style={{ fontSize: 12, color: "var(--muted)" }}>· 待规划</span>}
                {filled && entry?.stale && (
                  <button
                    onClick={() => onRefresh(z.id, z.title[lang])}
                    title="上游信息已变,点击让 AI 更新这块"
                    style={{
                      marginLeft: "auto",
                      fontSize: 11,
                      padding: "2px 8px",
                      borderRadius: 6,
                      border: "1px solid var(--amber)",
                      background: "var(--amber-soft)",
                      color: "var(--amber)",
                    }}
                  >
                    ⟳ 上游已变,更新
                  </button>
                )}
              </div>
              <AnimatePresence mode="wait">
                {filled && Renderer ? (
                  <motion.div key={entry.version} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} transition={{ duration: 0.4 }}>
                    <Renderer data={entry.data} />
                  </motion.div>
                ) : null}
              </AnimatePresence>
            </motion.section>
          </div>
        );
      })}
    </div>
  );
}
