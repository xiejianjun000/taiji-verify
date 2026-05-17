/**
 * TypeScript类型定义 for Taiji Verify Skill
 */

export interface TaijiVerifyConfig {
  apiUrl: string;
  strictMode: boolean;
}

export interface TaijiVerifyResponse {
  verdict: Verdict;
  is_passing: boolean;
  delta_s: number | null;
  risk_level: string | null;
  failures: Failure[];
  processing_time_ms: number;
  details?: Record<string, unknown>;
}

export type Verdict =
  | "pass"
  | "conditional_pass"
  | "corrected"
  | "block"
  | "escalate";

export interface Failure {
  mode_id: string;
  mode_name: string;
  severity: string;
  details: string;
  location?: string;
}

export interface BatchVerifyResponse {
  results: TaijiVerifyResponse[];
  total: number;
  passed: number;
  processing_time_ms: number;
}

export interface SkillContext<C = Record<string, unknown>> {
  text: string;
  config: C;
  user?: {
    id: string;
    name: string;
  };
  session?: {
    id: string;
  };
}

export interface SkillResult {
  success: boolean;
  message: string;
  metadata?: Record<string, unknown>;
  blocks?: Array<{
    type: "warning" | "error" | "info";
    text: string;
  }>;
}

export type Skill<C = Record<string, unknown>> = {
  name: string;
  description: string;
  triggers: string[];
  aliases?: string[];
  config?: {
    schema: Record<string, ConfigField>;
    defaults: C;
  };
  handle: (context: SkillContext<C>) => Promise<SkillResult>;
};

export interface ConfigField {
  type: "string" | "boolean" | "number";
  default: unknown;
  description?: string;
}
