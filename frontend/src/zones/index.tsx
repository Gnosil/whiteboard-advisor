import type { ComponentType } from "react";
import FamilyProfile from "./FamilyProfile";
import ProtectionGap from "./ProtectionGap";
import CoveragePlan from "./CoveragePlan";

// zone id → 纯函数渲染组件(data → JSX)。新增模板/zone 在此注册。
export const ZONE_RENDERERS: Record<string, ComponentType<{ data: any }>> = {
  family_profile: FamilyProfile,
  protection_gap: ProtectionGap,
  coverage_plan: CoveragePlan,
};
