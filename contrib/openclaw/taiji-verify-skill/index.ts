/**
 * Taiji Verify Skill for OpenClaw
 *
 * 使用方式:
 * 1. 安装: npm install @your-org/openclaw-skill-taiji-verify
 * 2. 配置: 在openclaw配置中添加技能
 * 3. 使用: /verify <文本> 或 "验证这个回答"
 */

import type { Skill, SkillContext, SkillResult } from "@openclaw/types";

interface VerifyConfig {
  apiUrl: string;
  strictMode: boolean;
}

interface TaijiResponse {
  verdict: "pass" | "conditional_pass" | "corrected" | "block" | "escalate";
  is_passing: boolean;
  delta_s: number | null;
  risk_level: string | null;
  failures: Array<{
    mode_id: string;
    mode_name: string;
    severity: string;
    details: string;
  }>;
  processing_time_ms: number;
}

/**
 * Taiji Verify Skill
 */
export const taijiVerifySkill: Skill<VerifyConfig> = {
  name: "taiji-verify",
  description: "太极验证 - 检查AI输出是否可信，无幻觉、无逻辑跳跃、无事实冲突",
  triggers: ["/verify", "/taiji", "/验证"],
  aliases: ["verify", "taiji"],

  config: {
    schema: {
      apiUrl: {
        type: "string",
        default: "http://localhost:8080",
        description: "Taiji Verify API地址",
      },
      strictMode: {
        type: "boolean",
        default: false,
        description: "严格模式 - 只允许pass判定",
      },
    },
    defaults: {
      apiUrl: "http://localhost:8080",
      strictMode: false,
    },
  },

  async handle(context: SkillContext<VerifyConfig>): Promise<SkillResult> {
    const { text, config } = context;
    const { apiUrl, strictMode } = config;

    if (!text || text.trim().length === 0) {
      return {
        success: false,
        message: "请提供要验证的文本，例如: /verify <文本>",
      };
    }

    try {
      const response = await fetch(`${apiUrl}/verify`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ text }),
      });

      if (!response.ok) {
        throw new Error(`API请求失败: ${response.status}`);
      }

      const result: TaijiResponse = await response.json();

      const verdictEmoji = result.is_passing ? "✅" : "❌";
      const verdictText = {
        pass: "通过",
        conditional_pass: "有条件通过",
        corrected: "修正后通过",
        block: "阻断",
        escalate: "升级",
      }[result.verdict];

      const deltaSInfo = result.delta_s
        ? ` | ΔS: ${result.delta_s.toFixed(3)}`
        : "";

      let message = `${verdictEmoji} **${verdictText}**${deltaSInfo}`;

      if (result.risk_level) {
        message += ` | 风险: ${result.risk_level}`;
      }

      if (result.failures && result.failures.length > 0) {
        message += "\n\n**检测到的问题:**";
        for (const failure of result.failures.slice(0, 3)) {
          message += `\n- ${failure.mode_name}: ${failure.details || failure.severity}`;
        }
      }

      message += `\n\n⏱️ 处理耗时: ${result.processing_time_ms}ms`;

      const shouldBlock =
        strictMode && result.verdict !== "pass"
          ? "⚠️ 严格模式: 输出未完全通过验证"
          : undefined;

      return {
        success: result.is_passing || !strictMode,
        message,
        metadata: {
          verdict: result.verdict,
          is_passing: result.is_passing,
          delta_s: result.delta_s,
          risk_level: result.risk_level,
          failures_count: result.failures?.length || 0,
          blocked: !!shouldBlock,
        },
        blocks: shouldBlock ? [{ type: "warning", text: shouldBlock }] : undefined,
      };
    } catch (error) {
      return {
        success: false,
        message: `验证失败: ${error instanceof Error ? error.message : "未知错误"}`,
        metadata: {
          error: error instanceof Error ? error.message : "未知错误",
        },
      };
    }
  },
};

/**
 * 批量验证命令
 */
export const taijiVerifyBatchSkill: Skill<VerifyConfig> = {
  name: "taiji-verify-batch",
  description: "批量验证多个文本",
  triggers: ["/verify-batch", "/verify-all"],

  config: taijiVerifySkill.config,

  async handle(context: SkillContext<VerifyConfig>): Promise<SkillResult> {
    const { text, config } = context;
    const { apiUrl } = config;

    const lines = text
      .split("\n")
      .map((l) => l.trim())
      .filter((l) => l.length > 0);

    if (lines.length === 0) {
      return {
        success: false,
        message: "请提供要验证的文本（每行一个）",
      };
    }

    try {
      const response = await fetch(`${apiUrl}/verify/batch`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ texts: lines }),
      });

      if (!response.ok) {
        throw new Error(`API请求失败: ${response.status}`);
      }

      const result = await response.json();

      const passRate = ((result.passed / result.total) * 100).toFixed(1);
      let message = `📊 **批量验证结果**\n\n`;
      message += `通过: ${result.passed}/${result.total} (${passRate}%)\n`;
      message += `耗时: ${result.processing_time_ms}ms\n\n`;

      for (const r of result.results.slice(0, 5)) {
        const emoji = r.is_passing ? "✅" : "❌";
        message += `${emoji} ${r.verdict}\n`;
      }

      if (result.results.length > 5) {
        message += `... 还有 ${result.results.length - 5} 条`;
      }

      return {
        success: result.passed === result.total,
        message,
        metadata: {
          total: result.total,
          passed: result.passed,
          pass_rate: result.passed / result.total,
        },
      };
    } catch (error) {
      return {
        success: false,
        message: `批量验证失败: ${error instanceof Error ? error.message : "未知错误"}`,
      };
    }
  },
};

export default [taijiVerifySkill, taijiVerifyBatchSkill];
