import { AnimatePresence, motion } from "framer-motion";
import type { Lang, ZoneMeta, ZoneStateEntry } from "../lib/types";
import { ZONE_RENDERERS } from "../zones";

interface Props {
  meta: ZoneMeta[];
  zones: Record<string, ZoneStateEntry>;
  focus: string | null;
  lang: Lang;
}

export default function Whiteboard({ meta, zones, focus, lang }: Props) {
  const ordered = [...meta].sort((a, b) => a.order - b.order);

  return (
    <div
      style={{
        flex: 1,
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
        gap: 16,
        alignContent: "start",
        overflow: "auto",
        padding: 4,
      }}
    >
      {ordered.map((z) => {
        const entry = zones[z.id];
        const Renderer = ZONE_RENDERERS[z.id];
        const isFocus = focus === z.id;
        const filled = !!entry?.data && Object.keys(entry.data).length > 0;
        return (
          <motion.section
            key={z.id}
            layout
            initial={{ opacity: 0, scale: 0.92 }}
            animate={{
              opacity: 1,
              scale: 1,
              boxShadow: isFocus ? "0 0 0 2px var(--accent), 0 0 24px var(--accent-soft)" : "none",
            }}
            transition={{ type: "spring", stiffness: 220, damping: 24 }}
            style={{
              background: "var(--panel)",
              borderRadius: 14,
              padding: 16,
              border: "1px solid #232a33",
              minHeight: 120,
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
              <span style={{ fontWeight: 700 }}>{z.title[lang]}</span>
              {!filled && <span style={{ fontSize: 12, color: "var(--muted)" }}>· 待填充</span>}
            </div>
            <AnimatePresence mode="wait">
              {filled && Renderer ? (
                <motion.div
                  key={entry.version}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.4 }}
                >
                  <Renderer data={entry.data} />
                </motion.div>
              ) : (
                <div style={{ color: "#3a444f", fontSize: 13 }}>AI 将在这里画出内容…</div>
              )}
            </AnimatePresence>
          </motion.section>
        );
      })}
    </div>
  );
}
