import { useState } from "react";
import type { Lang } from "../lib/types";

const PERSONAS: { id: string; label: { zh: string; en: string } }[] = [
  { id: "gentleman", label: { zh: "资深绅士", en: "Senior Gentleman" } },
  { id: "auntie", label: { zh: "亲切阿姨", en: "Warm Auntie" } },
  { id: "young_pro", label: { zh: "专业青年", en: "Young Pro" } },
];

interface Props {
  onDone: (opts: { lang: Lang; persona: string }) => void;
}

export default function Onboarding({ onDone }: Props) {
  const [step, setStep] = useState(0);
  const [lang, setLang] = useState<Lang>("zh");
  const [persona, setPersona] = useState("gentleman");

  const card = (children: React.ReactNode) => (
    <div style={{ position: "fixed", inset: 0, background: "var(--bg)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 200 }}>
      <div style={{ width: 420, maxWidth: "90vw", padding: 28, background: "var(--panel)", borderRadius: 16, border: "1px solid var(--border)" }}>{children}</div>
    </div>
  );

  const btn = (label: string, onClick: () => void, primary = true) => (
    <button
      onClick={onClick}
      style={{ padding: "10px 18px", borderRadius: 8, border: primary ? "none" : "1px solid var(--border)", background: primary ? "var(--accent)" : "transparent", color: primary ? "#fff" : "var(--ink)", fontSize: 14 }}
    >
      {label}
    </button>
  );

  if (step === 0) {
    return card(
      <>
        <h2 style={{ marginTop: 0 }}>欢迎 / Welcome</h2>
        <p style={{ color: "var(--muted)" }}>选择你习惯的语言 · Choose your language</p>
        <div style={{ display: "flex", gap: 10, marginBottom: 20 }}>
          {(["zh", "en"] as Lang[]).map((l) => (
            <button
              key={l}
              onClick={() => setLang(l)}
              style={{ flex: 1, padding: 12, borderRadius: 10, border: lang === l ? "2px solid var(--accent)" : "1px solid var(--border)", background: "transparent", color: "var(--ink)", fontSize: 15 }}
            >
              {l === "zh" ? "中文" : "English"}
            </button>
          ))}
        </div>
        {btn(lang === "zh" ? "下一步" : "Next", () => setStep(1))}
      </>
    );
  }

  if (step === 1) {
    return card(
      <>
        <h2 style={{ marginTop: 0 }}>{lang === "zh" ? "隐私承诺" : "Our Privacy Promise"}</h2>
        <ul style={{ color: "var(--muted)", fontSize: 14, lineHeight: 1.7, paddingLeft: 18 }}>
          <li>{lang === "zh" ? "你提供的信息只用于生成本次规划草图。" : "Your inputs are only used to draft this plan."}</li>
          <li>{lang === "zh" ? "默认匿名,不强制注册。" : "Anonymous by default, no forced sign-up."}</li>
          <li>{lang === "zh" ? "只有你主动同意时,才会把信息交给经纪人。" : "We only hand off to a broker with your consent."}</li>
          <li>{lang === "zh" ? "所有建议均为一般性思路,非具体投资建议。" : "All output is general guidance, not specific advice."}</li>
        </ul>
        <div style={{ display: "flex", gap: 8 }}>
          {btn(lang === "zh" ? "上一步" : "Back", () => setStep(0), false)}
          {btn(lang === "zh" ? "我了解了" : "Got it", () => setStep(2))}
        </div>
      </>
    );
  }

  return card(
    <>
      <h2 style={{ marginTop: 0 }}>{lang === "zh" ? "选择讲解人" : "Pick your advisor voice"}</h2>
      <p style={{ color: "var(--muted)", fontSize: 14 }}>{lang === "zh" ? "AI 会用这个声音边画边讲解。" : "The AI narrates while drawing."}</p>
      <div style={{ display: "flex", flexDirection: "column", gap: 8, marginBottom: 20 }}>
        {PERSONAS.map((p) => (
          <button
            key={p.id}
            onClick={() => setPersona(p.id)}
            style={{ padding: 12, borderRadius: 10, border: persona === p.id ? "2px solid var(--accent)" : "1px solid var(--border)", background: "transparent", color: "var(--ink)", fontSize: 15, textAlign: "left" }}
          >
            {p.label[lang]}
          </button>
        ))}
      </div>
      <div style={{ display: "flex", gap: 8 }}>
        {btn(lang === "zh" ? "上一步" : "Back", () => setStep(1), false)}
        {btn(lang === "zh" ? "开始" : "Start", () => onDone({ lang, persona }))}
      </div>
    </>
  );
}
