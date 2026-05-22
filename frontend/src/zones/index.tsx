import type { ComponentType } from "react";
import FamilyProfile from "./FamilyProfile";
import ProtectionGap from "./ProtectionGap";
import CoveragePlan from "./CoveragePlan";
import IncomeAssets from "./IncomeAssets";
import EducationFund from "./EducationFund";
import RetirementCashflow from "./RetirementCashflow";
import EstateSuccession from "./EstateSuccession";
import CrossBorderNotes from "./CrossBorderNotes";
import SummaryDashboard from "./SummaryDashboard";

// zone id → 纯函数渲染组件(data → JSX)。新增 zone 在此注册。
export const ZONE_RENDERERS: Record<string, ComponentType<{ data: any }>> = {
  family_profile: FamilyProfile,
  income_assets: IncomeAssets,
  protection_gap: ProtectionGap,
  coverage_plan: CoveragePlan,
  education_fund: EducationFund,
  retirement_cashflow: RetirementCashflow,
  estate_succession: EstateSuccession,
  cross_border_notes: CrossBorderNotes,
  summary_dashboard: SummaryDashboard,
};
