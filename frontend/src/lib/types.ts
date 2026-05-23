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
  stale?: boolean;
}

export interface AiMessage {
  role: "user" | "ai";
  text: string;
  nextQuestion?: string | null;
  streaming?: boolean;
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

export interface AssetAccount {
  type: string;
  value?: number | null;
  unit?: string;
  note?: string;
}
export interface IncomeAssetsData {
  accounts: AssetAccount[];
  total_investable?: number | null;
  unit?: string;
  summary?: string;
}

export interface EduChild {
  name: string;
  location?: string;
  start_year?: number | null;
  annual_cost?: number | null;
  years?: number | null;
  unit?: string;
}
export interface EducationFundData {
  children: EduChild[];
  total_need?: number | null;
  funding_gap?: number | null;
  unit?: string;
  summary?: string;
}

export interface IncomeSource {
  name: string;
  annual?: number | null;
  from_age?: number | null;
}
export interface RetirementCashflowData {
  retire_age?: number | null;
  annual_expense?: number | null;
  income_sources?: IncomeSource[];
  gap_years?: number | null;
  unit?: string;
  summary?: string;
}

export interface EstateStructure {
  type: string;
  beneficiary?: string;
  jurisdiction?: string;
  note?: string;
}
export interface EstateSuccessionData {
  structures: EstateStructure[];
  tax_notes?: string;
  summary?: string;
}

export interface CrossBorderNote {
  jurisdiction: string;
  topic: string;
  detail?: string;
}
export interface CrossBorderNotesData {
  notes: CrossBorderNote[];
  summary?: string;
}

export interface DashboardHighlight {
  label: string;
  value: string;
  unit?: string;
}
export interface SummaryDashboardData {
  highlights: DashboardHighlight[];
  action_items?: string[];
  summary?: string;
}

export interface StagePlanItem {
  category: string;
  action: string;
  priority?: string | null;
  note?: string;
}
export interface LifeStageData {
  age_range?: string;
  focus?: string;
  items: StagePlanItem[];
  summary?: string;
}

export interface TemplateMeta {
  id: string;
  title: { zh: string; en: string };
}
