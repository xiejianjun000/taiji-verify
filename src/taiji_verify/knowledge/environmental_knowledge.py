"""
生态环境领域知识库

完整覆盖：
- 大气污染与防治
- 水污染与防治
- 固体废物与土壤污染
- 噪声污染
- 辐射污染
- 生态保护与修复
- 环境影响评价
- 碳排放与气候变化
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class EnvKnowledgeEntry:
    """环境知识条目"""
    id: str
    content: str
    subcategory: str
    source: str
    keywords: list[str] = field(default_factory=list)
    standard_code: Optional[str] = None
    year: Optional[int] = None


# 扩展子类别常量
SUBCATEGORY_PERMIT = "permit"           # 排污许可
SUBCATEGORY_MONITORING = "monitoring"    # 环境监测
SUBCATEGORY_EMERGENCY = "emergency"     # 环境应急
SUBCATEGORY_CLEAN_PRODUCTION = "clean_production"  # 清洁生产
SUBCATEGORY_VEHICLE = "vehicle"         # 机动车尾气
SUBCATEGORY_WASTEFREE = "wastefree"     # 无废城市
SUBCATEGORY_SOIL_REMEDIATION = "soil_remediation"  # 土壤修复


class EnvironmentalKnowledgeBase:
    """
    生态环境知识库

    Usage:
        kb = EnvironmentalKnowledgeBase()
        kb.load_all()

        results = kb.query("PM2.5", subcategory="air")
        results = kb.query("水质标准", subcategory="water")
    """

    def __init__(self):
        self._entries: dict[str, list[EnvKnowledgeEntry]] = {
            "air": [],              # 大气污染
            "water": [],            # 水污染
            "soil": [],             # 土壤污染
            "solid_waste": [],      # 固体废物
            "noise": [],            # 噪声污染
            "radiation": [],        # 辐射污染
            "ecology": [],          # 生态保护
            "eia": [],              # 环境影响评价
            "carbon": [],           # 碳排放
            "permit": [],           # 排污许可
            "monitoring": [],       # 环境监测
            "emergency": [],        # 环境应急
            "clean_production": [], # 清洁生产
            "vehicle": [],          # 机动车尾气
            "wastefree": [],        # 无废城市
            "soil_remediation": [], # 土壤修复
        }

    def load_all(self) -> EnvironmentalKnowledgeBase:
        """加载所有环境知识"""
        self.load_air_pollution()
        self.load_water_pollution()
        self.load_soil_pollution()
        self.load_solid_waste()
        self.load_noise_pollution()
        self.load_radiation_pollution()
        self.load_ecology_protection()
        self.load_eia()
        self.load_carbon_emission()
        self.load_permit_knowledge()
        self.load_monitoring_knowledge()
        self.load_emergency_knowledge()
        self.load_clean_production()
        self.load_vehicle_emission()
        self.load_wastefree_city()
        self.load_soil_remediation()
        return self

    def load_air_pollution(self) -> EnvironmentalKnowledgeBase:
        """加载大气污染知识"""
        self._entries["air"] = [
            EnvKnowledgeEntry(
                id="AIR001",
                content="PM2.5是指空气动力学直径小于或等于2.5微米的颗粒物，是衡量空气质量的重要指标",
                subcategory="air",
                source="GB 3095-2012 环境空气质量标准",
                keywords=["PM2.5", "细颗粒物", "空气质量"],
                standard_code="GB 3095",
                year=2012,
            ),
            EnvKnowledgeEntry(
                id="AIR002",
                content="PM10是指空气动力学直径小于或等于10微米的颗粒物",
                subcategory="air",
                source="GB 3095-2012 环境空气质量标准",
                keywords=["PM10", "可吸入颗粒物"],
                standard_code="GB 3095",
                year=2012,
            ),
            EnvKnowledgeEntry(
                id="AIR003",
                content="SO2二氧化硫是主要的大气污染物之一，主要来源于燃煤排放",
                subcategory="air",
                source="GB 21902-2008",
                keywords=["SO2", "二氧化硫", "燃煤"],
                standard_code="GB 21902",
                year=2008,
            ),
            EnvKnowledgeEntry(
                id="AIR004",
                content="NOx氮氧化物包括一氧化氮和二氧化氮，主要来源于机动车尾气和工业排放",
                subcategory="air",
                source="GB 16297-1996",
                keywords=["NOx", "氮氧化物", "机动车", "尾气"],
                standard_code="GB 16297",
                year=1996,
            ),
            EnvKnowledgeEntry(
                id="AIR005",
                content="O3臭氧是二次污染物，高浓度臭氧对人体健康有害",
                subcategory="air",
                source="GB 3095-2012",
                keywords=["O3", "臭氧", "光化学烟雾"],
                standard_code="GB 3095",
                year=2012,
            ),
            EnvKnowledgeEntry(
                id="AIR006",
                content="CO一氧化碳是一种有毒气体，主要来源于不完全燃烧",
                subcategory="air",
                source="GB 3095-2012",
                keywords=["CO", "一氧化碳", "不完全燃烧"],
                standard_code="GB 3095",
                year=2012,
            ),
            EnvKnowledgeEntry(
                id="AIR007",
                content="Pb铅及其化合物是大气重金属污染物，对人体神经系统有害",
                subcategory="air",
                source="GB 3095-2012",
                keywords=["Pb", "铅", "重金属"],
                standard_code="GB 3095",
                year=2012,
            ),
            EnvKnowledgeEntry(
                id="AIR008",
                content="环境空气质量功能区分为一类区和二类区，一类区为自然保护区等，二类区为居住区等",
                subcategory="air",
                source="GB 3095-2012",
                keywords=["功能区", "一类区", "二类区", "自然保护区"],
                standard_code="GB 3095",
                year=2012,
            ),
            EnvKnowledgeEntry(
                id="AIR009",
                content="大气污染综合排放标准规定了33种大气污染物的排放限值",
                subcategory="air",
                source="GB 16297-1996 大气污染物综合排放标准",
                keywords=["综合排放标准", "排放限值", "污染物"],
                standard_code="GB 16297",
                year=1996,
            ),
            EnvKnowledgeEntry(
                id="AIR010",
                content="工业炉窑大气污染物排放需满足GB 9078-1996要求",
                subcategory="air",
                source="GB 9078-1996",
                keywords=["工业炉窑", "排放标准", "炉窑"],
                standard_code="GB 9078",
                year=1996,
            ),
            EnvKnowledgeEntry(
                id="AIR011",
                content="锅炉大气污染物排放需满足GB 13271-2014要求",
                subcategory="air",
                source="GB 13271-2014 锅炉大气污染物排放标准",
                keywords=["锅炉", "大气污染", "排放标准"],
                standard_code="GB 13271",
                year=2014,
            ),
            EnvKnowledgeEntry(
                id="AIR012",
                content="挥发性有机物VOCs是臭氧和PM2.5的重要前体物",
                subcategory="air",
                source="HJ 604-2017",
                keywords=["VOCs", "挥发性有机物", "臭氧前体"],
                standard_code="HJ 604",
                year=2017,
            ),
            EnvKnowledgeEntry(
                id="AIR013",
                content="氨NH3是大气中重要的碱性气体，参与二次气溶胶生成",
                subcategory="air",
                source="HJ 194-2005",
                keywords=["NH3", "氨", "气溶胶"],
                standard_code="HJ 194",
                year=2005,
            ),
            EnvKnowledgeEntry(
                id="AIR014",
                content="酸雨是指pH值小于5.6的降水，主要由SO2和NOx排放造成",
                subcategory="air",
                source="环境科学常识",
                keywords=["酸雨", "pH值", "硫氧化物"],
            ),
            EnvKnowledgeEntry(
                id="AIR015",
                content="雾霾是雾和霾的组合，能见度低于10公里",
                subcategory="air",
                source="环境科学常识",
                keywords=["雾霾", "能见度", "颗粒物"],
            ),
        ]
        return self

    def load_water_pollution(self) -> EnvironmentalKnowledgeBase:
        """加载水污染知识"""
        self._entries["water"] = [
            EnvKnowledgeEntry(
                id="WAT001",
                content="地表水环境质量标准GB 3838-2002将水体分为Ⅰ-Ⅴ类",
                subcategory="water",
                source="GB 3838-2002 地表水环境质量标准",
                keywords=["地表水", "水质标准", "Ⅰ类", "Ⅱ类", "Ⅲ类", "Ⅳ类", "Ⅴ类"],
                standard_code="GB 3838",
                year=2002,
            ),
            EnvKnowledgeEntry(
                id="WAT002",
                content="COD化学需氧量是衡量水体有机污染程度的重要指标",
                subcategory="water",
                source="HJ 828-2017",
                keywords=["COD", "化学需氧量", "有机污染"],
                standard_code="HJ 828",
                year=2017,
            ),
            EnvKnowledgeEntry(
                id="WAT003",
                content="BOD5生化需氧量是反映水体可生化降解有机物含量的指标",
                subcategory="water",
                source="HJ 505-2009",
                keywords=["BOD", "生化需氧量", "有机物"],
                standard_code="HJ 505",
                year=2009,
            ),
            EnvKnowledgeEntry(
                id="WAT004",
                content="氨氮NH3-N是水体富营养化的主要指标之一",
                subcategory="water",
                source="HJ 535-2009",
                keywords=["氨氮", "NH3-N", "富营养化"],
                standard_code="HJ 535",
                year=2009,
            ),
            EnvKnowledgeEntry(
                id="WAT005",
                content="总磷TP是水体富营养化的限制性因子",
                subcategory="water",
                source="GB 11894-89",
                keywords=["总磷", "TP", "富营养化"],
                standard_code="GB 11894",
                year=1989,
            ),
            EnvKnowledgeEntry(
                id="WAT006",
                content="总氮TN是水体富营养化的重要指标",
                subcategory="water",
                source="HJ 636-2012",
                keywords=["总氮", "TN", "富营养化"],
                standard_code="HJ 636",
                year=2012,
            ),
            EnvKnowledgeEntry(
                id="WAT007",
                content="pH值反映水体的酸碱性，饮用水的pH值应在6.5-8.5之间",
                subcategory="water",
                source="GB 5749-2022",
                keywords=["pH值", "酸碱性", "饮用水"],
                standard_code="GB 5749",
                year=2022,
            ),
            EnvKnowledgeEntry(
                id="WAT008",
                content="溶解氧DO是水体自净能力的重要指标",
                subcategory="water",
                source="GB 3838-2002",
                keywords=["溶解氧", "DO", "自净"],
                standard_code="GB 3838",
                year=2002,
            ),
            EnvKnowledgeEntry(
                id="WAT009",
                content="重金属污染物包括汞、镉、铅、铬等，对人体有毒害作用",
                subcategory="water",
                source="GB 11607-89",
                keywords=["重金属", "汞", "镉", "铅", "铬"],
                standard_code="GB 11607",
                year=1989,
            ),
            EnvKnowledgeEntry(
                id="WAT010",
                content="石油类是水体油类污染物的总称",
                subcategory="water",
                source="HJ 970-2018",
                keywords=["石油类", "油类污染物"],
                standard_code="HJ 970",
                year=2018,
            ),
            EnvKnowledgeEntry(
                id="WAT011",
                content="阴离子表面活性剂是生活污水的重要指标",
                subcategory="water",
                source="GB 7494-87",
                keywords=["表面活性剂", "LAS", "阴离子"],
                standard_code="GB 7494",
                year=1987,
            ),
            EnvKnowledgeEntry(
                id="WAT012",
                content="水污染物综合排放标准GB 8978-1996规定了68种水污染物的排放限值",
                subcategory="water",
                source="GB 8978-1996 污水综合排放标准",
                keywords=["综合排放标准", "污水", "排放限值"],
                standard_code="GB 8978",
                year=1996,
            ),
            EnvKnowledgeEntry(
                id="WAT013",
                content="城镇污水处理厂污染物排放标准GB 18918-2002",
                subcategory="water",
                source="GB 18918-2002",
                keywords=["污水处理厂", "一级A", "一级B"],
                standard_code="GB 18918",
                year=2002,
            ),
            EnvKnowledgeEntry(
                id="WAT014",
                content="黑臭水体是指城市建成区内呈现令人不悦的颜色和散发令人不适气味的水体",
                subcategory="water",
                source="黑臭水体整治工作指南",
                keywords=["黑臭水体", "城市黑臭"],
            ),
            EnvKnowledgeEntry(
                id="WAT015",
                content="饮用水水源地应符合GB 3838-2002中Ⅲ类及以上水域标准",
                subcategory="water",
                source="GB 3838-2002",
                keywords=["水源地", "饮用水源", "Ⅲ类"],
                standard_code="GB 3838",
                year=2002,
            ),
        ]
        return self

    def load_soil_pollution(self) -> EnvironmentalKnowledgeBase:
        """加载土壤污染知识"""
        self._entries["soil"] = [
            EnvKnowledgeEntry(
                id="SOI001",
                content="土壤环境质量标准GB 15618-2018规定了土壤污染风险管控值",
                subcategory="soil",
                source="GB 15618-2018",
                keywords=["土壤环境质量", "风险管控值", "GB15618"],
                standard_code="GB 15618",
                year=2018,
            ),
            EnvKnowledgeEntry(
                id="SOI002",
                content="土壤重金属污染包括镉、汞、砷、铅、铬等",
                subcategory="soil",
                source="土壤污染防治法",
                keywords=["重金属", "镉", "汞", "砷", "铅", "铬"],
            ),
            EnvKnowledgeEntry(
                id="SOI003",
                content="土壤pH值影响重金属的活性和迁移能力",
                subcategory="soil",
                source="土壤学基础",
                keywords=["土壤pH", "重金属活性"],
            ),
            EnvKnowledgeEntry(
                id="SOI004",
                content="有机污染物包括多环芳烃PAHs、多氯联苯PCBs等",
                subcategory="soil",
                source="土壤污染防治法",
                keywords=["有机污染物", "PAHs", "PCBs"],
            ),
            EnvKnowledgeEntry(
                id="SOI005",
                content="农用地土壤污染风险管控标准GB 15618-2018分为风险筛选值和风险管制值",
                subcategory="soil",
                source="GB 15618-2018",
                keywords=["农用地", "风险筛选值", "风险管制值"],
                standard_code="GB 15618",
                year=2018,
            ),
        ]
        return self

    def load_solid_waste(self) -> EnvironmentalKnowledgeBase:
        """加载固体废物知识"""
        self._entries["solid_waste"] = [
            EnvKnowledgeEntry(
                id="SOL001",
                content="固体废物分为一般工业固废、危险废物和生活垃圾",
                subcategory="solid_waste",
                source="固体废物污染环境防治法",
                keywords=["一般固废", "危险废物", "生活垃圾", "固废分类"],
            ),
            EnvKnowledgeEntry(
                id="SOL002",
                content="危险废物是指列入国家危险废物名录或具有危险特性的废物",
                subcategory="solid_waste",
                source="国家危险废物名录",
                keywords=["危险废物", "HW01-HW49", "名录"],
            ),
            EnvKnowledgeEntry(
                id="SOL003",
                content="危险废物转移须填写危险废物转移联单",
                subcategory="solid_waste",
                source="固废法",
                keywords=["转移联单", "五联单", "危废转移"],
            ),
            EnvKnowledgeEntry(
                id="SOL004",
                content="危险废物贮存须符合GB 18597-2023要求",
                subcategory="solid_waste",
                source="GB 18597-2023",
                keywords=["危废贮存", "贮存设施", "标准"],
                standard_code="GB 18597",
                year=2023,
            ),
            EnvKnowledgeEntry(
                id="SOL005",
                content="危险废物处置须由具备资质的单位进行",
                subcategory="solid_waste",
                source="固废法",
                keywords=["危废处置", "处置资质", "经营许可"],
            ),
            EnvKnowledgeEntry(
                id="SOL006",
                content="一般工业固体废物贮存、处置场污染控制标准GB 18599-2020",
                subcategory="solid_waste",
                source="GB 18599-2020",
                keywords=["一般固废", "贮存场", "处置场"],
                standard_code="GB 18599",
                year=2020,
            ),
            EnvKnowledgeEntry(
                id="SOL007",
                content="生活垃圾分为可回收物、有害垃圾、厨余垃圾和其他垃圾",
                subcategory="solid_waste",
                source="城市生活垃圾分类",
                keywords=["生活垃圾分类", "可回收", "厨余", "有害"],
            ),
            EnvKnowledgeEntry(
                id="SOL008",
                content="医疗废物属于危险废物，须专门收集处置",
                subcategory="solid_waste",
                source="医疗废物管理条例",
                keywords=["医疗废物", "医疗垃圾", "HW01"],
            ),
            EnvKnowledgeEntry(
                id="SOL009",
                content="建筑垃圾应分类收集、综合利用或无害化处置",
                subcategory="solid_waste",
                source="建筑垃圾处理技术规范",
                keywords=["建筑垃圾", "装修垃圾", "拆除垃圾"],
            ),
            EnvKnowledgeEntry(
                id="SOL010",
                content="废旧电子产品属于危险废物，需专门回收处理",
                subcategory="solid_waste",
                source="电器电子产品有害物质限制使用管理办法",
                keywords=["电子废物", "废旧电器", "WEEE"],
            ),
        ]
        return self

    def load_noise_pollution(self) -> EnvironmentalKnowledgeBase:
        """加载噪声污染知识"""
        self._entries["noise"] = [
            EnvKnowledgeEntry(
                id="NOI001",
                content="声环境质量标准GB 3096-2008规定了各类声环境功能区的噪声限值",
                subcategory="noise",
                source="GB 3096-2008",
                keywords=["声环境质量", "昼间", "夜间", "分贝"],
                standard_code="GB 3096",
                year=2008,
            ),
            EnvKnowledgeEntry(
                id="NOI002",
                content="0类声环境功能区指康复疗养区等特别需要安静的区域，昼间不超过50dB",
                subcategory="noise",
                source="GB 3096-2008",
                keywords=["0类区", "康复疗养区", "50dB"],
                standard_code="GB 3096",
                year=2008,
            ),
            EnvKnowledgeEntry(
                id="NOI003",
                content="1类声环境功能区指以居住为主的区域，昼间不超过55dB，夜间不超过45dB",
                subcategory="noise",
                source="GB 3096-2008",
                keywords=["1类区", "居住区", "55dB", "45dB"],
                standard_code="GB 3096",
                year=2008,
            ),
            EnvKnowledgeEntry(
                id="NOI004",
                content="2类声环境功能区指商业、居住、工业混杂区，昼间不超过60dB，夜间不超过50dB",
                subcategory="noise",
                source="GB 3096-2008",
                keywords=["2类区", "混杂区", "60dB", "50dB"],
                standard_code="GB 3096",
                year=2008,
            ),
            EnvKnowledgeEntry(
                id="NOI005",
                content="3类声环境功能区指工业区，昼间不超过65dB，夜间不超过55dB",
                subcategory="noise",
                source="GB 3096-2008",
                keywords=["3类区", "工业区", "65dB", "55dB"],
                standard_code="GB 3096",
                year=2008,
            ),
            EnvKnowledgeEntry(
                id="NOI006",
                content="4类声环境功能区指交通干线两侧区域",
                subcategory="noise",
                source="GB 3096-2008",
                keywords=["4类区", "交通干线", "铁路", "高速公路"],
                standard_code="GB 3096",
                year=2008,
            ),
            EnvKnowledgeEntry(
                id="NOI007",
                content="工业企业厂界环境噪声排放标准GB 12348-2008",
                subcategory="noise",
                source="GB 12348-2008",
                keywords=["厂界噪声", "工业企业", "排放标准"],
                standard_code="GB 12348",
                year=2008,
            ),
            EnvKnowledgeEntry(
                id="NOI008",
                content="建筑施工场界环境噪声排放标准GB 12523-2011",
                subcategory="noise",
                source="GB 12523-2011",
                keywords=["施工噪声", "建筑施工", "昼间", "夜间"],
                standard_code="GB 12523",
                year=2011,
            ),
        ]
        return self

    def load_radiation_pollution(self) -> EnvironmentalKnowledgeBase:
        """加载辐射污染知识"""
        self._entries["radiation"] = [
            EnvKnowledgeEntry(
                id="RAD001",
                content="电离辐射包括α、β、γ射线和中子等",
                subcategory="radiation",
                source="辐射防护规定",
                keywords=["电离辐射", "α射线", "β射线", "γ射线"],
            ),
            EnvKnowledgeEntry(
                id="RAD002",
                content="公众年有效剂量限值为1mSv",
                subcategory="radiation",
                source="GB 18871-2002",
                keywords=["剂量限值", "1mSv", "有效剂量"],
                standard_code="GB 18871",
                year=2002,
            ),
            EnvKnowledgeEntry(
                id="RAD003",
                content="电磁辐射污染包括工频电磁场和射频电磁场",
                subcategory="radiation",
                source="电磁辐射防护规定",
                keywords=["电磁辐射", "工频", "射频", "电场强度"],
            ),
            EnvKnowledgeEntry(
                id="RAD004",
                content="移动通信基站电磁辐射应满足GB 8702-2014要求",
                subcategory="radiation",
                source="GB 8702-2014",
                keywords=["基站辐射", "移动通信", "电磁环境"],
                standard_code="GB 8702",
                year=2014,
            ),
            EnvKnowledgeEntry(
                id="RAD005",
                content="放射性同位素与射线装置分类由国务院生态环境主管部门规定",
                subcategory="radiation",
                source="放射性同位素与射线装置安全和防护条例",
                keywords=["放射源", "射线装置", "Ⅰ类", "Ⅱ类", "Ⅲ类"],
            ),
        ]
        return self

    def load_ecology_protection(self) -> EnvironmentalKnowledgeBase:
        """加载生态保护知识"""
        self._entries["ecology"] = [
            EnvKnowledgeEntry(
                id="ECO001",
                content="生态保护红线是指具有重要生态功能的区域，实行严格保护",
                subcategory="ecology",
                source="生态保护红线划定指南",
                keywords=["生态保护红线", "红线", "严格保护"],
            ),
            EnvKnowledgeEntry(
                id="ECO002",
                content="自然保护区分为核心区、缓冲区和实验区",
                subcategory="ecology",
                source="自然保护区条例",
                keywords=["自然保护区", "核心区", "缓冲区", "实验区"],
            ),
            EnvKnowledgeEntry(
                id="ECO003",
                content="生物多样性包括遗传多样性、物种多样性和生态系统多样性",
                subcategory="ecology",
                source="生物多样性保护",
                keywords=["生物多样性", "遗传多样性", "物种多样性"],
            ),
            EnvKnowledgeEntry(
                id="ECO004",
                content="外来入侵物种会对本地生态系统造成危害",
                subcategory="ecology",
                source="外来入侵物种名录",
                keywords=["外来入侵物种", "入侵物种", "生物入侵"],
            ),
            EnvKnowledgeEntry(
                id="ECO005",
                content="湿地具有调节气候、涵养水源、保护生物多样性等功能",
                subcategory="ecology",
                source="湿地保护法",
                keywords=["湿地", "红树林", "沼泽", "生物多样性"],
            ),
            EnvKnowledgeEntry(
                id="ECO006",
                content="森林生态系统具有固碳、涵养水源、保持水土等生态功能",
                subcategory="ecology",
                source="森林法",
                keywords=["森林", "生态系统", "固碳", "涵养水源"],
            ),
            EnvKnowledgeEntry(
                id="ECO007",
                content="生态修复是指对受损生态系统进行人工或辅助恢复",
                subcategory="ecology",
                source="生态修复技术规范",
                keywords=["生态修复", "生态恢复", "矿山修复"],
            ),
            EnvKnowledgeEntry(
                id="ECO008",
                content="生态影响评价需识别重要生态敏感区，包括自然保护区等",
                subcategory="ecology",
                source="生态影响评价技术导则",
                keywords=["生态敏感区", "生态影响评价", "自然保护区"],
            ),
            EnvKnowledgeEntry(
                id="ECO009",
                content="水土流失治理包括梯田、淤地坝、植被恢复等措施",
                subcategory="ecology",
                source="水土保持法",
                keywords=["水土流失", "梯田", "淤地坝", "水土保持"],
            ),
            EnvKnowledgeEntry(
                id="ECO010",
                content="物种保护等级分为国家一级保护、国家二级保护和省重点保护",
                subcategory="ecology",
                source="野生动物保护法",
                keywords=["保护动物", "一级保护", "二级保护", "物种"],
            ),
        ]
        return self

    def load_eia(self) -> EnvironmentalKnowledgeBase:
        """加载环境影响评价知识"""
        self._entries["eia"] = [
            EnvKnowledgeEntry(
                id="EIA001",
                content="环境影响评价分为报告书、报告表和登记表三类",
                subcategory="eia",
                source="环境影响评价法",
                keywords=["环评", "报告书", "报告表", "登记表"],
            ),
            EnvKnowledgeEntry(
                id="EIA002",
                content="建设项目环境影响评价分类管理名录由生态环境部制定发布",
                subcategory="eia",
                source="建设项目环境影响评价分类管理名录",
                keywords=["分类管理名录", "环评类别", "行业分类"],
            ),
            EnvKnowledgeEntry(
                id="EIA003",
                content="大气环境影响预测采用AERMOD或CALPUFF模型",
                subcategory="eia",
                source="环境影响评价技术导则 大气环境",
                keywords=["大气预测模型", "AERMOD", "CALPUFF"],
            ),
            EnvKnowledgeEntry(
                id="EIA004",
                content="地表水环境影响预测采用数学模型法或类比分析法",
                subcategory="eia",
                source="环境影响评价技术导则 地表水环境",
                keywords=["地表水预测", "数学模型", "水质预测"],
            ),
            EnvKnowledgeEntry(
                id="EIA005",
                content="声环境影响预测采用导则推荐模型计算",
                subcategory="eia",
                source="环境影响评价技术导则 声环境",
                keywords=["声环境预测", "噪声预测", "衰减计算"],
            ),
            EnvKnowledgeEntry(
                id="EIA006",
                content="环境风险评价需识别危险物质、预测事故情景、提出防范措施",
                subcategory="eia",
                source="建设项目环境风险评价技术导则",
                keywords=["环境风险评价", "风险分析", "应急预案"],
            ),
            EnvKnowledgeEntry(
                id="EIA007",
                content="环境影响报告书须包括工程分析、环境现状调查、影响预测、环保措施等内容",
                subcategory="eia",
                source="环评技术要求",
                keywords=["报告书章节", "工程分析", "现状调查", "影响预测"],
            ),
            EnvKnowledgeEntry(
                id="EIA008",
                content="清洁生产是指不断采取改进设计、使用清洁能源等措施",
                subcategory="eia",
                source="清洁生产促进法",
                keywords=["清洁生产", "清洁能源", "节能减排"],
            ),
            EnvKnowledgeEntry(
                id="EIA009",
                content="环保投资应明确投资估算和资金来源",
                subcategory="eia",
                source="环评文件编制要求",
                keywords=["环保投资", "投资估算", "资金来源"],
            ),
            EnvKnowledgeEntry(
                id="EIA010",
                content="三同时制度是指建设项目环保设施须与主体工程同时设计、同时施工、同时投产使用",
                subcategory="eia",
                source="环境保护法",
                keywords=["三同时", "环保设施", "投产"],
            ),
        ]
        return self

    def load_carbon_emission(self) -> EnvironmentalKnowledgeBase:
        """加载碳排放知识"""
        self._entries["carbon"] = [
            EnvKnowledgeEntry(
                id="CAR001",
                content="碳达峰是指某个地区或行业的二氧化碳排放达到峰值后不再增长",
                subcategory="carbon",
                source="碳达峰碳中和政策",
                keywords=["碳达峰", "碳排放峰值"],
            ),
            EnvKnowledgeEntry(
                id="CAR002",
                content="碳中和是指通过节能减排和碳抵消实现二氧化碳净零排放",
                subcategory="carbon",
                source="碳达峰碳中和政策",
                keywords=["碳中和", "净零排放", "碳抵消"],
            ),
            EnvKnowledgeEntry(
                id="CAR003",
                content="全国碳排放权交易市场的交易产品为碳排放配额",
                subcategory="carbon",
                source="碳排放权交易管理办法",
                keywords=["碳市场", "碳排放权", "碳配额", "CEA"],
            ),
            EnvKnowledgeEntry(
                id="CAR004",
                content="温室气体包括二氧化碳CH4、甲烷N2O、氢氟烃HFCs等",
                subcategory="carbon",
                source="温室气体排放核算指南",
                keywords=["温室气体", "GHG", "二氧化碳", "甲烷"],
            ),
            EnvKnowledgeEntry(
                id="CAR005",
                content="碳排放核算边界分为范围1、范围2和范围3排放",
                subcategory="carbon",
                source="ISO 14064",
                keywords=["范围1", "范围2", "范围3", "碳核算"],
            ),
            EnvKnowledgeEntry(
                id="CAR006",
                content="碳足迹是指产品或服务全生命周期产生的温室气体排放量",
                subcategory="carbon",
                source="碳足迹标准",
                keywords=["碳足迹", "LCA", "生命周期评价"],
            ),
            EnvKnowledgeEntry(
                id="CAR007",
                content="CCER是中国核证自愿减排量，可用于碳市场抵消",
                subcategory="carbon",
                source="温室气体自愿减排交易管理暂行办法",
                keywords=["CCER", "核证减排量", "自愿减排"],
            ),
            EnvKnowledgeEntry(
                id="CAR008",
                content="碳汇是指通过植树造林、森林管理等方式吸收二氧化碳",
                subcategory="carbon",
                source="林业碳汇",
                keywords=["碳汇", "林业碳汇", "碳吸收"],
            ),
            EnvKnowledgeEntry(
                id="CAR009",
                content="绿色电力证书是可再生能源发电的电子凭证",
                subcategory="carbon",
                source="绿色电力证书认购",
                keywords=["绿证", "绿色电力", "可再生能源"],
            ),
            EnvKnowledgeEntry(
                id="CAR010",
                content="ESG指环境、社会和治理，是可持续发展的评价体系",
                subcategory="carbon",
                source="ESG披露要求",
                keywords=["ESG", "可持续发展", "社会责任"],
            ),
        ]
        return self

    def load_permit_knowledge(self) -> EnvironmentalKnowledgeBase:
        """加载排污许可知识"""
        self._entries["permit"] = [
            EnvKnowledgeEntry(
                id="PER001",
                content="排污许可分为重点管理、简化管理和登记管理三类",
                subcategory="permit",
                source="排污许可管理条例",
                keywords=["排污许可", "重点管理", "简化管理", "登记管理"],
            ),
            EnvKnowledgeEntry(
                id="PER002",
                content="排污许可证有效期为5年，延续换证需提前申请",
                subcategory="permit",
                source="排污许可管理办法",
                keywords=["排污许可证", "有效期", "延续", "换证"],
            ),
            EnvKnowledgeEntry(
                id="PER003",
                content="排污单位应当建立环境管理台账记录制度",
                subcategory="permit",
                source="排污许可管理办法",
                keywords=["环境管理台账", "台账记录", "排污台账"],
            ),
            EnvKnowledgeEntry(
                id="PER004",
                content="污染物排放口需设置规范化排放口和标志牌",
                subcategory="permit",
                source="排污口规范化整治技术要求",
                keywords=["排放口", "规范化", "标志牌"],
            ),
            EnvKnowledgeEntry(
                id="PER005",
                content="排污权是指排污单位经核定允许排放污染物的权利",
                subcategory="permit",
                source="排污权交易试点",
                keywords=["排污权", "排污权交易", "排污指标"],
            ),
            EnvKnowledgeEntry(
                id="PER006",
                content="主要排放口需安装自动监测设备并与生态环境部门联网",
                subcategory="permit",
                source="排污许可技术规范",
                keywords=["自动监测", "在线监测", "联网"],
            ),
            EnvKnowledgeEntry(
                id="PER007",
                content="排污许可执行报告应包括自行监测结果和合规判定",
                subcategory="permit",
                source="排污许可执行报告技术规范",
                keywords=["执行报告", "自行监测", "合规判定"],
            ),
            EnvKnowledgeEntry(
                id="PER008",
                content="总量控制指标包括化学需氧量、氨氮、二氧化硫、氮氧化物等",
                subcategory="permit",
                source="主要污染物总量减排核算办法",
                keywords=["总量控制", "COD", "氨氮", "SO2", "NOx"],
            ),
            EnvKnowledgeEntry(
                id="PER009",
                content="依法取得排污许可证的排污单位不得无证排污",
                subcategory="permit",
                source="环境保护法",
                keywords=["无证排污", "依法排污", "许可证"],
            ),
            EnvKnowledgeEntry(
                id="PER010",
                content="排污许可证正本应悬挂在主要办公场所",
                subcategory="permit",
                source="排污许可管理办法",
                keywords=["许可证正本", "悬挂", "办公场所"],
            ),
        ]
        return self

    def load_monitoring_knowledge(self) -> EnvironmentalKnowledgeBase:
        """加载环境监测知识"""
        self._entries["monitoring"] = [
            EnvKnowledgeEntry(
                id="MON001",
                content="环境空气质量监测点位分为城市点、区域点和背景点",
                subcategory="monitoring",
                source="环境空气质量监测点位布设技术规范",
                keywords=["监测点位", "城市点", "区域点"],
            ),
            EnvKnowledgeEntry(
                id="MON002",
                content="水质监测断面分为对照断面、控制断面和消减断面",
                subcategory="monitoring",
                source="地表水和污水监测技术规范",
                keywords=["水质监测断面", "对照断面", "控制断面"],
            ),
            EnvKnowledgeEntry(
                id="MON003",
                content="污染源监测包括排污单位自行监测和生态环境部门监督性监测",
                subcategory="monitoring",
                source="污染源监测管理办法",
                keywords=["污染源监测", "自行监测", "监督性监测"],
            ),
            EnvKnowledgeEntry(
                id="MON004",
                content="自动监测设备应定期进行比对监测和质控考核",
                subcategory="monitoring",
                source="自动监控管理办法",
                keywords=["比对监测", "质控考核", "自动监测"],
            ),
            EnvKnowledgeEntry(
                id="MON005",
                content="环境监测报告分为监测快报、监测月报和监测年报",
                subcategory="monitoring",
                source="环境监测管理办法",
                keywords=["监测报告", "监测快报", "月报", "年报"],
            ),
            EnvKnowledgeEntry(
                id="MON006",
                content="环境标准样品用于监测方法验证和质量控制",
                subcategory="monitoring",
                source="环境标准样品管理办法",
                keywords=["标准样品", "质控样", "标准物质"],
            ),
            EnvKnowledgeEntry(
                id="MON007",
                content="污染物排放连续监测系统CEMS用于火电等行业",
                subcategory="monitoring",
                source="固定污染源烟气排放连续监测技术规范",
                keywords=["CEMS", "连续监测", "烟气排放"],
                standard_code="HJ 75",
            ),
            EnvKnowledgeEntry(
                id="MON008",
                content="水质自动监测站可实现水质参数的连续自动监测",
                subcategory="monitoring",
                source="地表水自动监测技术规范",
                keywords=["水质自动站", "水质自动监测", "连续监测"],
            ),
            EnvKnowledgeEntry(
                id="MON009",
                content="土壤环境监测需采集表层土壤和剖面样品",
                subcategory="monitoring",
                source="土壤环境监测技术规范",
                keywords=["土壤监测", "土壤采样", "剖面样品"],
                standard_code="HJ/T 166",
            ),
            EnvKnowledgeEntry(
                id="MON010",
                content="环境监测数据应真实准确，禁止篡改伪造监测数据",
                subcategory="monitoring",
                source="环境监测数据弄虚作假行为判定及处理办法",
                keywords=["监测数据", "弄虚作假", "篡改", "伪造"],
            ),
        ]
        return self

    def load_emergency_knowledge(self) -> EnvironmentalKnowledgeBase:
        """加载环境应急知识"""
        self._entries["emergency"] = [
            EnvKnowledgeEntry(
                id="EME001",
                content="突发环境事件分为特别重大、重大、较大和一般四级",
                subcategory="emergency",
                source="国家突发环境事件应急预案",
                keywords=["突发环境事件", "分级", "重大事件"],
            ),
            EnvKnowledgeEntry(
                id="EME002",
                content="企业应编制突发环境事件应急预案并备案",
                subcategory="emergency",
                source="企业事业单位突发环境事件应急预案备案管理办法",
                keywords=["应急预案", "预案备案", "环境应急"],
            ),
            EnvKnowledgeEntry(
                id="EME003",
                content="突发环境事件应急响应包括信息报告、应急处置和信息公开",
                subcategory="emergency",
                source="突发环境事件应急管理办法",
                keywords=["应急响应", "信息报告", "应急处置"],
            ),
            EnvKnowledgeEntry(
                id="EME004",
                content="环境应急物资储备库应配备围油栏、吸附材料等应急物资",
                subcategory="emergency",
                source="环境应急物资分类及产品目录",
                keywords=["应急物资", "围油栏", "吸附材料"],
            ),
            EnvKnowledgeEntry(
                id="EME005",
                content="重点行业企业应开展环境风险评估并编制环境应急预案",
                subcategory="emergency",
                source="企业突发环境事件风险评估指南",
                keywords=["风险评估", "环境风险", "风险等级"],
            ),
            EnvKnowledgeEntry(
                id="EME006",
                content="突发水环境污染事件应采取截流、拦污、吸附等措施",
                subcategory="emergency",
                source="水污染事故处置技术规范",
                keywords=["水污染事故", "截流", "应急处置"],
            ),
            EnvKnowledgeEntry(
                id="EME007",
                content="突发大气环境污染事件应采取关闭阀门、喷淋降尘等措施",
                subcategory="emergency",
                source="大气污染事故应急处置技术规范",
                keywords=["大气污染事故", "应急处置", "喷淋"],
            ),
            EnvKnowledgeEntry(
                id="EME008",
                content="环境应急演练分为桌面演练和实战演练",
                subcategory="emergency",
                source="环境应急演练管理办法",
                keywords=["应急演练", "桌面演练", "实战演练"],
            ),
            EnvKnowledgeEntry(
                id="EME009",
                content="发生突发环境事件企业应立即报告并启动应急预案",
                subcategory="emergency",
                source="环境保护法",
                keywords=["事件报告", "立即报告", "信息报送"],
            ),
            EnvKnowledgeEntry(
                id="EME010",
                content="环境应急专家库为企业突发环境事件应对提供技术支撑",
                subcategory="emergency",
                source="环境应急专家库管理办法",
                keywords=["应急专家", "专家库", "技术支撑"],
            ),
        ]
        return self

    def load_clean_production(self) -> EnvironmentalKnowledgeBase:
        """加载清洁生产知识"""
        self._entries["clean_production"] = [
            EnvKnowledgeEntry(
                id="CLN001",
                content="清洁生产审核分为强制性审核和自愿性审核",
                subcategory="clean_production",
                source="清洁生产审核办法",
                keywords=["清洁生产审核", "强制审核", "自愿审核"],
            ),
            EnvKnowledgeEntry(
                id="CLN002",
                content="清洁生产审核程序包括筹划与组织、预审核、审核等阶段",
                subcategory="clean_production",
                source="清洁生产审核技术规范",
                keywords=["审核阶段", "预审核", "实施方案"],
                standard_code="HJ 469",
            ),
            EnvKnowledgeEntry(
                id="CLN003",
                content="清洁生产方案分为无费方案、低费方案、中费方案和高费方案",
                subcategory="clean_production",
                source="清洁生产审核指南",
                keywords=["清洁生产方案", "无费方案", "高费方案"],
            ),
            EnvKnowledgeEntry(
                id="CLN004",
                content="清洁生产指标分为定量指标和定性指标",
                subcategory="clean_production",
                source="清洁生产标准",
                keywords=["清洁生产指标", "定量指标", "定性指标"],
            ),
            EnvKnowledgeEntry(
                id="CLN005",
                content="清洁生产水平分为国际清洁生产领先水平、国内清洁生产先进水平等",
                subcategory="clean_production",
                source="清洁生产标准体系",
                keywords=["清洁生产水平", "国际领先", "国内先进"],
            ),
            EnvKnowledgeEntry(
                id="CLN006",
                content="重点行业清洁生产技术推行方案由工信部发布",
                subcategory="clean_production",
                source="工业清洁生产推行规划",
                keywords=["清洁生产技术", "技术推行", "行业方案"],
            ),
            EnvKnowledgeEntry(
                id="CLN007",
                content="清洁生产审核报告应包括企业基本情况、清洁生产审核过程等",
                subcategory="clean_production",
                source="清洁生产审核报告编制要求",
                keywords=["审核报告", "编制要求", "报告内容"],
            ),
            EnvKnowledgeEntry(
                id="CLN008",
                content="清洁生产绩效包括单位产品污染物产生量和排放量",
                subcategory="clean_production",
                source="清洁生产绩效评价指南",
                keywords=["清洁生产绩效", "污染物产生量", "排放强度"],
            ),
            EnvKnowledgeEntry(
                id="CLN009",
                content="物料衡算用于分析生产过程中物料输入输出平衡",
                subcategory="clean_production",
                source="清洁生产审核物料衡算方法",
                keywords=["物料衡算", "能量衡算", "平衡分析"],
            ),
            EnvKnowledgeEntry(
                id="CLN010",
                content="清洁生产验收需满足污染物排放标准和清洁生产指标要求",
                subcategory="clean_production",
                source="清洁生产审核验收指南",
                keywords=["验收指南", "清洁生产验收", "达标验收"],
            ),
        ]
        return self

    def load_vehicle_emission(self) -> EnvironmentalKnowledgeBase:
        """加载机动车尾气知识"""
        self._entries["vehicle"] = [
            EnvKnowledgeEntry(
                id="VEH001",
                content="机动车污染物排放标准分为国一到国六标准",
                subcategory="vehicle",
                source="轻型汽车污染物排放限值及测量方法",
                keywords=["国六标准", "国五标准", "排放标准"],
            ),
            EnvKnowledgeEntry(
                id="VEH002",
                content="重型柴油车污染物排放应满足GB 17691-2018要求",
                subcategory="vehicle",
                source="GB 17691-2018",
                keywords=["重型柴油车", "重型车标准", "NOx"],
                standard_code="GB 17691",
                year=2018,
            ),
            EnvKnowledgeEntry(
                id="VEH003",
                content="机动车环保信息公开是指企业公开污染物排放信息",
                subcategory="vehicle",
                source="机动车环保信息公开管理办法",
                keywords=["环保信息", "信息公开", "型式认证"],
            ),
            EnvKnowledgeEntry(
                id="VEH004",
                content="非道路移动机械包括挖掘机、装载机、叉车等",
                subcategory="vehicle",
                source="非道路移动机械排气污染防治技术政策",
                keywords=["非道路移动机械", "工程机械", "农用机械"],
            ),
            EnvKnowledgeEntry(
                id="VEH005",
                content="非道路移动机械排放标准分为一至四阶段",
                subcategory="vehicle",
                source="非道路移动机械用柴油机排放限值",
                keywords=["非道路标准", "三阶段", "四阶段"],
            ),
            EnvKnowledgeEntry(
                id="VEH006",
                content="在用机动车排放检验采用加载减速法或双怠速法",
                subcategory="vehicle",
                source="机动车排放定期检验规范",
                keywords=["排放检验", "加载减速", "双怠速"],
            ),
            EnvKnowledgeEntry(
                id="VEH007",
                content="OBD车载诊断系统用于监测机动车排放控制系统",
                subcategory="vehicle",
                source="车载诊断系统管理规范",
                keywords=["OBD", "车载诊断", "排放控制"],
            ),
            EnvKnowledgeEntry(
                id="VEH008",
                content="新能源车包括纯电动汽车、插电式混合动力汽车等",
                subcategory="vehicle",
                source="新能源汽车产业发展规划",
                keywords=["新能源汽车", "纯电动", "混合动力"],
            ),
            EnvKnowledgeEntry(
                id="VEH009",
                content="船舶大气污染物排放控制区包括硫氧化物和氮氧化物控制区",
                subcategory="vehicle",
                source="船舶大气污染物排放控制区实施方案",
                keywords=["船舶排放", "排放控制区", "ECA"],
            ),
            EnvKnowledgeEntry(
                id="VEH010",
                content="铁路内燃机车应符合GB 13486-2014排放要求",
                subcategory="vehicle",
                source="GB 13486-2014",
                keywords=["铁路机车", "内燃机车", "机车排放"],
                standard_code="GB 13486",
                year=2014,
            ),
        ]
        return self

    def load_wastefree_city(self) -> EnvironmentalKnowledgeBase:
        """加载无废城市知识"""
        self._entries["wastefree"] = [
            EnvKnowledgeEntry(
                id="WFL001",
                content="无废城市是指通过推动形成绿色发展方式实现固体废物源头减量",
                subcategory="wastefree",
                source="无废城市建设试点工作方案",
                keywords=["无废城市", "固体废物", "源头减量"],
            ),
            EnvKnowledgeEntry(
                id="WFL002",
                content="生活垃圾实行分类投放、分类收集、分类运输、分类处理",
                subcategory="wastefree",
                source="生活垃圾分类制度实施方案",
                keywords=["垃圾分类", "分类投放", "分类处理"],
            ),
            EnvKnowledgeEntry(
                id="WFL003",
                content="建筑垃圾资源化利用率是考核无废城市建设的重要指标",
                subcategory="wastefree",
                source="无废城市建设指标体系",
                keywords=["建筑垃圾", "资源化利用", "利用率"],
            ),
            EnvKnowledgeEntry(
                id="WFL004",
                content="危险废物集中处置设施是危险废物安全处置的保障",
                subcategory="wastefree",
                source="危险废物集中处置设施建设规划",
                keywords=["危废处置设施", "集中处置", "安全处置"],
            ),
            EnvKnowledgeEntry(
                id="WFL005",
                content="工业固体废物综合利用率反映工业废物资源化水平",
                subcategory="wastefree",
                source="工业固体废物综合利用",
                keywords=["工业固废", "综合利用率", "资源化"],
            ),
            EnvKnowledgeEntry(
                id="WFL006",
                content="白色污染治理包括限制塑料购物袋使用和推广可降解塑料",
                subcategory="wastefree",
                source="关于进一步加强塑料污染治理的意见",
                keywords=["白色污染", "塑料污染", "可降解塑料"],
            ),
            EnvKnowledgeEntry(
                id="WFL007",
                content="餐厨垃圾应专门收集运输进行资源化处理",
                subcategory="wastefree",
                source="餐厨垃圾资源化处理技术规范",
                keywords=["餐厨垃圾", "厨余垃圾", "资源化处理"],
            ),
            EnvKnowledgeEntry(
                id="WFL008",
                content="废旧电池属于危险废物，应分类收集安全处置",
                subcategory="wastefree",
                source="废电池污染防治技术政策",
                keywords=["废旧电池", "废电池", "重金属"],
            ),
            EnvKnowledgeEntry(
                id="WFL009",
                content="废旧纺织品应通过捐赠、翻新或纤维化再利用等方式处理",
                subcategory="wastefree",
                source="废旧纺织品综合利用技术规范",
                keywords=["废旧纺织品", "旧衣回收", "再利用"],
            ),
            EnvKnowledgeEntry(
                id="WFL010",
                content="静脉产业是指废物的回收、再利用、再制造和资源化产业",
                subcategory="wastefree",
                source="静脉产业园区建设标准",
                keywords=["静脉产业", "资源循环", "再制造"],
            ),
        ]
        return self

    def load_soil_remediation(self) -> EnvironmentalKnowledgeBase:
        """加载土壤修复知识"""
        self._entries["soil_remediation"] = [
            EnvKnowledgeEntry(
                id="SRM001",
                content="土壤污染风险评估包括危害识别、暴露评估、毒性评估和风险表征",
                subcategory="soil_remediation",
                source="建设用地土壤污染风险评估技术导则",
                keywords=["风险评估", "危害识别", "暴露评估"],
                standard_code="HJ 25.3",
            ),
            EnvKnowledgeEntry(
                id="SRM002",
                content="土壤修复技术包括异位修复和原位修复两大类",
                subcategory="soil_remediation",
                source="建设用地土壤修复技术导则",
                keywords=["土壤修复技术", "异位修复", "原位修复"],
                standard_code="HJ 25.4",
            ),
            EnvKnowledgeEntry(
                id="SRM003",
                content="热脱附技术适用于挥发性有机物污染土壤修复",
                subcategory="soil_remediation",
                source="污染土壤异位热脱附处理工程技术规范",
                keywords=["热脱附", "有机物污染", "VOCs"],
                standard_code="HJ 662",
            ),
            EnvKnowledgeEntry(
                id="SRM004",
                content="土壤淋洗技术适用于重金属污染土壤处理",
                subcategory="soil_remediation",
                source="土壤淋洗技术指南",
                keywords=["土壤淋洗", "重金属修复", "淋洗液"],
            ),
            EnvKnowledgeEntry(
                id="SRM005",
                content="生物修复技术包括植物修复和微生物修复",
                subcategory="soil_remediation",
                source="污染地块土壤生物修复技术指南",
                keywords=["生物修复", "植物修复", "微生物修复"],
            ),
            EnvKnowledgeEntry(
                id="SRM006",
                content="建设用地土壤污染状况调查分为初步调查、详细调查和风险评估",
                subcategory="soil_remediation",
                source="建设用地土壤污染状况调查技术导则",
                keywords=["场地调查", "初步调查", "详细调查"],
                standard_code="HJ 25.1",
            ),
            EnvKnowledgeEntry(
                id="SRM007",
                content="农用地土壤污染风险管控包括农艺调控、种植结构调整等",
                subcategory="soil_remediation",
                source="农用地土壤污染风险管控标准",
                keywords=["农用地管控", "农艺调控", "种植调整"],
                standard_code="GB 15618",
            ),
            EnvKnowledgeEntry(
                id="SRM008",
                content="土壤修复工程需编制修复方案并经专家评审",
                subcategory="soil_remediation",
                source="污染地块土壤修复工程方案编制指南",
                keywords=["修复方案", "专家评审", "方案编制"],
            ),
            EnvKnowledgeEntry(
                id="SRM009",
                content="土壤修复效果评估需达到修复目标值要求",
                subcategory="soil_remediation",
                source="建设用地土壤修复效果评估技术规定",
                keywords=["效果评估", "修复目标", "达标评估"],
            ),
            EnvKnowledgeEntry(
                id="SRM010",
                content="矿山生态修复包括地形地貌景观修复、土壤重构和植被恢复",
                subcategory="soil_remediation",
                source="矿山生态修复工程技术规范",
                keywords=["矿山修复", "生态修复", "植被恢复"],
            ),
        ]
        return self

    def query(
        self,
        text: str,
        subcategory: Optional[str] = None,
        limit: int = 10,
    ) -> list[EnvKnowledgeEntry]:
        """
        查询环境知识

        Args:
            text: 查询文本
            subcategory: 子类别
            limit: 返回数量

        Returns:
            相关知识条目
        """
        text_lower = text.lower()
        results: list[tuple[int, EnvKnowledgeEntry]] = []

        categories = [subcategory] if subcategory else self._entries.keys()

        for cat in categories:
            for entry in self._entries.get(cat, []):
                score = 0
                for keyword in entry.keywords:
                    if keyword.lower() in text_lower:
                        score += 2
                if entry.standard_code and entry.standard_code.lower() in text_lower:
                    score += 5
                if score > 0:
                    results.append((score, entry))

        results.sort(key=lambda x: x[0], reverse=True)
        return [entry for _, entry in results[:limit]]

    def verify_fact(self, text: str) -> tuple[bool, Optional[str], Optional[str]]:
        """
        验证环境相关事实

        Returns:
            (是否匹配知识库, 匹配内容, 来源)
        """
        results = self.query(text, limit=1)
        if results:
            entry = results[0]
            for keyword in entry.keywords:
                if keyword in text:
                    return True, entry.content, f"{entry.source} ({entry.standard_code})" if entry.standard_code else entry.source
        return False, None, None

    def get_categories(self) -> list[str]:
        """获取所有子类别"""
        return list(self._entries.keys())

    def entry_count(self, subcategory: Optional[str] = None) -> int:
        """获取条目数量"""
        if subcategory:
            return len(self._entries.get(subcategory, []))
        return sum(len(entries) for entries in self._entries.values())


def create_default_env_knowledge_base() -> EnvironmentalKnowledgeBase:
    """创建默认环境知识库"""
    kb = EnvironmentalKnowledgeBase()
    kb.load_all()
    return kb
