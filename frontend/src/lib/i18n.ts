import type { Lang } from "./types";

type Dict = Record<string, { zh: string; en: string }>;

const STRINGS: Dict = {
  connected: { zh: "● 已连接", en: "● Connected" },
  connecting: { zh: "○ 连接中", en: "○ Connecting" },
  send: { zh: "发送", en: "Send" },
  newSession: { zh: "新建", en: "New" },
  share: { zh: "分享", en: "Share" },
  exportPdf: { zh: "导出PDF", en: "Export PDF" },
  inputPlaceholder: { zh: "说点什么…", en: "Say something…" },
  thinking: { zh: "AI 正在思考…", en: "AI is thinking…" },
  findBroker: { zh: "找经纪人深入", en: "Talk to a broker" },
  planDone: { zh: "规划草图已完成。要不要让一位持牌经纪人帮你深入做一版?", en: "Draft ready. Want a licensed broker to take it further?" },
  premiumOnly: { zh: "这是 Premium 功能。Demo 中点确定可模拟升级。", en: "Premium feature. Click OK to simulate upgrade in this demo." },
  idle: { zh: "还在吗?需要换个话题,或者继续刚才的规划?", en: "Still there? Want a new topic or continue?" },
};

export function t(key: keyof typeof STRINGS, lang: Lang): string {
  const entry = STRINGS[key];
  return entry ? entry[lang] : String(key);
}
