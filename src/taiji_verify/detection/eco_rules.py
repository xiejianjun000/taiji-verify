"""
Eco Rules - 环境监测数据质量审计规则引擎 (ECO-Audit V3.0)

包含 200 条已定义审计规则，覆盖 6 大维度：
  - 技术合规与反造假 (R001-R050, 50条)
  - 数据逻辑与真实性校验 (R051-R100, 50条)
  - 物理链路与环境完整性 (R101-R130, 30条)
  - 运维与质控规范 (R131-R160, 30条)
  - 第三方检测 (R161-R180, 20条)
  - 特定行业/因子 (R181-R200, 20条)

每条规则包含：
  - id: 规则编号
  - name: 规则名称
  - description: 规则描述
  - detection_logic: 检测逻辑说明
  - legal_basis: 法律法规映射依据
  - applicable_modes: 适用的审计模式 (快速/标准/完整)
  - dimension: 所属维度分类
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable, Optional, List
from datetime import datetime


# ============================================================================
# 维度常量
# ============================================================================

DIMENSION_TECHNICAL_COMPLIANCE = "技术合规与反造假"
DIMENSION_DATA_LOGIC = "数据逻辑与真实性校验"
DIMENSION_PHYSICAL_LINK = "物理链路与环境完整性"
DIMENSION_OPS_QC = "运维与质控规范"
DIMENSION_THIRD_PARTY = "第三方检测"
DIMENSION_INDUSTRY_SPECIFIC = "特定行业/因子"

ALL_DIMENSIONS = [
    DIMENSION_TECHNICAL_COMPLIANCE,
    DIMENSION_DATA_LOGIC,
    DIMENSION_PHYSICAL_LINK,
    DIMENSION_OPS_QC,
    DIMENSION_THIRD_PARTY,
    DIMENSION_INDUSTRY_SPECIFIC,
]

# ============================================================================
# 审计模式常量
# ============================================================================

MODE_FAST = "快速"
MODE_STANDARD = "标准"
MODE_COMPLETE = "完整"

ALL_MODES = [MODE_FAST, MODE_STANDARD, MODE_COMPLETE]


# ============================================================================
# 核心数据模型
# ============================================================================


@dataclass
class EcoRule:
    """
    生态环境审计规则数据模型。

    Attributes:
        id: 规则唯一标识，如 "R001"。
        name: 规则中文名称，如 "分析仪/工控机隐藏菜单与后门扫描"。
        description: 规则的简要描述。
        detection_logic: 检测逻辑的详细技术说明。
        legal_basis: 相关法律法规或技术标准依据。
        applicable_modes: 适用的审计模式列表，如 ["快速", "标准", "完整"]。
        dimension: 规则所属维度分类。
        enabled: 规则是否启用，默认为 True。
    """

    id: str
    name: str
    description: str
    detection_logic: str
    legal_basis: str
    applicable_modes: List[str]
    dimension: str
    enabled: bool = True

    def __post_init__(self):
        """确保 applicable_modes 是列表类型。"""
        if isinstance(self.applicable_modes, str):
            self.applicable_modes = [
                m.strip() for m in self.applicable_modes.split("/") if m.strip()
            ]
        # 确保 legal_basis 不为空
        if not self.legal_basis:
            self.legal_basis = "—"


# ============================================================================
# 规则工厂辅助函数
# ============================================================================


def _make_mode_str(modes: List[str]) -> str:
    """将模式列表格式化为可读字符串。"""
    return " / ".join(modes)


# ============================================================================
# 200 条已定义规则数据
# ============================================================================


def _build_all_rules() -> List[EcoRule]:
    """
    构建全部 200 条 ECO-Audit V3.0 审计规则。

    Returns:
        包含所有规则实例的列表。
    """
    rules = []

    # -----------------------------------------------------------------------
    # 维度一：技术合规与反造假 (R001-R050, 50条)
    # -----------------------------------------------------------------------
    _tech_rules = [
        EcoRule(
            id="R001",
            name="分析仪/工控机隐藏菜单与后门扫描",
            description="扫描工控机及分析仪固件中的隐藏菜单入口、后门程序及默认工程密码。",
            detection_logic="使用YARA规则库扫描工控机及分析仪固件，匹配已知的隐藏菜单入口、后门程序、默认工程密码等特征。",
            legal_basis="《办法》第4条第9项；环办监测函〔2024〕214号",
            applicable_modes=["快速", "标准", "完整"],
            dimension=DIMENSION_TECHNICAL_COMPLIANCE,
        ),
        EcoRule(
            id="R002",
            name="进程白名单与可疑进程扫描",
            description="提取工控机运行进程，与验收基线白名单比对，标记异常进程。",
            detection_logic="提取工控机所有运行进程，与验收基线进程白名单比对，标记新增/缺失进程。",
            legal_basis="《办法》第4条第8项；《刑法》第286条",
            applicable_modes=["快速", "标准", "完整"],
            dimension=DIMENSION_TECHNICAL_COMPLIANCE,
        ),
        EcoRule(
            id="R003",
            name="电子记录/日志完整性深度扫描",
            description="检测系统日志、操作日志中的异常痕迹。",
            detection_logic="扫描系统日志、操作日志、参数修改日志，检测长时段空白、异常删除、时间戳倒退或回填等痕迹。",
            legal_basis="《办法》第4条第8项/第11项；《大气污染防治法》第24条",
            applicable_modes=["标准", "完整"],
            dimension=DIMENSION_TECHNICAL_COMPLIANCE,
        ),
        EcoRule(
            id="R004",
            name="全参数一致性快检",
            description="分析仪EEPROM、数采仪、工控机参数与验收报告四方比对。",
            detection_logic="分析仪EEPROM参数、数采仪配置参数、工控机软件参数与验收报告、备案文件四方比对。",
            legal_basis="《办法》第4条第8项；《大气污染防治法》第24条",
            applicable_modes=["快速", "标准", "完整"],
            dimension=DIMENSION_TECHNICAL_COMPLIANCE,
        ),
        EcoRule(
            id="R005",
            name="数据保持/恒值输出功能审计",
            description="检查维护和校准状态下是否存在数据锁定功能。",
            detection_logic='检查"维护""校准"状态下是否存在数据锁定功能。',
            legal_basis="环办执法函〔2021〕484号；HJ 212-2025",
            applicable_modes=["标准", "完整"],
            dimension=DIMENSION_TECHNICAL_COMPLIANCE,
        ),
        EcoRule(
            id="R006",
            name="模拟信号注入/旁路功能检测",
            description="检测是否存在可导入外部数据替代真实监测数据的接口。",
            detection_logic="检测是否存在可导入外部数据替代真实监测数据的接口或功能。",
            legal_basis="《办法》第5条第5项；《刑法》第286条",
            applicable_modes=["标准", "完整"],
            dimension=DIMENSION_TECHNICAL_COMPLIANCE,
        ),
        EcoRule(
            id="R007",
            name="双套算法/参数集检测",
            description="比对显示通道与原始记录通道数据是否存在人为偏差。",
            detection_logic='同时读取"显示"和"原始记录"两个通道的数据，比对是否存在人为偏差。',
            legal_basis="《办法》第4条第8项；《产品质量法》",
            applicable_modes=["标准", "完整"],
            dimension=DIMENSION_TECHNICAL_COMPLIANCE,
        ),
        EcoRule(
            id="R008",
            name="远程控制/维护通道审计",
            description="扫描网络配置、开放端口、远程桌面服务及第三方远程软件。",
            detection_logic="扫描网络配置、开放端口、远程桌面服务、第三方远程软件。",
            legal_basis="环办监测函〔2024〕214号；《刑法》第285条",
            applicable_modes=["标准", "完整"],
            dimension=DIMENSION_TECHNICAL_COMPLIANCE,
        ),
        EcoRule(
            id="R009",
            name="基准模式序列/预设数据包检测",
            description="分析校准后数据序列，识别可预测的固定值排列。",
            detection_logic="分析校准后数据序列，识别可预测的固定值排列。",
            legal_basis="《办法》第5条第5项",
            applicable_modes=["标准", "完整"],
            dimension=DIMENSION_TECHNICAL_COMPLIANCE,
        ),
        EcoRule(
            id="R010",
            name="设备认证与铭牌一致性校验",
            description="核验CCEP认证证书真伪，比对铭牌信息与认证证书。",
            detection_logic="核验CCEP认证证书真伪，比对铭牌信息与认证证书、备案文件。",
            legal_basis="《产品质量法》第53条",
            applicable_modes=["快速", "标准", "完整"],
            dimension=DIMENSION_TECHNICAL_COMPLIANCE,
        ),
        EcoRule(
            id="R011",
            name="非法修改程序固件检测",
            description="哈希校验比对当前固件与厂家官方原始固件。",
            detection_logic="哈希校验比对当前固件与厂家官方原始固件。",
            legal_basis="《刑法》第286条",
            applicable_modes=["标准", "完整"],
            dimension=DIMENSION_TECHNICAL_COMPLIANCE,
        ),
        EcoRule(
            id="R012",
            name='"飞检"时空矛盾分析',
            description="核验采样人员/设备在同一天的地理分布和时间是否物理可行。",
            detection_logic="核验同一采样人员/设备在同一天的采样任务地理分布和时间是否物理可行。",
            legal_basis="《办法》第5条第6项",
            applicable_modes=["标准", "完整"],
            dimension=DIMENSION_TECHNICAL_COMPLIANCE,
        ),
        EcoRule(
            id="R013",
            name="软件阈值/限值设定审计",
            description="检查是否存在非法的数据输出上限、下限或过滤规则。",
            detection_logic="检查是否存在非法的数据输出上限、下限或过滤规则。",
            legal_basis="《办法》第4条第8项",
            applicable_modes=["标准", "完整"],
            dimension=DIMENSION_TECHNICAL_COMPLIANCE,
        ),
        EcoRule(
            id="R014",
            name="颗粒物采样嘴/探杆物理合规性检查",
            description="核验采样嘴尺寸、朝向、探杆长度是否与备案一致。",
            detection_logic="核验采样嘴尺寸、朝向、探杆长度是否与备案一致。",
            legal_basis="HJ 75-2017；GB/T 16157-1996",
            applicable_modes=["标准", "完整"],
            dimension=DIMENSION_TECHNICAL_COMPLIANCE,
        ),
        EcoRule(
            id="R015",
            name="回流气/尾气稀释干扰评估",
            description="计算回流气出口与采样嘴间距，评估稀释干扰程度。",
            detection_logic="计算回流气出口与采样嘴间距，建立模型评估稀释干扰程度。",
            legal_basis="《办法》第4条第4项；《大气污染防治法》第20条",
            applicable_modes=["标准", "完整"],
            dimension=DIMENSION_TECHNICAL_COMPLIANCE,
        ),
        EcoRule(
            id="R016",
            name="采样探头温度/加热状态审计",
            description="核验采样探头加热温度是否≥120℃。",
            detection_logic="核验采样探头加热温度是否≥120℃。",
            legal_basis="HJ 75-2017",
            applicable_modes=["标准", "完整"],
            dimension=DIMENSION_TECHNICAL_COMPLIANCE,
        ),
        EcoRule(
            id="R017",
            name="反吹系统工作状态审计",
            description="核验反吹频次和时长是否异常偏离合理范围。",
            detection_logic="核验反吹频次和时长是否异常偏离合理范围。",
            legal_basis="HJ 75-2017",
            applicable_modes=["标准", "完整"],
            dimension=DIMENSION_TECHNICAL_COMPLIANCE,
        ),
        EcoRule(
            id="R018",
            name="FID熄火数据一致性",
            description="识别FID熄火期间仍有恒值数据的异常。",
            detection_logic="识别FID熄火期间仍有恒值数据的异常。",
            legal_basis="HJ 1013-2019；《办法》第5条第5项",
            applicable_modes=["标准", "完整"],
            dimension=DIMENSION_TECHNICAL_COMPLIANCE,
        ),
        EcoRule(
            id="R019",
            name="VOCs采样管线温度校验",
            description="验证VOCs采样管线温度是否全程≥120℃。",
            detection_logic="验证VOCs采样管线温度是否全程≥120℃。",
            legal_basis="HJ 1013-2019",
            applicable_modes=["标准", "完整"],
            dimension=DIMENSION_TECHNICAL_COMPLIANCE,
        ),
        EcoRule(
            id="R020",
            name="采样时序完整性审计",
            description="比对采样泵启动→进样信号→测量完成→上报时间的时序链。",
            detection_logic="比对采样泵启动→进样信号→测量完成→上报时间的时序链。",
            legal_basis="HJ 355-2019",
            applicable_modes=["标准", "完整"],
            dimension=DIMENSION_TECHNICAL_COMPLIANCE,
        ),
        EcoRule(
            id="R021",
            name="水质采样器/供样泵状态审计",
            description="读取采样泵电流/功率，验证采样泵是否正常运行。",
            detection_logic="读取采样泵电流/功率，验证采样泵是否正常运行。",
            legal_basis="HJ 353-2019",
            applicable_modes=["标准", "完整"],
            dimension=DIMENSION_TECHNICAL_COMPLIANCE,
        ),
        EcoRule(
            id="R022",
            name="采样探头反吹周期关联分析",
            description="检测反吹频次和时长异常偏离合理范围。",
            detection_logic="反吹频次和时长异常偏离合理范围的检测。",
            legal_basis="HJ 75-2017",
            applicable_modes=["标准", "完整"],
            dimension=DIMENSION_TECHNICAL_COMPLIANCE,
        ),
        EcoRule(
            id="R023",
            name="分析仪光源/检测器状态审计",
            description="读取分析仪内部诊断参数（光源强度、检测器信号）。",
            detection_logic="读取分析仪内部诊断参数（光源强度、检测器信号）。",
            legal_basis="HJ 75-2017",
            applicable_modes=["标准", "完整"],
            dimension=DIMENSION_TECHNICAL_COMPLIANCE,
        ),
        EcoRule(
            id="R024",
            name="设备唯一标识完整性审计",
            description="核验各组件唯一标识编码是否符合EAN-13标准。",
            detection_logic="核验各组件唯一标识编码是否符合EAN-13标准。",
            legal_basis="HJ 212-2025",
            applicable_modes=["标准", "完整"],
            dimension=DIMENSION_TECHNICAL_COMPLIANCE,
        ),
        EcoRule(
            id="R025",
            name="软件升级/固件更新记录审计",
            description="核验系统软件升级后原有信息是否自动备份保存。",
            detection_logic="核验系统软件升级后原有信息是否自动备份保存。",
            legal_basis="环办监测函〔2024〕214号",
            applicable_modes=["标准", "完整"],
            dimension=DIMENSION_TECHNICAL_COMPLIANCE,
        ),
        EcoRule(
            id="R026",
            name="防爆安全合规性审计",
            description="检查防爆区域内设备是否具备有效的防爆合格证，核对防爆等级与现场危险区域划分是否匹配。",
            detection_logic="检查防爆区域（Ex区）内分析仪、接线盒、控制柜等设备是否具备有效的防爆合格证，核对防爆等级与现场危险区域划分（Zone 0/1/2）是否匹配，验证防爆密封接头是否密封完好。",
            legal_basis="GB 3836 系列（爆炸性环境设备）；HJ 75-2017（安装安全要求）；《安全生产法》第36条",
            applicable_modes=["完整"],
            dimension=DIMENSION_TECHNICAL_COMPLIANCE,
        ),
        EcoRule(
            id="R027",
            name="防腐蚀涂层/材质合规性检测",
            description="核验接触腐蚀性气体的部件材质是否符合介质腐蚀性要求，检查腐蚀程度超标情况。",
            detection_logic="核验采样探头、采样管线、冷凝器等接触腐蚀性气体的部件材质（如316L不锈钢、PTFE涂层）是否符合介质腐蚀性要求，检查腐蚀程度超标情况。",
            legal_basis="HJ 75-2017（6.2 材质要求）；HJ 76-2017（防腐性能检测）",
            applicable_modes=["标准"],
            dimension=DIMENSION_TECHNICAL_COMPLIANCE,
        ),
        EcoRule(
            id="R028",
            name="电源冗余与UPS状态审计",
            description="检查CEMS/水质在线监测系统是否配置UPS或双回路供电，验证UPS容量是否满足断电后持续运行要求。",
            detection_logic="检查CEMS/水质在线监测系统是否配置UPS或双回路供电，验证UPS容量是否满足断电后系统持续运行≥2小时要求，检查UPS充放电记录。",
            legal_basis="HJ 75-2017（7.3 供电要求）；HJ 355-2019（4.2 供电系统）",
            applicable_modes=["标准"],
            dimension=DIMENSION_TECHNICAL_COMPLIANCE,
        ),
        EcoRule(
            id="R029",
            name="数据加密传输合规性",
            description="检查数采仪与监控中心之间的数据传输是否采用加密协议，验证HJ 212-2025要求的数字签名和MAC校验机制是否启用。",
            detection_logic="检查数采仪与监控中心之间的数据传输是否采用加密协议（TLS 1.2+），验证HJ 212-2025要求的数字签名和MAC校验机制是否启用，检测明文传输行为。",
            legal_basis="HJ 212-2025（数据传输安全）；《网络安全法》第21条",
            applicable_modes=["完整"],
            dimension=DIMENSION_TECHNICAL_COMPLIANCE,
        ),
        EcoRule(
            id="R030",
            name="采样管线材质与密封性检测",
            description="检查采样管线材质是否为惰性材料，管线接头密封是否完好，是否存在漏气/漏液风险。",
            detection_logic="检查采样管线材质是否为PTFE/PFA等惰性材料，管线接头密封是否完好，是否存在漏气/漏液风险，验证管线加热温度传感器是否正常工作。",
            legal_basis="HJ 75-2017（6.3 采样管线）；HJ 1013-2019（VOCs采样管线）",
            applicable_modes=["标准"],
            dimension=DIMENSION_TECHNICAL_COMPLIANCE,
        ),
        EcoRule(
            id="R031",
            name="伴热管线温度连续监控",
            description="实时读取伴热管线各段温度传感器数据，检测温度低于设定阈值的持续时间和频率。",
            detection_logic="实时读取伴热管线各段温度传感器数据，检测温度低于设定阈值（通常≥120℃）的持续时间和频率，判断是否存在冷凝风险。",
            legal_basis="HJ 75-2017（6.3.3 伴热温度）；HJ 1013-2019",
            applicable_modes=["标准"],
            dimension=DIMENSION_TECHNICAL_COMPLIANCE,
        ),
        EcoRule(
            id="R032",
            name="冷凝器/干燥器工作状态审计",
            description="读取冷凝器温度、蠕动泵运行状态、干燥剂湿度指标，验证除水效率是否满足露点≤4℃要求。",
            detection_logic="读取冷凝器温度、蠕动泵运行状态、干燥剂湿度指标，验证除水效率是否满足露点≤4℃要求，检测冷凝水排放是否异常。",
            legal_basis="HJ 76-2017（5.2.5 水分去除）；HJ 75-2017",
            applicable_modes=["标准"],
            dimension=DIMENSION_TECHNICAL_COMPLIANCE,
        ),
        EcoRule(
            id="R033",
            name="预处理系统过滤器堵塞检测",
            description="通过压差传感器读数判断过滤器前后压差是否超过设定限值，分析过滤器更换周期是否合规。",
            detection_logic="通过压差传感器读数判断过滤器前后压差是否超过设定限值，结合历史数据趋势分析过滤器更换周期是否合规。",
            legal_basis="HJ 75-2017（运维管理要求）",
            applicable_modes=["快速"],
            dimension=DIMENSION_TECHNICAL_COMPLIANCE,
        ),
        EcoRule(
            id="R034",
            name="采样泵/抽气泵运行状态监控",
            description="读取采样泵运行电流、流量、真空度参数，与设备额定参数比对，检测泵效率下降等异常。",
            detection_logic="读取采样泵运行电流、流量、真空度参数，与设备额定参数比对，检测泵效率下降、叶片磨损等异常。",
            legal_basis="HJ 75-2017（运行维护）；HJ 355-2019",
            applicable_modes=["标准"],
            dimension=DIMENSION_TECHNICAL_COMPLIANCE,
        ),
        EcoRule(
            id="R035",
            name="零气发生器/零气纯度验证",
            description="检查零气发生器是否在线运行，检测输出零气中目标污染物浓度是否低于检测限的1/3。",
            detection_logic="检查零气发生器是否在线运行，检测输出零气中目标污染物浓度是否低于检测限的1/3，验证零气切换阀动作是否正常。",
            legal_basis="HJ 75-2017（校准要求）；HJ 76-2017（零气技术要求）",
            applicable_modes=["标准"],
            dimension=DIMENSION_TECHNICAL_COMPLIANCE,
        ),
        EcoRule(
            id="R036",
            name="标准物质/标气全链条追溯",
            description="核验标准气体的来源、有效期、浓度值及不确定度、领用/使用记录，检测超期使用或无证标气。",
            detection_logic="核验标准气体的来源（有证标物证书）、有效期、浓度值及不确定度、领用记录、使用记录，检测超期使用或无证标气。",
            legal_basis="《标准物质管理办法》；HJ 75-2017；HJ 355-2019",
            applicable_modes=["完整"],
            dimension=DIMENSION_TECHNICAL_COMPLIANCE,
        ),
        EcoRule(
            id="R037",
            name="标准溶液配制/标定记录审计",
            description="检查标准溶液配制记录是否完整，配制人员资质是否符合要求，标定曲线R²是否达标。",
            detection_logic="检查标准溶液配制记录（称量、定容、标定）是否完整，配制人员资质是否符合要求，有效期是否合规，标定曲线R²是否达标。",
            legal_basis="《标准物质管理办法》；HJ 355-2019（标液管理）",
            applicable_modes=["完整"],
            dimension=DIMENSION_TECHNICAL_COMPLIANCE,
        ),
        EcoRule(
            id="R038",
            name="标定曲线有效期及偏离度审计",
            description="检查各参数标定曲线的有效期，比对最近一次标定曲线与历史曲线的斜率/截距偏离度。",
            detection_logic="检查各参数标定曲线的有效期，比对最近一次标定曲线与历史曲线的斜率/截距偏离度，检测偏离超过±10%未重新标定的情况。",
            legal_basis="HJ 75-2017；HJ 355-2019（校准曲线管理）",
            applicable_modes=["标准"],
            dimension=DIMENSION_TECHNICAL_COMPLIANCE,
        ),
        EcoRule(
            id="R039",
            name="校准/标定时间合理性校验",
            description="检查校准操作是否在合理的时间间隔内执行，校准时间分布是否符合运维规范要求。",
            detection_logic="检查校准操作是否在合理的时间间隔内执行（如每日零点/跨度校准），校准时间分布是否符合运维规范要求，检测长期未校准情况。",
            legal_basis="HJ 75-2017（7.2 日常校准）；HJ 355-2019",
            applicable_modes=["快速"],
            dimension=DIMENSION_TECHNICAL_COMPLIANCE,
        ),
        EcoRule(
            id="R040",
            name="分析仪量程匹配性审计",
            description="核验分析仪量程设置与排污许可限值、执行排放标准限值的匹配度。",
            detection_logic="核验分析仪量程设置与排污许可限值、执行排放标准限值的匹配度，检测量程过大导致测量精度不足或量程过小导致频繁超量程的情况。",
            legal_basis="HJ 75-2017（量程选择原则）；《排污许可管理条例》",
            applicable_modes=["标准"],
            dimension=DIMENSION_TECHNICAL_COMPLIANCE,
        ),
        EcoRule(
            id="R041",
            name="数采仪数据缓存区完整性检测",
            description="检查数采仪内部数据缓存区容量和使用情况，验证断电/断网期间数据是否正常缓存。",
            detection_logic="检查数采仪内部数据缓存区容量和使用情况，验证断电/断网期间数据是否正常缓存，检测缓存数据是否存在覆盖或丢失。",
            legal_basis="HJ 212-2025（数据存储要求）；HJ 75-2017",
            applicable_modes=["标准"],
            dimension=DIMENSION_TECHNICAL_COMPLIANCE,
        ),
        EcoRule(
            id="R042",
            name="工控机/数采仪时间同步审计",
            description="检查数采仪、分析仪、工控机三者之间的系统时钟偏差，验证是否通过NTP协议同步。",
            detection_logic="检查数采仪、分析仪、工控机三者之间的系统时钟偏差，验证是否通过NTP协议与标准时间服务器同步，偏差超过±1分钟即告警。",
            legal_basis="HJ 212-2025（时间同步要求）；HJ 75-2017",
            applicable_modes=["快速"],
            dimension=DIMENSION_TECHNICAL_COMPLIANCE,
        ),
        EcoRule(
            id="R043",
            name="采样平台/梯子结构安全合规性",
            description="检查采样平台面积、护栏高度、承重、梯子宽度、防滑措施是否达标。",
            detection_logic="检查采样平台面积≥1.5m²、护栏高度≥1.2m、承重≥200kg/m²是否达标，梯子宽度≥0.9m、防滑措施是否到位。",
            legal_basis="HJ 1405-2024（采样平台建设要求）；GB 4053.3-2009",
            applicable_modes=["完整"],
            dimension=DIMENSION_TECHNICAL_COMPLIANCE,
        ),
        EcoRule(
            id="R044",
            name="视频监控盲区及合规性审计",
            description="检查排放口监控视频覆盖率是否覆盖关键节点，检测是否存在监控盲区或摄像头被遮挡。",
            detection_logic="检查排放口监控视频覆盖率是否覆盖采样平台、分析仪房、采样管路关键节点，检测是否存在监控盲区或摄像头被遮挡、转向。",
            legal_basis="HJ 1405-2024（视频监控要求）；《排污许可管理条例》",
            applicable_modes=["标准"],
            dimension=DIMENSION_TECHNICAL_COMPLIANCE,
        ),
        EcoRule(
            id="R045",
            name="分析仪量程切换逻辑合规性",
            description="检测双量程分析仪的量程切换逻辑是否符合规范，是否存在人为强制锁定低量程的行为。",
            detection_logic="检测双量程分析仪的量程切换逻辑是否符合规范（如自动切换触发条件），切换时数据是否有效标记，是否存在人为强制锁定低量程的行为。",
            legal_basis="HJ 76-2017（量程切换要求）；HJ 212-2025",
            applicable_modes=["标准"],
            dimension=DIMENSION_TECHNICAL_COMPLIANCE,
        ),
        EcoRule(
            id="R046",
            name="分析仪诊断参数阈值越界检测",
            description="读取分析仪自检诊断参数与技术规范允许范围比对，越界即触发合规告警。",
            detection_logic="读取分析仪自检诊断参数（光源能量、检测器噪声、电路偏移等），与技术规范中的允许范围比对，越界即触发合规告警。",
            legal_basis="HJ 76-2017（系统自检功能要求）",
            applicable_modes=["快速"],
            dimension=DIMENSION_TECHNICAL_COMPLIANCE,
        ),
        EcoRule(
            id="R047",
            name="CEMS系统响应时间合规性",
            description="通过注入标准气体记录响应时间（T90），与HJ 76-2017要求的响应时间限值比对。",
            detection_logic="通过注入标准气体记录响应时间（T90），与HJ 76-2017要求的响应时间限值比对，超标即判定系统响应异常。",
            legal_basis="HJ 76-2017（响应时间≤200s）",
            applicable_modes=["标准"],
            dimension=DIMENSION_TECHNICAL_COMPLIANCE,
        ),
        EcoRule(
            id="R048",
            name="烟气参数测量合规性",
            description="检查烟温、烟压、流速、湿度传感器的安装位置、标定状态和数据合理性。",
            detection_logic="检查烟温、烟压、流速、湿度传感器的安装位置、标定状态和数据合理性，检测流速低于量程20%仍正常运行的异常情况。",
            legal_basis="HJ 75-2017（烟气参数测量）；GB/T 16157-1996",
            applicable_modes=["标准"],
            dimension=DIMENSION_TECHNICAL_COMPLIANCE,
        ),
        EcoRule(
            id="R049",
            name="氨逃逸/逃逸氨监测合规性",
            description="检查脱硝系统出口是否安装氨逃逸监测设备，量程、校准周期、数据接入是否合规。",
            detection_logic="检查脱硝系统出口是否安装氨逃逸监测设备，量程是否覆盖0-30mg/m³范围，校准周期是否合规，数据是否纳入监控平台。",
            legal_basis="HJ 75-2017；DB13/2209-2025（河北火电厂氨排放限值）",
            applicable_modes=["标准"],
            dimension=DIMENSION_TECHNICAL_COMPLIANCE,
        ),
        EcoRule(
            id="R050",
            name="采样点位/排放口编号一致性校验",
            description="比对现场采样点位编号、分析仪配置编码、数采仪上报编号、排污许可证排放口编号的一致性。",
            detection_logic="比对现场采样点位编号、分析仪配置中的点位编码、数采仪上报的点位编号、排污许可证中的排放口编号，确保四者一致。",
            legal_basis="HJ 1405-2024（点位编码规则）；《排污许可管理条例》；HJ 212-2025",
            applicable_modes=["快速"],
            dimension=DIMENSION_TECHNICAL_COMPLIANCE,
        ),
    ]
    rules.extend(_tech_rules)

    # -----------------------------------------------------------------------
    # 维度二：数据逻辑与真实性校验 (R051-R100, 50条)
    # -----------------------------------------------------------------------
    _data_rules = [
        EcoRule(
            id="R051",
            name="氨氮-总氮逻辑矛盾检测",
            description="逐条比对氨氮与总氮值，标记氨氮>总氮的记录。",
            detection_logic="逐条比对氨氮与总氮值，标记氨氮>总氮的记录。",
            legal_basis="《水污染防治法》第39条/83条",
            applicable_modes=["快速", "标准", "完整"],
            dimension=DIMENSION_DATA_LOGIC,
        ),
        EcoRule(
            id="R052",
            name="COD-BOD/高锰酸盐指数逻辑矛盾检测",
            description="标记COD<BOD等违反化学原理的记录。",
            detection_logic="标记COD<BOD等违反化学原理的记录。",
            legal_basis="《水污染防治法》第39条",
            applicable_modes=["标准", "完整"],
            dimension=DIMENSION_DATA_LOGIC,
        ),
        EcoRule(
            id="R053",
            name="多因子同步骤降/骤升检测",
            description="监测多个因子是否发生无工况支持的同步剧烈变化。",
            detection_logic="监测多个因子是否发生无工况支持的同步剧烈变化。",
            legal_basis="《办法》第4条第2项/第4项/第6项",
            applicable_modes=["标准", "完整"],
            dimension=DIMENSION_DATA_LOGIC,
        ),
        EcoRule(
            id="R054",
            name="长期恒值/低波动异常检测",
            description="计算变异系数(CV)，标记变化幅度长期低于量程1%的时段。",
            detection_logic="计算变异系数(CV)，标记变化幅度长期低于量程1%的时段。",
            legal_basis="《办法》第4条第8项；HJ 75/356",
            applicable_modes=["快速", "标准", "完整"],
            dimension=DIMENSION_DATA_LOGIC,
        ),
        EcoRule(
            id="R055",
            name="治理设施-排放数据逻辑一致性校验",
            description="治理设施运行参数与排放浓度时间轴对齐和相关性分析。",
            detection_logic="治理设施运行参数与排放浓度时间轴对齐和相关性分析。",
            legal_basis="《办法》第4条第3项；《大气污染防治法》第20条",
            applicable_modes=["标准", "完整"],
            dimension=DIMENSION_DATA_LOGIC,
        ),
        EcoRule(
            id="R056",
            name="生产工况-排放数据逻辑一致性校验",
            description="生产负荷与排放数据时序关联分析。",
            detection_logic="生产负荷与排放数据时序关联分析。",
            legal_basis="《办法》第4条第3项",
            applicable_modes=["标准", "完整"],
            dimension=DIMENSION_DATA_LOGIC,
        ),
        EcoRule(
            id="R057",
            name="烟气参数-排放数据物理一致性校验",
            description="基于烟气组分比例计算理论值与实测值偏差。",
            detection_logic="基于烟气组分比例计算理论值与实测值偏差。",
            legal_basis="《办法》第4条第8项",
            applicable_modes=["标准", "完整"],
            dimension=DIMENSION_DATA_LOGIC,
        ),
        EcoRule(
            id="R058",
            name="数据突变/阶跃信号检测",
            description="使用LightGBM或滑动窗口算法检测突然阶跃。",
            detection_logic="LightGBM或滑动窗口算法检测突然阶跃。",
            legal_basis="《办法》第4条第8项；HJ 75",
            applicable_modes=["标准", "完整"],
            dimension=DIMENSION_DATA_LOGIC,
        ),
        EcoRule(
            id="R059",
            name="数据过度平滑/规律性波动检测",
            description="分析频谱特征和自相关性。",
            detection_logic="分析频谱特征和自相关性。",
            legal_basis="《办法》第4条第8项",
            applicable_modes=["标准", "完整"],
            dimension=DIMENSION_DATA_LOGIC,
        ),
        EcoRule(
            id="R060",
            name="排放总量与物料衡算的逻辑矛盾检测",
            description="基于排污许可证反推理论排放浓度范围。",
            detection_logic="基于排污许可证反推理论排放浓度范围。",
            legal_basis="《环境保护税法》；《排污许可管理条例》",
            applicable_modes=["标准", "完整"],
            dimension=DIMENSION_DATA_LOGIC,
        ),
        EcoRule(
            id="R061",
            name="校准/校验数据与运行数据的时间逻辑校验",
            description="核验校准时间戳是否在工作时间、是否在运维计划内。",
            detection_logic="核验校准时间戳是否在工作时间、是否在运维计划内。",
            legal_basis="HJ 355/75",
            applicable_modes=["标准", "完整"],
            dimension=DIMENSION_DATA_LOGIC,
        ),
        EcoRule(
            id="R062",
            name="反吹/维护操作与数据响应的逻辑校验",
            description="分析反吹后数据响应时间、恢复时间是否符合物理预期。",
            detection_logic="分析反吹后数据响应时间、恢复时间是否符合物理预期。",
            legal_basis="《办法》第5条第1项",
            applicable_modes=["标准", "完整"],
            dimension=DIMENSION_DATA_LOGIC,
        ),
        EcoRule(
            id="R063",
            name="多监测点位间数据逻辑一致性校验",
            description="比对同一企业多个排放口排放数据的相关性。",
            detection_logic="比对同一企业多个排放口排放数据的相关性。",
            legal_basis="—",
            applicable_modes=["标准", "完整"],
            dimension=DIMENSION_DATA_LOGIC,
        ),
        EcoRule(
            id="R064",
            name="监测数据与气象/季节变化逻辑一致性校验",
            description="分析排放浓度与气温、湿度、季节性生产规律的相关性。",
            detection_logic="分析排放浓度与气温、湿度、季节性生产规律的相关性。",
            legal_basis="—",
            applicable_modes=["完整"],
            dimension=DIMENSION_DATA_LOGIC,
        ),
        EcoRule(
            id="R065",
            name="排放量数据连续性/完整性校验",
            description="识别浓度数据正常但排放量数据长期为零或空值的断点。",
            detection_logic="识别浓度数据正常但排放量数据长期为零或空值的断点。",
            legal_basis="HJ 212-2025",
            applicable_modes=["快速", "标准", "完整"],
            dimension=DIMENSION_DATA_LOGIC,
        ),
        EcoRule(
            id="R066",
            name="烟尘/颗粒物浓度与烟气含氧量逻辑关联",
            description="分析颗粒物浓度与烟气含氧量的相关性，低氧高尘或高氧低尘的异常组合即触发可疑标记。",
            detection_logic="分析颗粒物浓度与烟气含氧量的相关性，低氧高尘或高氧低尘的异常组合即触发可疑标记；结合燃烧效率模型评估数据合理性。",
            legal_basis="HJ 75-2017；GB 13271-2014（锅炉排放标准）",
            applicable_modes=["标准"],
            dimension=DIMENSION_DATA_LOGIC,
        ),
        EcoRule(
            id="R067",
            name="等速跟踪偏差超限检测",
            description="读取颗粒物CEMS等速跟踪系数，检测采样流速与烟气流速的偏差是否超过±10%阈值。",
            detection_logic="读取颗粒物CEMS等速跟踪系数，检测采样流速与烟气流速的偏差是否超过±10%阈值，连续偏差超限即判定等速跟踪失效。",
            legal_basis="HJ 76-2017（等速跟踪功能要求）；GB/T 16157-1996",
            applicable_modes=["标准"],
            dimension=DIMENSION_DATA_LOGIC,
        ),
        EcoRule(
            id="R068",
            name="折算浓度与实测浓度换算逻辑校验",
            description="根据实测浓度和含氧量/过剩空气系数重新计算折算浓度，与上报的折算浓度比对。",
            detection_logic="根据实测浓度、实测含氧量/过剩空气系数，按照标准公式重新计算折算浓度，与上报的折算浓度比对，偏差超过±2%即标记异常。",
            legal_basis="HJ 75-2017；各污染物排放标准中的折算公式",
            applicable_modes=["快速"],
            dimension=DIMENSION_DATA_LOGIC,
        ),
        EcoRule(
            id="R069",
            name="小时均值/日均值计算逻辑合规性",
            description="验证小时均值和日均值是否由足够有效数据计算得出，检测不足有效时间仍出具均值的情况。",
            detection_logic="验证小时均值是否由有效数据（≥45min有效数据）计算得出，日均值是否由≥18个有效小时均值计算得出，检测不足有效时间仍出具均值的情况。",
            legal_basis="HJ 75-2017（数据有效性判别）；HJ 356-2019",
            applicable_modes=["标准"],
            dimension=DIMENSION_DATA_LOGIC,
        ),
        EcoRule(
            id="R070",
            name="超标数据截断/封顶检测",
            description="分析排放浓度数据分布，检测是否存在大量数据集中在量程上限或标准限值附近的'平顶'现象。",
            detection_logic="分析排放浓度数据分布，检测是否存在大量数据集中在量程上限或标准限值附近的'平顶'现象，判断是否人为设置数据上限。",
            legal_basis="《办法》第4条第8项（干扰数据）；《刑法》第286条",
            applicable_modes=["完整"],
            dimension=DIMENSION_DATA_LOGIC,
        ),
        EcoRule(
            id="R071",
            name="排放数据突变/阶跃异常检测",
            description="检测相邻采样周期内排放浓度的突变幅度，结合工况数据评估突变合理性。",
            detection_logic="检测相邻采样周期内排放浓度的突变幅度（如从10mg/m³突变到80mg/m³），结合工况数据（负荷、燃料）评估突变合理性。",
            legal_basis="《办法》第5条（伪造监测数据情形）；HJ 212-2025",
            applicable_modes=["标准"],
            dimension=DIMENSION_DATA_LOGIC,
        ),
        EcoRule(
            id="R072",
            name="排放数据与生产负荷关联性分析",
            description="将排放浓度/流量数据与DCS生产负荷关联分析，检测高负荷低排放或停产期间仍有排放的异常。",
            detection_logic="将排放浓度/流量数据与DCS生产负荷、燃料消耗量、运行时间关联分析，检测高负荷低排放或停产期间仍有排放的异常情况。",
            legal_basis="《办法》第5条第5项（凭空生成数据）；《排污许可管理条例》第19条",
            applicable_modes=["完整"],
            dimension=DIMENSION_DATA_LOGIC,
        ),
        EcoRule(
            id="R073",
            name="烟气湿度与脱硫效率逻辑关联",
            description="分析脱硫塔进出口烟气湿度变化与脱硫效率的逻辑关系，异常偏低即判定旁路或稀释。",
            detection_logic="分析脱硫塔进出口烟气湿度变化与脱硫效率的逻辑关系，湿法脱硫后烟气湿度应显著升高，异常偏低即判定旁路或稀释。",
            legal_basis="HJ 75-2017；HJ 76-2017",
            applicable_modes=["标准"],
            dimension=DIMENSION_DATA_LOGIC,
        ),
        EcoRule(
            id="R074",
            name="脱硝系统氨逃逸与NOx去除率关联",
            description="分析氨逃逸浓度与NOx去除率的相关性，评估喷氨量是否合理。",
            detection_logic="分析氨逃逸浓度与NOx去除率的相关性，高脱硝效率应伴随合理氨逃逸范围，氨逃逸过高说明喷氨过量，过低说明喷氨不足。",
            legal_basis="HJ 75-2017；DB13/2209-2025",
            applicable_modes=["标准"],
            dimension=DIMENSION_DATA_LOGIC,
        ),
        EcoRule(
            id="R075",
            name="SO₂-NOx协同治理逻辑校验",
            description="分析SO₂和NOx排放浓度的协同变化趋势，两者的去除效率应有合理的相关性。",
            detection_logic="分析SO₂和NOx排放浓度的协同变化趋势，脱硫脱硝设施同时运行时，两者的去除效率应有合理的相关性。",
            legal_basis="GB 13223-2011（火电厂大气污染物排放标准）；HJ 75-2017",
            applicable_modes=["标准"],
            dimension=DIMENSION_DATA_LOGIC,
        ),
        EcoRule(
            id="R076",
            name="SO₂-CO₂摩尔比异常检测",
            description="基于燃料含硫量和燃烧特性计算理论SO₂/CO₂摩尔比范围，检测实测比值偏离理论值过大的情况。",
            detection_logic="基于燃料含硫量和燃烧特性，计算理论SO₂/CO₂摩尔比范围，检测实测比值偏离理论值过大的情况（可能暗示稀释或旁路）。",
            legal_basis="GB 13223-2011；HJ 75-2017",
            applicable_modes=["完整"],
            dimension=DIMENSION_DATA_LOGIC,
        ),
        EcoRule(
            id="R077",
            name="烟气流量与物料平衡校验",
            description="基于燃料消耗量、鼓风量、烟气成分计算理论烟气量，与CEMS实测烟气流量比对。",
            detection_logic="基于燃料消耗量、鼓风量、烟气成分计算理论烟气量，与CEMS实测烟气流量比对，偏差超过±30%即判定流量数据可疑。",
            legal_basis="HJ 75-2017（烟气流量测量）；GB/T 16157-1996",
            applicable_modes=["完整"],
            dimension=DIMENSION_DATA_LOGIC,
        ),
        EcoRule(
            id="R078",
            name="排污许可限值超限智能判定",
            description="自动读取排污许可证中的排放限值，将在线监测数据与限值逐一对比，检测超标未标记情况。",
            detection_logic="自动读取排污许可证中的排放限值（小时均值、日均值、月均值），将在线监测数据与限值逐一对比，检测超标未标记情况。",
            legal_basis="《排污许可管理条例》第17条/第20条；GB 13223-2011",
            applicable_modes=["标准"],
            dimension=DIMENSION_DATA_LOGIC,
        ),
        EcoRule(
            id="R079",
            name="多参数质量守恒校验",
            description="基于碳平衡、硫平衡、氮平衡原理构建质量守恒方程，校验数据自洽性。",
            detection_logic="基于碳平衡、硫平衡、氮平衡原理，利用CO₂、SO₂、NOx等多参数浓度和烟气流量构建质量守恒方程，校验数据自洽性。",
            legal_basis="HJ 75-2017；GB/T 16157-1996",
            applicable_modes=["完整"],
            dimension=DIMENSION_DATA_LOGIC,
        ),
        EcoRule(
            id="R080",
            name="COD去除率与处理工艺匹配性",
            description="根据污水处理工艺设定合理COD去除率区间，检测去除率异常偏高或偏低的情况。",
            detection_logic="根据污水处理厂的设计处理工艺（AAO、SBR、氧化沟等），设定合理COD去除率区间，检测去除率异常偏高（>95%）或偏低的情况。",
            legal_basis="GB 18918-2002（城镇污水处理厂污染物排放标准）；HJ 355-2019",
            applicable_modes=["标准"],
            dimension=DIMENSION_DATA_LOGIC,
        ),
        EcoRule(
            id="R081",
            name="氨氮-总磷化学计量关系校验",
            description="基于生物脱氮除磷工艺的化学计量关系，分析氨氮去除与总磷去除的协同性。",
            detection_logic="基于生物脱氮除磷工艺的化学计量关系，分析氨氮去除与总磷去除的协同性，检测只去除氮不去除磷（或相反）的异常工艺。",
            legal_basis="GB 18918-2002；HJ 355-2019",
            applicable_modes=["标准"],
            dimension=DIMENSION_DATA_LOGIC,
        ),
        EcoRule(
            id="R082",
            name="排水量与进水量物料平衡校验",
            description="比对污水处理设施进水量与排水量，结合蒸发损失和污泥含水率计算理论排水量。",
            detection_logic="比对污水处理设施进水量与排水量，结合蒸发损失和污泥含水率计算理论排水量，偏差过大即判定水量数据异常。",
            legal_basis="HJ 353-2019（流量测量要求）；GB 18918-2002",
            applicable_modes=["标准"],
            dimension=DIMENSION_DATA_LOGIC,
        ),
        EcoRule(
            id="R083",
            name="pH值波动范围合理性检测",
            description="分析pH值时间序列，检测pH值长期恒定或频繁大幅波动的异常情况。",
            detection_logic="分析pH值时间序列，检测pH值长期恒定（方差<0.01）或频繁大幅波动（>2pH单位/小时）的异常情况。",
            legal_basis="HJ 355-2019；《办法》第5条第5项",
            applicable_modes=["快速"],
            dimension=DIMENSION_DATA_LOGIC,
        ),
        EcoRule(
            id="R084",
            name="溶解氧与曝气状态关联性",
            description="分析溶解氧浓度与曝气设备运行状态的相关性，矛盾即标记异常。",
            detection_logic="分析溶解氧浓度与曝气设备运行状态（电流/频率）的相关性，曝气运行但DO不升或DO升高但曝气停止的矛盾即标记异常。",
            legal_basis="HJ 355-2019（DO监测运维要求）",
            applicable_modes=["标准"],
            dimension=DIMENSION_DATA_LOGIC,
        ),
        EcoRule(
            id="R085",
            name="烟气参数与颗粒物测量相互干扰检测",
            description="分析烟气流速过低或过高对颗粒物测量的影响，标记数据有效性存疑。",
            detection_logic="分析烟气流速过低或过高对颗粒物测量的影响，流速低于5m/s或高于30m/s时颗粒物CEMS测量精度下降，应标记数据有效性存疑。",
            legal_basis="HJ 76-2017（测量范围要求）；HJ 836-2017",
            applicable_modes=["标准"],
            dimension=DIMENSION_DATA_LOGIC,
        ),
        EcoRule(
            id="R086",
            name="重金属/特征因子检测频次合规性",
            description="核查排污许可证要求的手工监测频次，检测是否按期开展，结果是否按时录入平台。",
            detection_logic="核查排污许可证要求的手工监测频次（如重金属每季度/每半年一次），检测是否按期开展，检测结果是否按时录入平台。",
            legal_basis="《排污许可管理条例》第17条；HJ 91.1-2019",
            applicable_modes=["标准"],
            dimension=DIMENSION_DATA_LOGIC,
        ),
        EcoRule(
            id="R087",
            name="季节性生产规律与排放数据偏离",
            description="基于企业历史排放数据建立季节性基线模型，检测当前排放数据与季节性基线的显著偏离。",
            detection_logic="基于企业历史排放数据建立季节性基线模型，检测当前排放数据与季节性基线的显著偏离（>2σ），识别非季节性异常。",
            legal_basis="《办法》第4条/第5条；HJ 212-2025",
            applicable_modes=["完整"],
            dimension=DIMENSION_DATA_LOGIC,
        ),
        EcoRule(
            id="R088",
            name="设备运行时长与产污时长匹配性",
            description="比对生产设施运行时间与污染治理设施运行时间，检测治理设施运行时间显著短于生产设施的情况。",
            detection_logic="比对生产设施运行时间（通过DCS/电表数据）与污染治理设施运行时间，检测治理设施运行时间显著短于生产设施的情况。",
            legal_basis="《大气污染防治法》第20条；《办法》第4条第4项",
            applicable_modes=["完整"],
            dimension=DIMENSION_DATA_LOGIC,
        ),
        EcoRule(
            id="R089",
            name="数据有效率/捕获率合规性",
            description="计算在线监测系统数据捕获率，月度捕获率低于90%即判定系统运行异常。",
            detection_logic="计算在线监测系统数据捕获率（有效数据条数/应采数据条数），月度捕获率低于90%即判定系统运行异常，需排查原因。",
            legal_basis="HJ 356-2019（数据有效性判别）；HJ 75-2017",
            applicable_modes=["快速"],
            dimension=DIMENSION_DATA_LOGIC,
        ),
        EcoRule(
            id="R090",
            name="标气核查结果与漂移修正逻辑",
            description="检查日常标气核查结果，当漂移超过±5%时是否执行了修正，检测漂移超标但未修正的数据。",
            detection_logic="检查日常标气核查结果，当漂移超过±5%时是否执行了修正，修正后的数据是否正确追溯，检测漂移超标但未修正的数据。",
            legal_basis="HJ 75-2017（漂移检查与修正）；HJ 355-2019",
            applicable_modes=["标准"],
            dimension=DIMENSION_DATA_LOGIC,
        ),
        EcoRule(
            id="R091",
            name="多点位排放口数据协同性分析",
            description="对同一排污单位多个排放口的排放数据进行协同分析，检测数据趋势高度一致的异常。",
            detection_logic="对同一排污单位多个排放口（如多根烟囱）的排放数据进行协同分析，检测各排口数据趋势高度一致但绝对值不同的异常（可能共享数据源）。",
            legal_basis="《办法》第5条第5项；HJ 212-2025",
            applicable_modes=["完整"],
            dimension=DIMENSION_DATA_LOGIC,
        ),
        EcoRule(
            id="R092",
            name="排放数据周期性循环检测",
            description="利用傅里叶变换或小波分析检测排放数据中的隐藏周期性模式，发现人为设定的循环数据序列。",
            detection_logic="利用傅里叶变换或小波分析检测排放数据中的隐藏周期性模式，发现人为设定的循环数据序列（如每天同一时间出现相同数值）。",
            legal_basis="《办法》第5条第5项（预设数据包）；环办监测函〔2024〕214号",
            applicable_modes=["完整"],
            dimension=DIMENSION_DATA_LOGIC,
        ),
        EcoRule(
            id="R093",
            name="工况标记与排放数据逻辑一致性",
            description="检查企业上报的工况标记与排放数据的逻辑一致性，标记停机期间仍有正常排放数据即判定矛盾。",
            detection_logic="检查企业上报的工况标记（启停机、故障、维护）与排放数据的逻辑一致性，标记停机期间仍有正常排放数据即判定矛盾。",
            legal_basis="《生态环境监测条例》第25条；《排污许可管理条例》第20条",
            applicable_modes=["标准"],
            dimension=DIMENSION_DATA_LOGIC,
        ),
        EcoRule(
            id="R094",
            name="脱硫剂/脱硝剂消耗量与去除效率关联",
            description="基于脱硫剂或脱硝剂消耗量理论计算应达到的去除效率，与CEMS实测去除效率比对。",
            detection_logic="基于脱硫剂（石灰石）或脱硝剂（液氨/尿素）的消耗量，理论计算应达到的去除效率，与CEMS实测去除效率比对，偏差过大即判定异常。",
            legal_basis="《排污许可管理条例》第19条；HJ 75-2017",
            applicable_modes=["完整"],
            dimension=DIMENSION_DATA_LOGIC,
        ),
        EcoRule(
            id="R095",
            name="VOCs组分与非甲烷总烃总量匹配",
            description="将VOCs在线监测的各组分浓度加和，与非甲烷总烃（NMHC）总量比对。",
            detection_logic="将VOCs在线监测的各组分浓度加和，与非甲烷总烃（NMHC）总量比对，组分加和不应超过总量，且应有合理占比关系。",
            legal_basis="HJ 1286-2023（NMHC-CEMS技术要求）；GB 37822-2019",
            applicable_modes=["标准"],
            dimension=DIMENSION_DATA_LOGIC,
        ),
        EcoRule(
            id="R096",
            name="颗粒物与气态污染物去除工艺关联分析",
            description="分析除尘设施与脱硫脱硝设施之间的协同效应，检测关联性是否合理。",
            detection_logic="分析除尘设施（电除尘/布袋）与脱硫脱硝设施之间的协同效应，检测颗粒物浓度变化与气态污染物去除效率的关联性是否合理。",
            legal_basis="HJ 75-2017；HJ 836-2017",
            applicable_modes=["完整"],
            dimension=DIMENSION_DATA_LOGIC,
        ),
        EcoRule(
            id="R097",
            name="在线监测数据与手工监测数据偏差",
            description="比对同一排放口同期在线监测数据与手工监测数据，计算相对偏差。",
            detection_logic="比对同一排放口同期在线监测数据与手工监测数据，计算相对偏差，超过标准允许偏差范围（通常±30%）即判定在线监测数据可疑。",
            legal_basis="HJ 75-2017（数据比对要求）；HJ 836-2017",
            applicable_modes=["标准"],
            dimension=DIMENSION_DATA_LOGIC,
        ),
        EcoRule(
            id="R098",
            name="数据标记合规性深度审计",
            description="检查数据标记类型的使用是否符合规范，检测将超标数据标记为维护/故障以逃避监管的行为。",
            detection_logic="检查数据标记类型（正常、维护、校准、故障、超量程）的使用是否符合规范，检测将超标数据标记为维护/故障以逃避监管的行为。",
            legal_basis="《生态环境监测条例》第25条（虚假标记为弄虚作假）；HJ 212-2025",
            applicable_modes=["完整"],
            dimension=DIMENSION_DATA_LOGIC,
        ),
        EcoRule(
            id="R099",
            name="历史数据回填/篡改痕迹检测",
            description="利用数据库事务日志、文件系统时间戳比对、数据时间戳连续性分析检测历史数据篡改痕迹。",
            detection_logic="利用数据库事务日志、文件系统mtime/atime比对、数据时间戳连续性分析，检测历史数据是否存在回填、修改、删除后重建的痕迹。",
            legal_basis="《办法》第4条第8项（篡改数据）；《刑法》第286条",
            applicable_modes=["完整"],
            dimension=DIMENSION_DATA_LOGIC,
        ),
        EcoRule(
            id="R100",
            name="多源数据交叉验证",
            description="将在线监测数据与电力消耗、燃料采购量、产品产量、环保税申报数据等多源数据交叉验证。",
            detection_logic="将在线监测数据与电力消耗、燃料采购量、产品产量、环保税申报数据等多源数据交叉验证，检测逻辑矛盾（如零用电却有正常排放）。",
            legal_basis="《环境保护税法》；《排污许可管理条例》；《办法》第5条",
            applicable_modes=["完整"],
            dimension=DIMENSION_DATA_LOGIC,
        ),
    ]
    rules.extend(_data_rules)

    # -----------------------------------------------------------------------
    # 维度三：物理链路与环境完整性 (R101-R130, 30条)
    # -----------------------------------------------------------------------
    _physical_rules = [
        EcoRule(
            id="R101",
            name="全程伴热温度链合规性审计",
            description="连续监测采样探头、伴热管线、冷凝器等关键节点温度。",
            detection_logic="连续监测采样探头、伴热管线、冷凝器等关键节点温度。",
            legal_basis="HJ 75-2017；HJ 1013-2019",
            applicable_modes=["标准", "完整"],
            dimension=DIMENSION_PHYSICAL_LINK,
        ),
        EcoRule(
            id="R102",
            name="采样管路气密性/压力逻辑校验",
            description="通过采样泵负载、管路压力校验是否存在漏气、堵塞或断开。",
            detection_logic="通过采样泵负载、管路压力校验是否存在漏气、堵塞或断开。",
            legal_basis="《办法》第4条第5项/第8项",
            applicable_modes=["标准", "完整"],
            dimension=DIMENSION_PHYSICAL_LINK,
        ),
        EcoRule(
            id="R103",
            name="等速跟踪/采样代表性审计",
            description="核验等速跟踪误差是否持续满足±8%要求。",
            detection_logic="核验等速跟踪误差是否持续满足±8%要求。",
            legal_basis="HJ 76-2017",
            applicable_modes=["标准", "完整"],
            dimension=DIMENSION_PHYSICAL_LINK,
        ),
        EcoRule(
            id="R104",
            name="全光路/全系统校准方式审计",
            description="核验执行的是全光路校准还是仅分析仪本机校准。",
            detection_logic="核验执行的是全光路校准还是仅分析仪本机校准。",
            legal_basis="HJ 75-2017",
            applicable_modes=["标准", "完整"],
            dimension=DIMENSION_PHYSICAL_LINK,
        ),
        EcoRule(
            id="R105",
            name="预处理系统适用性评估",
            description="评估CEMS预处理方式是否适用当前工况。",
            detection_logic="评估CEMS预处理方式是否适用当前工况。",
            legal_basis="HJ 75-2017",
            applicable_modes=["标准", "完整"],
            dimension=DIMENSION_PHYSICAL_LINK,
        ),
        EcoRule(
            id="R106",
            name="FID/分析仪核心传感器状态诊断",
            description="读取FID火焰状态、光学传感器光强等核心诊断参数。",
            detection_logic="读取FID火焰状态、光学传感器光强等核心诊断参数。",
            legal_basis="HJ 1013-2019",
            applicable_modes=["标准", "完整"],
            dimension=DIMENSION_PHYSICAL_LINK,
        ),
        EcoRule(
            id="R107",
            name="氨逃逸/易溶性气体伴热损失评估",
            description="评估易溶或易吸附气体在采样传输过程中的损失风险。",
            detection_logic="评估易溶或易吸附气体在采样传输过程中的损失风险。",
            legal_basis="DB13/2209-2025",
            applicable_modes=["标准", "完整"],
            dimension=DIMENSION_PHYSICAL_LINK,
        ),
        EcoRule(
            id="R108",
            name="采样时序完整性审计",
            description="比对采样泵启动→进样信号→测量完成→上报时间的时序链。",
            detection_logic="比对采样泵启动→进样信号→测量完成→上报时间的时序链。",
            legal_basis="HJ 355-2019",
            applicable_modes=["标准", "完整"],
            dimension=DIMENSION_PHYSICAL_LINK,
        ),
        EcoRule(
            id="R109",
            name="水质采样器/供样泵状态审计",
            description="读取采样泵电流/功率验证是否正常运行。",
            detection_logic="读取采样泵电流/功率验证是否正常运行。",
            legal_basis="HJ 353-2019",
            applicable_modes=["标准", "完整"],
            dimension=DIMENSION_PHYSICAL_LINK,
        ),
        EcoRule(
            id="R110",
            name="设备现场物理环境篡改风险评估",
            description="接入视频监控、门禁记录评估非授权人员异常进入。",
            detection_logic="接入视频监控、门禁记录评估非授权人员异常进入。",
            legal_basis="《生态环境监测条例》第13条",
            applicable_modes=["完整"],
            dimension=DIMENSION_PHYSICAL_LINK,
        ),
        EcoRule(
            id="R111",
            name="振动干扰对监测数据影响评估",
            description="实时监测振动频率和幅度，评估对颗粒物/流速测量的影响程度。",
            detection_logic="在采样平台或分析仪房安装振动传感器，实时监测振动频率和幅度，当振动超过设备允许阈值时，评估对颗粒物/流速测量的影响程度。",
            legal_basis="HJ 76-2017（安装环境要求）；GB/T 16157-1996",
            applicable_modes=["完整"],
            dimension=DIMENSION_PHYSICAL_LINK,
        ),
        EcoRule(
            id="R112",
            name="电磁干扰（EMI）对信号传输影响检测",
            description="检测分析仪信号线缆是否采用屏蔽电缆，评估现场强电磁环境对弱电信号的干扰风险。",
            detection_logic="检测分析仪信号线缆是否采用屏蔽电缆，接地是否良好，评估现场强电磁环境（变频器、高压设备）对弱电信号的干扰风险。",
            legal_basis="HJ 75-2017（电气安全）；GB/T 18268（电磁兼容性）",
            applicable_modes=["标准"],
            dimension=DIMENSION_PHYSICAL_LINK,
        ),
        EcoRule(
            id="R113",
            name="采样平台结构安全及合规性检测",
            description="检测采样平台面积、护栏高度、承重能力、防滑措施是否符合要求。",
            detection_logic="检测采样平台面积、护栏高度、承重能力、防滑措施是否符合HJ 1405-2024要求，平台锈蚀、松动等安全隐患即标记。",
            legal_basis="HJ 1405-2024（采样平台建设）；GB 4053.3-2009",
            applicable_modes=["完整"],
            dimension=DIMENSION_PHYSICAL_LINK,
        ),
        EcoRule(
            id="R114",
            name="采样孔/测试孔合规性检查",
            description="检查采样孔直径、数量、位置是否符合标准要求，采样孔盖板是否密封良好。",
            detection_logic="检查采样孔直径（≥φ80mm）、数量、位置是否符合GB/T 16157-1996要求，采样孔盖板是否密封良好，是否存在多个采样孔被违规使用。",
            legal_basis="GB/T 16157-1996（采样孔设置）；HJ/T 397-2007",
            applicable_modes=["标准"],
            dimension=DIMENSION_PHYSICAL_LINK,
        ),
        EcoRule(
            id="R115",
            name="环境温湿度对分析仪影响评估",
            description="验证分析仪房/站房内的温湿度是否在要求的工作范围内，超限即标记数据可信度降低。",
            detection_logic="读取分析仪房/站房内的温湿度传感器数据，验证是否在分析仪要求的工作范围内（通常5-40℃，湿度<85%RH），超限即标记数据可信度降低。",
            legal_basis="HJ 75-2017（站房环境要求）；HJ 353-2019",
            applicable_modes=["标准"],
            dimension=DIMENSION_PHYSICAL_LINK,
        ),
        EcoRule(
            id="R116",
            name="防雷接地系统合规性检测",
            description="检查CEMS站房及采样平台的防雷接地电阻、避雷器状态、信号线防雷措施。",
            detection_logic="检查CEMS站房及采样平台的防雷接地电阻（≤4Ω）、避雷器状态、信号线防雷措施，检测防雷失效风险。",
            legal_basis="HJ 75-2017（防雷要求）；GB 50057-2010（建筑物防雷设计规范）",
            applicable_modes=["标准"],
            dimension=DIMENSION_PHYSICAL_LINK,
        ),
        EcoRule(
            id="R117",
            name="站房门禁/入侵检测合规性",
            description="检查站房门禁系统是否正常运行，非授权时段的人员进出是否记录。",
            detection_logic="检查站房门禁系统是否正常运行，门禁日志是否完整，非授权时段的人员进出是否记录，检测门禁失效或人为破坏痕迹。",
            legal_basis="《生态环境监测条例》；HJ 75-2017（站房管理）",
            applicable_modes=["标准"],
            dimension=DIMENSION_PHYSICAL_LINK,
        ),
        EcoRule(
            id="R118",
            name="采样管路坡度/冷凝水排放合规性",
            description="检查采样管路坡度是否合规，冷凝水收集器是否定期排放。",
            detection_logic="检查采样管路坡度（通常≥3°向冷凝水收集器倾斜），冷凝水收集器是否定期排放，检测管路中积水导致的采样失真风险。",
            legal_basis="HJ 75-2017（采样管路安装）；HJ 1013-2019",
            applicable_modes=["标准"],
            dimension=DIMENSION_PHYSICAL_LINK,
        ),
        EcoRule(
            id="R119",
            name="气态汞监测采样管路特殊要求",
            description="检查气态汞监测系统采样管路材质及表面处理，检测管路吸附导致的汞损失风险。",
            detection_logic="检查气态汞监测系统采样管路是否采用硼硅玻璃或PTFE材质，管路内表面是否经硅烷化处理，检测管路吸附导致的汞损失风险。",
            legal_basis="HJ 1439-2026（气态汞采样管路要求）",
            applicable_modes=["完整"],
            dimension=DIMENSION_PHYSICAL_LINK,
        ),
        EcoRule(
            id="R120",
            name="水质采样管路死体积评估",
            description="计算水质采样管路滞留时间，评估样品代表性是否因管路过长或流量过低而降低。",
            detection_logic="计算水质采样管路从采样口到分析仪的滞留时间（死体积/流量），评估样品代表性是否因管路过长或流量过低而降低。",
            legal_basis="HJ 353-2019（采样管路要求）；HJ 355-2019",
            applicable_modes=["标准"],
            dimension=DIMENSION_PHYSICAL_LINK,
        ),
        EcoRule(
            id="R121",
            name="水质采样口位置合规性",
            description="检查水质采样口是否设置在污水排放口的充分混合段，距紊流源的距离是否满足要求。",
            detection_logic="检查水质采样口是否设置在污水排放口的充分混合段，距弯头/阀门等紊流源的距离是否满足≥5倍管径要求。",
            legal_basis="HJ 353-2019（采样口设置）；HJ 91.1-2019",
            applicable_modes=["标准"],
            dimension=DIMENSION_PHYSICAL_LINK,
        ),
        EcoRule(
            id="R122",
            name="烟气采样断面流场均匀性评估",
            description="通过CFD模拟或实测数据评估采样断面处烟气流速分布均匀性。",
            detection_logic="通过CFD模拟或实测数据评估采样断面处烟气流速分布均匀性，流速偏差超过±15%即判定采样断面不满足等速采样条件。",
            legal_basis="HJ 75-2017（采样断面选择）；GB/T 16157-1996",
            applicable_modes=["完整"],
            dimension=DIMENSION_PHYSICAL_LINK,
        ),
        EcoRule(
            id="R123",
            name="采样探头插入深度合规性",
            description="检查采样探头插入烟道/排放口的深度是否到达1/3~1/2截面直径位置。",
            detection_logic="检查采样探头插入烟道/排放口的深度是否到达1/3~1/2截面直径位置，检测插入过浅导致的代表性不足或过深导致的磨损风险。",
            legal_basis="HJ 75-2017（采样探头安装）；HJ 1405-2024",
            applicable_modes=["标准"],
            dimension=DIMENSION_PHYSICAL_LINK,
        ),
        EcoRule(
            id="R124",
            name="采样管线交叉污染检测",
            description="检测多排放口共用采样管线时是否存在交叉污染风险，评估切换阀密封性。",
            detection_logic="检测多排放口共用采样管线时是否存在交叉污染风险，评估切换阀密封性和管路清洗程序是否充分。",
            legal_basis="HJ 75-2017；HJ 1013-2019",
            applicable_modes=["标准"],
            dimension=DIMENSION_PHYSICAL_LINK,
        ),
        EcoRule(
            id="R125",
            name="现场噪声对监测设备影响",
            description="检测站房及周边噪声水平，评估高噪声环境对测量精度的影响。",
            detection_logic="检测站房及周边噪声水平，评估高噪声环境对超声波流量计、振动传感器等设备测量精度的影响。",
            legal_basis="HJ 76-2017（安装环境要求）",
            applicable_modes=["标准"],
            dimension=DIMENSION_PHYSICAL_LINK,
        ),
        EcoRule(
            id="R126",
            name="分析仪房/站房正压维持",
            description="检查站房是否维持微正压，防止外部污染空气渗入。",
            detection_logic="检查站房是否维持微正压（5-20Pa），防止外部污染空气渗入，检测门窗密封性及正压送风系统运行状态。",
            legal_basis="HJ 75-2017（站房要求）；HJ 353-2019",
            applicable_modes=["标准"],
            dimension=DIMENSION_PHYSICAL_LINK,
        ),
        EcoRule(
            id="R127",
            name="采样平台风速影响评估",
            description="在高风速条件下评估采样探头处烟气流向偏移对等速采样的影响。",
            detection_logic="在高风速条件下评估采样探头处烟气流向偏移对等速采样的影响，风速>10m/s时应标记数据可靠性降低。",
            legal_basis="HJ 75-2017；GB/T 16157-1996",
            applicable_modes=["标准"],
            dimension=DIMENSION_PHYSICAL_LINK,
        ),
        EcoRule(
            id="R128",
            name="采样口/平台防雨防雷措施",
            description="检查采样口是否配置防雨帽、采样平台是否有排水设施、防雷设施是否完好。",
            detection_logic="检查采样口是否配置防雨帽、采样平台是否有排水设施、防雷设施是否完好，检测雨水渗入采样管路导致的干扰风险。",
            legal_basis="HJ 1405-2024；HJ 75-2017",
            applicable_modes=["标准"],
            dimension=DIMENSION_PHYSICAL_LINK,
        ),
        EcoRule(
            id="R129",
            name="分析仪散热/通风条件评估",
            description="检查分析仪散热风扇运行状态、通风口通畅性、站房空调/排风系统是否正常运行。",
            detection_logic="检查分析仪散热风扇运行状态、通风口通畅性、站房空调/排风系统是否正常运行，散热不良导致的温度升高影响测量精度。",
            legal_basis="HJ 75-2017（站房环境要求）",
            applicable_modes=["标准"],
            dimension=DIMENSION_PHYSICAL_LINK,
        ),
        EcoRule(
            id="R130",
            name="采样管路保温层完整性检测",
            description="检查采样管路保温层是否完整无破损，检测局部热桥导致的冷凝风险。",
            detection_logic="检查采样管路保温层是否完整无破损，红外热成像检测保温层表面温度分布，检测局部热桥导致的冷凝风险。",
            legal_basis="HJ 75-2017（伴热保温要求）；HJ 1013-2019",
            applicable_modes=["标准"],
            dimension=DIMENSION_PHYSICAL_LINK,
        ),
    ]
    rules.extend(_physical_rules)

    # -----------------------------------------------------------------------
    # 维度四：运维与质控规范 (R131-R160, 30条)
    # -----------------------------------------------------------------------
    _ops_rules = [
        EcoRule(
            id="R131",
            name="校准/校验周期与内容合规审计",
            description="自动统计零点/量程校准、全系统校验周期是否符合规范。",
            detection_logic="自动统计零点/量程校准、全系统校验周期是否符合规范。",
            legal_basis="HJ 75-2017；HJ 355-2019",
            applicable_modes=["标准", "完整"],
            dimension=DIMENSION_OPS_QC,
        ),
        EcoRule(
            id="R132",
            name="校准/校验结果合规性与真实性审计",
            description="核验示值误差、漂移等指标是否在规范允许范围内。",
            detection_logic="核验示值误差、漂移等指标是否在规范允许范围内。",
            legal_basis="HJ 75-2017；HJ 355-2019；《标准物质管理办法》",
            applicable_modes=["标准", "完整"],
            dimension=DIMENSION_OPS_QC,
        ),
        EcoRule(
            id="R133",
            name="数据标记与设备状态一致性校验（增强版）",
            description="分析仪工作状态日志与数采仪上报标记状态逐时段比对。",
            detection_logic="分析仪工作状态日志与数采仪上报标记状态逐时段比对。",
            legal_basis="《办法》第5条第1项；《大气污染防治法》第20条",
            applicable_modes=["标准", "完整"],
            dimension=DIMENSION_OPS_QC,
        ),
        EcoRule(
            id="R134",
            name="数据标记与工况逻辑一致性校验",
            description="工况标记时段与真实生产状态参数比对。",
            detection_logic="工况标记时段与真实生产状态参数比对。",
            legal_basis="《办法》第4条第3项",
            applicable_modes=["标准", "完整"],
            dimension=DIMENSION_OPS_QC,
        ),
        EcoRule(
            id="R135",
            name="修约/补遗数据合规性审计",
            description="审计修约或补传数据的原因是否符合技术规范。",
            detection_logic="审计修约或补传数据的原因是否符合技术规范。",
            legal_basis="HJ 75-2017；《办法》第4条第12项",
            applicable_modes=["标准", "完整"],
            dimension=DIMENSION_OPS_QC,
        ),
        EcoRule(
            id="R136",
            name="无效数据时段判定合规性审计",
            description="自动计算规范要求的无效数据时段，与实际标记时段比对。",
            detection_logic="自动计算规范要求的无效数据时段，与实际标记时段比对。",
            legal_basis="HJ 356-2019",
            applicable_modes=["标准", "完整"],
            dimension=DIMENSION_OPS_QC,
        ),
        EcoRule(
            id="R137",
            name="维修后功能完整性验证审计",
            description="核验维修后是否在规定时间内进行了校准或质控测试。",
            detection_logic="核验维修后是否在规定时间内进行了校准或质控测试。",
            legal_basis="HJ 75-2017第11.5(d)条",
            applicable_modes=["标准", "完整"],
            dimension=DIMENSION_OPS_QC,
        ),
        EcoRule(
            id="R138",
            name="耗材/试剂/标液更换周期审计",
            description="核验耗材更换时间是否在规定周期内。",
            detection_logic="核验耗材更换时间是否在规定周期内。",
            legal_basis="HJ 355-2019",
            applicable_modes=["快速", "标准", "完整"],
            dimension=DIMENSION_OPS_QC,
        ),
        EcoRule(
            id="R139",
            name="运维人员到场真实性审计",
            description="运维台账与门禁、视频监控、车辆GPS交叉验证。",
            detection_logic="运维台账与门禁、视频监控、车辆GPS交叉验证。",
            legal_basis="《办法》第5条",
            applicable_modes=["标准", "完整"],
            dimension=DIMENSION_OPS_QC,
        ),
        EcoRule(
            id="R140",
            name="排污单位监督义务履行情况审计",
            description="核验排污单位是否及时发现运维违规并书面指出。",
            detection_logic="核验排污单位是否及时发现运维违规并书面指出。",
            legal_basis="《排污许可管理条例》第19-20条",
            applicable_modes=["完整"],
            dimension=DIMENSION_OPS_QC,
        ),
        EcoRule(
            id="R141",
            name="应急演练执行记录审计",
            description="检查运维单位是否按规定频次开展应急演练，演练记录是否完整。",
            detection_logic="检查运维单位是否按规定频次（至少每年一次）开展应急演练，演练记录是否完整（演练方案、签到表、演练报告），检测虚假演练。",
            legal_basis="《生态环境监测条例》；《突发环境事件应急管理办法》",
            applicable_modes=["完整"],
            dimension=DIMENSION_OPS_QC,
        ),
        EcoRule(
            id="R142",
            name="备机/备用设备管理合规性",
            description="检查关键设备是否配置备机，备机是否定期启动测试，状态是否满足应急切换条件。",
            detection_logic="检查关键设备（分析仪、采样泵等）是否配置备机，备机是否定期启动测试（至少每季度一次），备机状态是否满足应急切换条件。",
            legal_basis="HJ 75-2017（运维管理要求）；HJ 355-2019",
            applicable_modes=["标准"],
            dimension=DIMENSION_OPS_QC,
        ),
        EcoRule(
            id="R143",
            name="废液/废试剂合规处置",
            description="检查水质在线监测系统产生的废液是否分类收集、标识、台账登记，是否交由有资质单位处置。",
            detection_logic="检查水质在线监测系统产生的废液（消解液、标准液残液等）是否分类收集、标识、台账登记，是否交由有资质单位处置。",
            legal_basis="《固体废物污染环境防治法》；《危险废物管理条例》",
            applicable_modes=["标准"],
            dimension=DIMENSION_OPS_QC,
        ),
        EcoRule(
            id="R144",
            name="运维人员资质及培训记录",
            description="检查运维人员是否持有相关资格证书，培训记录是否完整，检测无证上岗或证书过期情况。",
            detection_logic="检查运维人员是否持有相关资格证书（如自动监控运维培训合格证），培训记录是否完整，检测无证上岗或证书过期情况。",
            legal_basis="《生态环境监测条例》第43条；《检验检测机构资质认定》",
            applicable_modes=["标准"],
            dimension=DIMENSION_OPS_QC,
        ),
        EcoRule(
            id="R145",
            name="运维台账完整性和一致性校验",
            description="检查运维台账是否连续完整，检测台账记录与系统操作日志不一致的情况。",
            detection_logic="检查运维台账（巡检记录、校准记录、故障维修记录、备件更换记录）是否连续完整，检测台账记录与系统操作日志不一致的情况。",
            legal_basis="HJ 75-2017（运维台账要求）；HJ 355-2019",
            applicable_modes=["完整"],
            dimension=DIMENSION_OPS_QC,
        ),
        EcoRule(
            id="R146",
            name="运维巡检频次合规性",
            description="检查运维巡检是否满足最低频次要求，检测巡检间隔超时或巡检记录造假。",
            detection_logic="检查运维巡检是否满足最低频次要求（烟气CEMS每周至少1次、水质在线监测每周至少2次），检测巡检间隔超时或巡检记录造假。",
            legal_basis="HJ 75-2017（7.3 巡检要求）；HJ 355-2019",
            applicable_modes=["快速"],
            dimension=DIMENSION_OPS_QC,
        ),
        EcoRule(
            id="R147",
            name="备件更换记录与寿命周期匹配",
            description="检查关键备件的更换记录与厂家建议的寿命周期比对，检测超期未更换或异常频繁更换。",
            detection_logic="检查关键备件（光源、检测器、蠕动泵管、过滤器等）的更换记录，与厂家建议的寿命周期比对，检测超期未更换或异常频繁更换。",
            legal_basis="HJ 75-2017（运维管理）；设备厂家技术规范",
            applicable_modes=["标准"],
            dimension=DIMENSION_OPS_QC,
        ),
        EcoRule(
            id="R148",
            name="运维合同/第三方运维合规性",
            description="检查运维合同是否在有效期内，运维单位是否具备相应资质，约定内容是否落实。",
            detection_logic="检查运维合同是否在有效期内，运维单位是否具备相应资质（如运维能力证书），合同约定的运维内容和频次是否落实。",
            legal_basis="《生态环境监测条例》；《排污许可管理条例》",
            applicable_modes=["完整"],
            dimension=DIMENSION_OPS_QC,
        ),
        EcoRule(
            id="R149",
            name="故障响应时间及恢复时效审计",
            description="统计系统故障发生到运维人员到场的时间及故障修复时间，检测超过合同约定时限的情况。",
            detection_logic="统计系统故障发生到运维人员到场的时间（响应时间）及故障修复时间（恢复时间），检测超过合同约定时限的情况。",
            legal_basis="HJ 75-2017（故障处理要求）；运维合同",
            applicable_modes=["标准"],
            dimension=DIMENSION_OPS_QC,
        ),
        EcoRule(
            id="R150",
            name="校准/核查仪器溯源管理",
            description="检查用于日常校准的标气/标液/标准物质是否具有溯源证书，是否在有效期内。",
            detection_logic="检查用于日常校准的标气/标液/标准物质是否具有溯源证书，是否在有效期内，是否按期送检，检测无溯源链的校准行为。",
            legal_basis="《标准物质管理办法》；ISO/IEC 17025；HJ 75-2017",
            applicable_modes=["完整"],
            dimension=DIMENSION_OPS_QC,
        ),
        EcoRule(
            id="R151",
            name="系统停机/恢复审批流程合规性",
            description="检查监测系统计划停机是否经过环保部门审批，恢复运行后是否完成校准和比对。",
            detection_logic="检查监测系统计划停机是否经过环保部门审批，停机期间是否有替代监测方案，恢复运行后是否完成校准和比对。",
            legal_basis="《排污许可管理条例》；HJ 75-2017",
            applicable_modes=["标准"],
            dimension=DIMENSION_OPS_QC,
        ),
        EcoRule(
            id="R152",
            name="运维耗材采购合规性",
            description="检查运维耗材的采购来源是否正规，是否具备产品合格证和检验报告。",
            detection_logic="检查运维耗材（标气、标液、试剂、滤芯等）的采购来源是否正规，是否具备产品合格证和检验报告，检测使用假冒或劣质耗材。",
            legal_basis="《产品质量法》；《标准物质管理办法》",
            applicable_modes=["标准"],
            dimension=DIMENSION_OPS_QC,
        ),
        EcoRule(
            id="R153",
            name="系统软件备份与恢复能力",
            description="检查监测系统软件是否定期备份，备份介质是否安全存储，恢复测试是否按期执行。",
            detection_logic="检查监测系统软件（含参数配置、数据库、标定曲线）是否定期备份，备份介质是否安全存储，恢复测试是否按期执行。",
            legal_basis="环办监测函〔2024〕214号；《网络安全法》",
            applicable_modes=["标准"],
            dimension=DIMENSION_OPS_QC,
        ),
        EcoRule(
            id="R154",
            name="交叉运维/同一运维人员多地运维合理性",
            description="分析同一运维人员在同一天内的巡检任务地理分布和时间安排，评估是否物理可行。",
            detection_logic="分析同一运维人员在同一天内的巡检任务地理分布和时间安排，评估是否物理可行，检测同一人在同一时间点出现在不同地点的矛盾。",
            legal_basis="《办法》第5条第6项；《生态环境监测条例》",
            applicable_modes=["完整"],
            dimension=DIMENSION_OPS_QC,
        ),
        EcoRule(
            id="R155",
            name="运维费用与运维质量匹配性分析",
            description="分析运维费用投入与运维质量指标的相关性，检测费用过低导致运维质量下降的情况。",
            detection_logic="分析运维费用投入与运维质量指标（数据捕获率、故障率、校准合格率）的相关性，检测费用过低导致运维质量下降的情况。",
            legal_basis="《排污许可管理条例》；《生态环境监测条例》",
            applicable_modes=["完整"],
            dimension=DIMENSION_OPS_QC,
        ),
        EcoRule(
            id="R156",
            name="质控图/质控数据趋势分析",
            description="建立关键参数的Shewhart质控图，检测超出控制限或连续偏移等失控趋势。",
            detection_logic="建立关键参数（零点、跨度、回收率）的Shewhart质控图，检测超出控制限或连续7点单侧偏移等失控趋势。",
            legal_basis="HJ 75-2017（质量控制要求）；HJ 355-2019",
            applicable_modes=["标准"],
            dimension=DIMENSION_OPS_QC,
        ),
        EcoRule(
            id="R157",
            name="系统年度比对/校验合规性",
            description="检查是否按要求每年至少开展一次CEMS与手工监测方法的比对校验，比对结果是否达标。",
            detection_logic="检查是否按要求每年至少开展一次CEMS与手工监测方法的比对校验，比对结果是否达标（相对误差、相对准确度等指标）。",
            legal_basis="HJ 75-2017（年度校验要求）；HJ 836-2017",
            applicable_modes=["标准"],
            dimension=DIMENSION_OPS_QC,
        ),
        EcoRule(
            id="R158",
            name="异常数据调查与处理记录",
            description="检查在线监测系统产生异常数据后是否开展调查并形成处理报告。",
            detection_logic="检查在线监测系统产生异常数据（超标、突变、缺失）后，是否开展调查并形成处理报告，检测异常数据未调查即标记为无效的情况。",
            legal_basis="《生态环境监测条例》；HJ 356-2019",
            applicable_modes=["标准"],
            dimension=DIMENSION_OPS_QC,
        ),
        EcoRule(
            id="R159",
            name="运维工具/仪器仪表计量检定",
            description="检查运维人员使用的便携式仪器是否按期计量检定，检定证书是否有效。",
            detection_logic="检查运维人员使用的便携式仪器（如流量计、温度计、气压计、标气减压阀）是否按期计量检定，检定证书是否有效。",
            legal_basis="《计量法》；《标准物质管理办法》",
            applicable_modes=["标准"],
            dimension=DIMENSION_OPS_QC,
        ),
        EcoRule(
            id="R160",
            name="系统退役/报废数据归档合规性",
            description="检查监测系统退役或报废时，历史监测数据是否完整归档并移交环保部门。",
            detection_logic="检查监测系统退役或报废时，历史监测数据是否完整归档并移交环保部门，检测数据随设备报废而丢失的情况。",
            legal_basis="《生态环境监测条例》；《排污许可管理条例》；《档案法》",
            applicable_modes=["完整"],
            dimension=DIMENSION_OPS_QC,
        ),
    ]
    rules.extend(_ops_rules)

    # -----------------------------------------------------------------------
    # 维度五：第三方检测 (R161-R180, 20条)
    # -----------------------------------------------------------------------
    _third_party_rules = [
        EcoRule(
            id="R161",
            name="手工监测报告方法适用性审计",
            description="评估报告中选用的手工监测方法是否适用被测工况。",
            detection_logic="评估报告中选用的手工监测方法是否适用被测工况。",
            legal_basis="—",
            applicable_modes=["标准", "完整"],
            dimension=DIMENSION_THIRD_PARTY,
        ),
        EcoRule(
            id="R162",
            name="手工监测采样流程合规性审计",
            description="核验采样时间、时长、间隔、流量、体积等参数。",
            detection_logic="核验采样时间、时长、间隔、流量、体积等参数。",
            legal_basis="—",
            applicable_modes=["标准", "完整"],
            dimension=DIMENSION_THIRD_PARTY,
        ),
        EcoRule(
            id="R163",
            name="实验室分析质控合规性审计",
            description="核验平行样、加标回收、全程序空白、恒重称量等质控要求。",
            detection_logic="核验平行样、加标回收、全程序空白、恒重称量等质控要求。",
            legal_basis="—",
            applicable_modes=["标准", "完整"],
            dimension=DIMENSION_THIRD_PARTY,
        ),
        EcoRule(
            id="R164",
            name="报告数据溯源与原始记录一致性校验",
            description="核验原始数据与正式报告在数值、时间、人员等信息上是否一致。",
            detection_logic="核验原始数据与正式报告在数值、时间、人员等信息上是否一致。",
            legal_basis="—",
            applicable_modes=["标准", "完整"],
            dimension=DIMENSION_THIRD_PARTY,
        ),
        EcoRule(
            id="R165",
            name="第三方检测机构资质与信用风险预警",
            description="核验CMA资质有效性，接入公开处罚信息库查询历史违法记录。",
            detection_logic="核验CMA资质有效性，接入公开处罚信息库查询历史违法记录。",
            legal_basis="—",
            applicable_modes=["快速", "标准", "完整"],
            dimension=DIMENSION_THIRD_PARTY,
        ),
        EcoRule(
            id="R166",
            name="分包管理合规性审计",
            description="检查第三方检测机构是否存在违规分包行为，分包单位是否具备相应资质。",
            detection_logic="检查第三方检测机构是否存在违规分包行为，分包比例是否超过总检测任务的允许上限，分包单位是否具备相应资质。",
            legal_basis="《检验检测机构资质认定管理办法》；《生态环境监测条例》第45条",
            applicable_modes=["完整"],
            dimension=DIMENSION_THIRD_PARTY,
        ),
        EcoRule(
            id="R167",
            name="第三方检测人员资质核查",
            description="核查第三方检测机构采样、分析、审核、报告人员的资质证书和培训记录。",
            detection_logic="核查第三方检测机构采样、分析、审核、报告人员的资质证书和培训记录，检测无证上岗、超范围检测或证书过期情况。",
            legal_basis="《检验检测机构资质认定》（RB/T 214-2017）；《生态环境监测条例》",
            applicable_modes=["完整"],
            dimension=DIMENSION_THIRD_PARTY,
        ),
        EcoRule(
            id="R168",
            name="第三方检测实验室CMA资质合规性",
            description="检查第三方检测实验室是否持有有效的CMA资质证书，检测项目是否在资质认定范围内。",
            detection_logic="检查第三方检测实验室是否持有有效的CMA资质证书，检测项目是否在资质认定范围内，检测超范围出具检测报告。",
            legal_basis="《检验检测机构资质认定管理办法》；RB/T 214-2017",
            applicable_modes=["标准"],
            dimension=DIMENSION_THIRD_PARTY,
        ),
        EcoRule(
            id="R169",
            name="第三方检测采样规范性审计",
            description="检查第三方检测采样过程是否遵循采样规范，采样记录是否完整，采样容器是否合规。",
            detection_logic="检查第三方检测采样过程是否遵循采样规范（HJ/T 397-2007等），采样记录（时间、地点、气象条件）是否完整，采样容器是否合规。",
            legal_basis="HJ/T 397-2007；GB/T 16157-1996；HJ 91.1-2019",
            applicable_modes=["标准"],
            dimension=DIMENSION_THIRD_PARTY,
        ),
        EcoRule(
            id="R170",
            name="第三方检测报告数据溯源性",
            description="检查第三方检测报告中的检测数据是否可溯源到原始记录。",
            detection_logic="检查第三方检测报告中的检测数据是否可溯源到原始记录（采样记录、分析原始记录、仪器谱图），检测数据链断裂或无法溯源的情况。",
            legal_basis="《检验检测机构资质认定管理办法》；RB/T 214-2017",
            applicable_modes=["完整"],
            dimension=DIMENSION_THIRD_PARTY,
        ),
        EcoRule(
            id="R171",
            name="第三方检测原始记录完整性",
            description="检查第三方检测原始记录是否完整，检测缺失原始记录或后补记录的情况。",
            detection_logic="检查第三方检测原始记录（采样记录、仪器分析记录、计算过程、审核签字）是否完整，检测缺失原始记录或后补记录的情况。",
            legal_basis="《检验检测机构资质认定管理办法》；《办法》第4条",
            applicable_modes=["完整"],
            dimension=DIMENSION_THIRD_PARTY,
        ),
        EcoRule(
            id="R172",
            name="第三方检测仪器校准/溯源合规性",
            description="检查第三方检测机构使用的分析仪器是否按期校准和溯源。",
            detection_logic="检查第三方检测机构使用的分析仪器是否按期校准和溯源，校准证书是否在有效期内，检测使用未校准仪器出具数据。",
            legal_basis="《计量法》；RB/T 214-2017",
            applicable_modes=["标准"],
            dimension=DIMENSION_THIRD_PARTY,
        ),
        EcoRule(
            id="R173",
            name="第三方检测报告一致性校验",
            description="将第三方检测报告中的结论数据与排污单位自行监测数据、在线监测数据进行交叉比对。",
            detection_logic="将第三方检测报告中的结论数据与排污单位自行监测数据、在线监测数据进行交叉比对，检测显著偏差或矛盾。",
            legal_basis="《排污许可管理条例》第17条；《办法》第4条/第5条",
            applicable_modes=["标准"],
            dimension=DIMENSION_THIRD_PARTY,
        ),
        EcoRule(
            id="R174",
            name="第三方检测机构信用/处罚记录",
            description="查询第三方检测机构的信用记录、行政处罚记录、从业禁止信息。",
            detection_logic="查询第三方检测机构的信用记录、行政处罚记录、从业禁止信息，检测存在严重失信记录或禁业处罚仍在执行期的机构。",
            legal_basis="《生态环境监测条例》第43条/第45条；《检验检测机构资质认定管理办法》",
            applicable_modes=["快速"],
            dimension=DIMENSION_THIRD_PARTY,
        ),
        EcoRule(
            id="R175",
            name="现场采样与实验室分析时间链校验",
            description="检查样品采集时间、样品送达实验室时间、分析开始时间的时序逻辑。",
            detection_logic="检查样品采集时间、样品送达实验室时间、分析开始时间的时序逻辑，检测采样到分析时间超过样品保存期限的情况。",
            legal_basis="HJ 91.1-2019（样品保存要求）；《检验检测机构资质认定管理办法》",
            applicable_modes=["标准"],
            dimension=DIMENSION_THIRD_PARTY,
        ),
        EcoRule(
            id="R176",
            name="第三方检测加标回收率合规性",
            description="检查第三方检测报告中加标回收率数据是否在合理范围内。",
            detection_logic="检查第三方检测报告中加标回收率数据是否在合理范围内（通常70%-130%），检测回收率异常但报告仍判定合格的情况。",
            legal_basis="HJ 91.1-2019；《检验检测机构资质认定管理办法》",
            applicable_modes=["标准"],
            dimension=DIMENSION_THIRD_PARTY,
        ),
        EcoRule(
            id="R177",
            name="第三方检测质控样考核合规性",
            description="检查第三方检测机构是否按要求参加质控样考核，考核结果是否在允许范围内。",
            detection_logic="检查第三方检测机构是否按要求参加质控样考核（有证标准物质或能力验证），考核结果是否在允许范围内。",
            legal_basis="RB/T 214-2017；《检验检测机构资质认定管理办法》",
            applicable_modes=["标准"],
            dimension=DIMENSION_THIRD_PARTY,
        ),
        EcoRule(
            id="R178",
            name="第三方检测采样气象条件合规性",
            description="检查第三方检测采样期间的气象条件是否符合采样规范要求。",
            detection_logic="检查第三方检测采样期间的气象条件（风速、风向、温度、湿度）是否符合采样规范要求，检测不利气象条件下采样导致的数据偏差。",
            legal_basis="HJ/T 397-2007；GB/T 16157-1996",
            applicable_modes=["标准"],
            dimension=DIMENSION_THIRD_PARTY,
        ),
        EcoRule(
            id="R179",
            name="第三方检测样品流转管控合规性",
            description="检查第三方检测样品流转过程中的冷链运输、保存条件、交接记录是否完整。",
            detection_logic="检查第三方检测样品流转过程中的冷链运输、保存条件、交接记录是否完整，检测样品在流转过程中变质或受污染的情况。",
            legal_basis="HJ 91.1-2019（样品管理）；《检验检测机构资质认定管理办法》",
            applicable_modes=["标准"],
            dimension=DIMENSION_THIRD_PARTY,
        ),
        EcoRule(
            id="R180",
            name="第三方检测报告审核/签发合规性",
            description="检查第三方检测报告的三级审核是否完整，签字人员是否具备相应资格。",
            detection_logic="检查第三方检测报告的三级审核（编制、审核、签发）是否完整，签字人员是否具备相应资格，检测跳过审核流程直接出具报告。",
            legal_basis="RB/T 214-2017（报告管理）；《检验检测机构资质认定管理办法》",
            applicable_modes=["标准"],
            dimension=DIMENSION_THIRD_PARTY,
        ),
    ]
    rules.extend(_third_party_rules)

    # -----------------------------------------------------------------------
    # 维度六：特定行业/因子 (R181-R200, 20条)
    # -----------------------------------------------------------------------
    _industry_rules = [
        EcoRule(
            id="R181",
            name="垃圾焚烧——工况标记合规性审计",
            description="炉膛温度、蒸汽流量、垃圾投料量与工况标记逻辑校验。",
            detection_logic="炉膛温度、蒸汽流量、垃圾投料量与工况标记逻辑校验。",
            legal_basis="生态环境部令第10号",
            applicable_modes=["标准", "完整"],
            dimension=DIMENSION_INDUSTRY_SPECIFIC,
        ),
        EcoRule(
            id="R182",
            name="湿法脱硫——SO₂冷凝损失评估",
            description="评估冷干直抽法CEMS的SO₂冷凝损失风险。",
            detection_logic="评估冷干直抽法CEMS的SO₂冷凝损失风险。",
            legal_basis="HJ 75-2017",
            applicable_modes=["标准", "完整"],
            dimension=DIMENSION_INDUSTRY_SPECIFIC,
        ),
        EcoRule(
            id="R183",
            name="VOCs治理设施——旁路异常开启检测",
            description="建立逻辑校验模型识别旁路偷排或稀释排放。",
            detection_logic="建立逻辑校验模型识别旁路偷排或稀释排放。",
            legal_basis="《办法》第4条第4项",
            applicable_modes=["标准", "完整"],
            dimension=DIMENSION_INDUSTRY_SPECIFIC,
        ),
        EcoRule(
            id="R184",
            name="VOCs排放——末端稀释干扰检测",
            description="NMHC骤降而O₂异常升高时判定为疑似稀释。",
            detection_logic="NMHC骤降而O₂异常升高时判定为疑似稀释。",
            legal_basis="《办法》第4条第2项/第4项",
            applicable_modes=["标准", "完整"],
            dimension=DIMENSION_INDUSTRY_SPECIFIC,
        ),
        EcoRule(
            id="R185",
            name="超低排放——排放浓度与治理设施能力匹配性评估",
            description="评估排放浓度长期稳定在极低水平与治理能力上限是否存在矛盾。",
            detection_logic="评估排放浓度是否长期稳定在极低水平与治理能力上限是否存在矛盾。",
            legal_basis="—",
            applicable_modes=["标准", "完整"],
            dimension=DIMENSION_INDUSTRY_SPECIFIC,
        ),
        EcoRule(
            id="R186",
            name="超声波流量计——关键参数透明性与双套算法审计",
            description="读取K系数、声程、各声道时差等诊断参数，比对内部原始流速与显示流速。",
            detection_logic="读取K系数、声程、各声道时差等诊断参数，比对内部原始流速与显示流速。",
            legal_basis="—",
            applicable_modes=["标准", "完整"],
            dimension=DIMENSION_INDUSTRY_SPECIFIC,
        ),
        EcoRule(
            id="R187",
            name="氨逃逸监测——采样位置合规性与数据质量校验",
            description="识别采样位置是否符合标准本意，结合喷氨量校验逻辑性。",
            detection_logic="识别采样位置是否符合标准本意，结合喷氨量校验逻辑性。",
            legal_basis="—",
            applicable_modes=["标准", "完整"],
            dimension=DIMENSION_INDUSTRY_SPECIFIC,
        ),
        EcoRule(
            id="R188",
            name="非甲烷总烃（NMHC）——FID检测器灵敏度衰减审计",
            description="连续监控FID检测器在同浓度标气下的峰面积变化趋势。",
            detection_logic="连续监控FID检测器在同浓度标气下的峰面积变化趋势。",
            legal_basis="—",
            applicable_modes=["标准", "完整"],
            dimension=DIMENSION_INDUSTRY_SPECIFIC,
        ),
        EcoRule(
            id="R189",
            name="水泥行业氨逃逸监测合规性",
            description="检查水泥窑炉SNCR/SCR脱硝系统出口是否安装氨逃逸在线监测设备，数据是否接入环保监控平台。",
            detection_logic="检查水泥窑炉SNCR/SCR脱硝系统出口是否安装氨逃逸在线监测设备，量程是否覆盖0-10mg/m³范围，数据是否接入环保监控平台。",
            legal_basis="GB 4915-2013（水泥工业大气污染物排放标准）；HJ 75-2017",
            applicable_modes=["标准"],
            dimension=DIMENSION_INDUSTRY_SPECIFIC,
        ),
        EcoRule(
            id="R190",
            name="水泥行业颗粒物无组织排放监测",
            description="检查水泥厂矿区、堆场、输送廊道等无组织排放源是否按要求设置TSP在线监测。",
            detection_logic="检查水泥厂矿区、堆场、输送廊道等无组织排放源是否按要求设置TSP在线监测，监测数据是否满足无组织排放管控要求。",
            legal_basis="GB 4915-2013；GB 16297-1996（无组织排放监控）",
            applicable_modes=["标准"],
            dimension=DIMENSION_INDUSTRY_SPECIFIC,
        ),
        EcoRule(
            id="R191",
            name="电厂脱硝系统运行合规性",
            description="检查火电厂SCR/SNCR脱硝系统的喷氨量、催化剂层压降、进出口NOx浓度，评估脱硝系统运行是否正常。",
            detection_logic="检查火电厂SCR/SNCR脱硝系统的喷氨量、催化剂层压降、进出口NOx浓度，评估脱硝系统运行是否正常，催化剂是否失活。",
            legal_basis="GB 13223-2011；HJ 75-2017",
            applicable_modes=["标准"],
            dimension=DIMENSION_INDUSTRY_SPECIFIC,
        ),
        EcoRule(
            id="R192",
            name="火电厂汞及其化合物排放监测",
            description="检查火电厂是否按要求开展汞及其化合物的手工监测或在线监测，监测频次是否合规。",
            detection_logic="检查火电厂是否按要求开展汞及其化合物的手工监测或在线监测（气态汞），监测频次是否合规，数据是否达标。",
            legal_basis="GB 13223-2011；HJ 1439-2026（气态汞监测技术要求）",
            applicable_modes=["完整"],
            dimension=DIMENSION_INDUSTRY_SPECIFIC,
        ),
        EcoRule(
            id="R193",
            name="垃圾焚烧厂二噁英排放监测",
            description="检查垃圾焚烧厂是否按许可要求开展二噁英排放的手工监测，采样和分析方法是否符合标准。",
            detection_logic="检查垃圾焚烧厂是否按许可要求开展二噁英排放的手工监测（至少每年一次），采样和分析方法是否符合HJ 77.2-2008标准。",
            legal_basis="GB 18485-2014（生活垃圾焚烧污染控制标准）；HJ 77.2-2008",
            applicable_modes=["完整"],
            dimension=DIMENSION_INDUSTRY_SPECIFIC,
        ),
        EcoRule(
            id="R194",
            name="垃圾焚烧厂炉温合规性监控",
            description="检查垃圾焚烧炉二燃室温度是否持续≥850℃，低于850℃的持续时间是否超过标准要求。",
            detection_logic="检查垃圾焚烧炉二燃室温度是否持续≥850℃（二噁英分解温度），温度低于850℃的持续时间是否超过标准要求（单次≤1min、累计≤30min/天）。",
            legal_basis="GB 18485-2014；生态环境部令第10号（自动监测数据应用管理规定）",
            applicable_modes=["快速"],
            dimension=DIMENSION_INDUSTRY_SPECIFIC,
        ),
        EcoRule(
            id="R195",
            name="钢铁行业烧结烟气脱硫脱硝合规性",
            description="检查钢铁烧结机头烟气脱硫脱硝设施的运行状态，检测治理设施与烧结设施不同步运行的情况。",
            detection_logic="检查钢铁烧结机头烟气脱硫脱硝设施的运行状态，进出口SO₂、NOx浓度及去除效率，检测治理设施与烧结设施不同步运行的情况。",
            legal_basis="GB 28662-2012（钢铁烧结、球团工业大气污染物排放标准）",
            applicable_modes=["标准"],
            dimension=DIMENSION_INDUSTRY_SPECIFIC,
        ),
        EcoRule(
            id="R196",
            name="VOCs行业特征因子专项监测",
            description="针对VOCs重点行业，检查是否对特征污染物开展专项监测，监测因子是否覆盖排污许可要求。",
            detection_logic="针对化工、涂装、印刷等VOCs重点行业，检查是否对特征污染物（苯系物、醛类、酮类等）开展专项监测，监测因子是否覆盖排污许可要求。",
            legal_basis="GB 37822-2019（VOCs无组织排放标准）；HJ 1286-2023",
            applicable_modes=["标准"],
            dimension=DIMENSION_INDUSTRY_SPECIFIC,
        ),
        EcoRule(
            id="R197",
            name="重金属行业特征污染物监测",
            description="检查涉重金属行业是否按要求开展特征重金属因子的定期监测，监测频次和因子是否合规。",
            detection_logic="检查电镀、冶炼、电池等涉重金属行业是否按要求开展特征重金属因子（铅、镉、铬、砷、汞等）的定期监测，监测频次和因子是否合规。",
            legal_basis="GB 21900-2008（电镀污染物排放标准）；GB 25467-2010（铅锌工业）",
            applicable_modes=["标准"],
            dimension=DIMENSION_INDUSTRY_SPECIFIC,
        ),
        EcoRule(
            id="R198",
            name="污水处理特征因子监测",
            description="检查工业废水处理设施是否按排污许可要求开展特征因子监测，监测方法和频次是否合规。",
            detection_logic="检查工业废水处理设施是否按排污许可要求开展特征因子监测（总氰化物、石油类、总锌等），监测方法和频次是否合规。",
            legal_basis="GB 8978-1996（污水综合排放标准）；HJ 355-2019",
            applicable_modes=["标准"],
            dimension=DIMENSION_INDUSTRY_SPECIFIC,
        ),
        EcoRule(
            id="R199",
            name="锅炉烟气超低排放改造合规性",
            description="检查燃煤锅炉超低排放改造后，颗粒物、SO₂、NOx排放浓度是否满足超低排放限值。",
            detection_logic="检查燃煤锅炉超低排放改造后，颗粒物、SO₂、NOx排放浓度是否满足超低排放限值（10/35/50mg/m³），在线监测数据是否持续达标。",
            legal_basis="GB 13271-2014（锅炉大气污染物排放标准）；发改环资〔2015〕2221号",
            applicable_modes=["标准"],
            dimension=DIMENSION_INDUSTRY_SPECIFIC,
        ),
        EcoRule(
            id="R200",
            name="焦化行业苯系物/酚类/氰化物专项监测",
            description="检查焦化企业废水和废气中特征污染物的监测是否按排污许可要求开展。",
            detection_logic="检查焦化企业废水和废气中特征污染物（苯系物、酚类、氰化物、氨等）的监测是否按排污许可要求开展，监测点位、频次、方法是否合规。",
            legal_basis="GB 16171-2012（炼焦化学工业污染物排放标准）；HJ 355-2019",
            applicable_modes=["标准"],
            dimension=DIMENSION_INDUSTRY_SPECIFIC,
        ),
    ]
    rules.extend(_industry_rules)

    return rules


# ============================================================================
# 规则引擎
# ============================================================================


class RuleEngine:
    """
    ECO-Audit V3.0 规则引擎。

    管理全部 200 条审计规则的注册、查询和分类。
    支持按维度、按模式筛选规则，并提供统计信息。

    Usage:
        engine = RuleEngine()
        # 获取全部规则
        all_rules = engine.get_all_rules()
        # 按维度查询
        tech_rules = engine.get_rules_by_dimension("技术合规与反造假")
        # 按模式查询
        fast_rules = engine.get_rules_by_mode("快速")
        # 统计信息
        stats = engine.get_statistics()
    """

    def __init__(self):
        """初始化规则引擎，加载全部 200 条规则。"""
        self._rules: List[EcoRule] = _build_all_rules()
        self._rule_index: dict[str, EcoRule] = {r.id: r for r in self._rules}

    def get_all_rules(self) -> List[EcoRule]:
        """
        获取全部审计规则。

        Returns:
            所有已注册且启用的 EcoRule 实例列表。
        """
        return [r for r in self._rules if r.enabled]

    def get_rule_by_id(self, rule_id: str) -> Optional[EcoRule]:
        """
        根据规则 ID 获取单条规则。

        Args:
            rule_id: 规则编号，如 "R001"。

        Returns:
            对应的 EcoRule 实例，未找到则返回 None。
        """
        return self._rule_index.get(rule_id)

    def get_rules_by_dimension(self, dimension: str) -> List[EcoRule]:
        """
        按维度分类获取规则。

        Args:
            dimension: 维度名称，必须是 ALL_DIMENSIONS 中的有效值。

        Returns:
            属于指定维度的所有已启用规则列表。

        Raises:
            ValueError: 如果维度名称无效。

        Example:
            >>> engine = RuleEngine()
            >>> rules = engine.get_rules_by_dimension("技术合规与反造假")
            >>> print(f"共 {len(rules)} 条反造假规则")
        """
        if dimension not in ALL_DIMENSIONS:
            raise ValueError(
                f"无效维度: '{dimension}'。"
                f"有效维度: {ALL_DIMENSIONS}"
            )
        return [
            r for r in self._rules
            if r.dimension == dimension and r.enabled
        ]

    def get_rules_by_mode(self, mode: str) -> List[EcoRule]:
        """
        按适用模式筛选规则。

        Args:
            mode: 审计模式，如 "快速"、"标准"、"完整"。

        Returns:
            适用于指定模式的所有已启用规则列表。

        Raises:
            ValueError: 如果模式名称无效。

        Example:
            >>> engine = RuleEngine()
            >>> fast_rules = engine.get_rules_by_mode("快速")
            >>> print(f"快速模式适用 {len(fast_rules)} 条规则")
        """
        if mode not in ALL_MODES:
            raise ValueError(
                f"无效模式: '{mode}'。"
                f"有效模式: {ALL_MODES}"
            )
        return [
            r for r in self._rules
            if mode in r.applicable_modes and r.enabled
        ]

    def get_rules_by_ids(self, rule_ids: List[str]) -> List[EcoRule]:
        """
        批量根据规则 ID 获取规则。

        Args:
            rule_ids: 规则编号列表，如 ["R001", "R003", "R051"]。

        Returns:
            匹配到的规则列表（按传入顺序），忽略不存在的 ID。
        """
        return [
            self._rule_index[rid]
            for rid in rule_ids
            if rid in self._rule_index
        ]

    def get_statistics(self) -> dict:
        """
        获取规则统计信息。

        Returns:
            包含以下键的字典:
                - total_rules: 总规则数
                - enabled_rules: 已启用规则数
                - disabled_rules: 已禁用规则数
                - by_dimension: 各维度规则数 {维度名: 数量}
                - by_mode: 各模式覆盖规则数 {模式名: 数量}
                - rule_id_range: 规则ID范围 (min_id, max_id)

        Example:
            >>> engine = RuleEngine()
            >>> stats = engine.get_statistics()
            >>> print(f"总规则数: {stats['total_rules']}")
            >>> for dim, count in stats['by_dimension'].items():
            ...     print(f"  {dim}: {count}条")
        """
        enabled_rules = [r for r in self._rules if r.enabled]
        disabled_rules = [r for r in self._rules if not r.enabled]

        by_dimension = {}
        for dim in ALL_DIMENSIONS:
            by_dimension[dim] = sum(1 for r in enabled_rules if r.dimension == dim)

        by_mode = {}
        for mode in ALL_MODES:
            by_mode[mode] = sum(
                1 for r in enabled_rules if mode in r.applicable_modes
            )

        all_ids = [r.id for r in self._rules]
        id_range = (min(all_ids), max(all_ids)) if all_ids else ("", "")

        return {
            "total_rules": len(self._rules),
            "enabled_rules": len(enabled_rules),
            "disabled_rules": len(disabled_rules),
            "by_dimension": by_dimension,
            "by_mode": by_mode,
            "rule_id_range": id_range,
        }

    def enable_rule(self, rule_id: str) -> bool:
        """
        启用指定规则。

        Args:
            rule_id: 规则编号。

        Returns:
            操作是否成功（规则是否存在）。
        """
        rule = self._rule_index.get(rule_id)
        if rule:
            rule.enabled = True
            return True
        return False

    def disable_rule(self, rule_id: str) -> bool:
        """
        禁用指定规则。

        Args:
            rule_id: 规则编号。

        Returns:
            操作是否成功（规则是否存在）。
        """
        rule = self._rule_index.get(rule_id)
        if rule:
            rule.enabled = False
            return True
        return False

    def get_enabled_rule_ids(self) -> List[str]:
        """
        获取所有已启用规则的 ID 列表。

        Returns:
            已启用规则的 ID 列表，按规则 ID 排序。
        """
        return sorted(r.id for r in self._rules if r.enabled)


# ============================================================================
# 便捷函数（向后兼容）
# ============================================================================


def get_all_rules() -> List[EcoRule]:
    """
    获取全部审计规则（便捷函数）。

    Returns:
        所有 EcoRule 实例列表。
    """
    return _build_all_rules()


def get_rules_by_dimension(dimension: str) -> List[EcoRule]:
    """
    按维度获取规则（便捷函数）。

    Args:
        dimension: 维度名称。

    Returns:
        属于指定维度的规则列表。
    """
    return [r for r in _build_all_rules() if r.dimension == dimension]


def get_rules_by_mode(mode: str) -> List[EcoRule]:
    """
    按模式获取规则（便捷函数）。

    Args:
        mode: 审计模式。

    Returns:
        适用于指定模式的规则列表。
    """
    return [r for r in _build_all_rules() if mode in r.applicable_modes]


def get_rule_count() -> int:
    """
    获取规则总数。

    Returns:
        当前已定义的规则总数。
    """
    return len(_build_all_rules())


def get_statistics() -> dict:
    """
    获取规则统计信息（便捷函数）。

    Returns:
        包含 total_rules, enabled_rules, disabled_rules, by_dimension, by_mode, rule_id_range 的字典。
    """
    return RuleEngine().get_statistics()
