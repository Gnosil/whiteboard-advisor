export type Lang = "zh" | "en";

export interface ZoneMeta {
  id: string;
  order: number;
  title: { zh: string; en: string };
}

export interface ZoneStateEntry {
  id: string;
  data: Record<string, unknown>;
  version: number;
  animation?: "grow" | "morph" | "flash";
}

export interface AiMessage {
  role: "user" | "ai";
  text: string;
  nextQuestion?: string | null;
}

// ---- zone data 形状(与后端模板 JSON Schema 对应) ----

export interface FamilyMember {
  role: string;
  name?: string;
  age?: number | null;
  location?: string;
  note?: string;
}
export interface FamilyProfileData {
  members: FamilyMember[];
  summary?: string;
}

export interface GapItem {
  category: string;
  current?: number | null;
  recommended?: number | null;
  gap?: number | null;
  unit?: string;
  note?: string;
}
export interface ProtectionGapData {
  items: GapItem[];
  summary?: string;
}

export interface CoverageProduct {
  type: string;
  coverage?: number | null;
  term?: string;
  est_premium?: number | null;
  unit?: string;
  rationale: string;
}
export interface CoveragePlanData {
  products: CoverageProduct[];
  total_premium?: number | null;
  disclaimer?: string;
}
