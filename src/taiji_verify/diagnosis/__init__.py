"""
Diagnosis Layer - Taiji Verify Layer 4

包含：
- symptom_map: 病候图（从core迁移）
- failure_modes: 失败检测器（从core迁移）
- global_fix_map: 全局修复图
- troubleshooting_atlas: 故障排除地图
"""

from taiji_verify.diagnosis.global_fix_map import (
    FixEntry,
    GlobalFixMap,
)
from taiji_verify.diagnosis.troubleshooting_atlas import (
    TroubleshootingAtlas,
    DiagnosisNode,
    DiagnosisResult,
)

__all__ = [
    "FixEntry",
    "GlobalFixMap",
    "TroubleshootingAtlas",
    "DiagnosisNode",
    "DiagnosisResult",
]
