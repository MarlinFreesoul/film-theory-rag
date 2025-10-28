"""
理论状态库 (Theory State Base)

基于WP01的三状态模型：
- 状态1：原型状态（心境的张力压缩）
- 状态2：当前状态（对话式角色构建）
- 状态3：投射状态（可能性空间生成）
"""

from typing import Dict, List, Tuple, Optional
from pydantic import BaseModel, Field
from enum import Enum


class TensionType(str, Enum):
    """张力类型"""
    TEMPORAL = "temporal"  # 时间性张力（如静止↔流逝）
    SPATIAL = "spatial"  # 空间性张力（如封闭↔开放）
    EMOTIONAL = "emotional"  # 情感性张力（如连接↔孤独）
    METAPHYSICAL = "metaphysical"  # 形而上张力（如秩序↔熵增）
    PERCEPTUAL = "perceptual"  # 感知性张力（如表层↔潜意识）


class DirectorTension(BaseModel):
    """导演核心张力"""
    director: str = Field(..., description="导演名称")
    tension_pair: Tuple[str, str] = Field(..., description="张力对（左↔右）")
    tension_type: TensionType = Field(..., description="张力类型")
    alpha: float = Field(..., ge=0.0, le=1.0, description="压缩系数α，控制张力平衡点")
    description: str = Field(..., description="张力描述")
    representative_works: List[str] = Field(default_factory=list, description="代表作品")

    class Config:
        json_schema_extra = {
            "example": {
                "director": "侯孝贤",
                "tension_pair": ("静止", "流逝"),
                "tension_type": "temporal",
                "alpha": 0.8,
                "description": "时间的双重性：静止的凝视与不可逆的流逝",
                "representative_works": ["《悲情城市》", "《最好的时光》"]
            }
        }


class ThreeStructureLevel(str, Enum):
    """三结构层次"""
    L1 = "第一结构"  # 故事剧情
    L2 = "第二结构"  # 隐喻象征
    L3 = "第三结构"  # 创作意图


class TheoreticalConcept(BaseModel):
    """理论概念"""
    concept_id: str = Field(..., description="概念ID")
    name: str = Field(..., description="概念名称")
    structure_level: ThreeStructureLevel = Field(..., description="所属结构层次")
    definition: str = Field(..., description="概念定义")
    keywords: List[str] = Field(default_factory=list, description="关键词")
    related_concepts: List[str] = Field(default_factory=list, description="相关概念ID")
    examples: List[Dict] = Field(default_factory=list, description="示例（作品、场景等）")


class TheoryStateBase:
    """
    理论状态库核心类

    功能：
    1. 管理导演核心张力数据
    2. 管理三结构理论概念
    3. 支持基于张力的检索
    4. 支持概念关联网络查询
    """

    def __init__(self):
        self.director_tensions: Dict[str, DirectorTension] = {}
        self.theoretical_concepts: Dict[str, TheoreticalConcept] = {}
        self._load_initial_data()

    def _load_initial_data(self):
        """加载初始数据（来自三篇工作论文）"""
        # 初始导演张力数据（来自WP01）
        initial_directors = [
            DirectorTension(
                director="侯孝贤",
                tension_pair=("静止", "流逝"),
                tension_type=TensionType.TEMPORAL,
                alpha=0.8,
                description="时间的双重性：静止的凝视与不可逆的流逝",
                representative_works=["《悲情城市》", "《最好的时光》"]
            ),
            DirectorTension(
                director="诺兰",
                tension_pair=("秩序", "熵增"),
                tension_type=TensionType.METAPHYSICAL,
                alpha=0.5,
                description="对抗熵增的秩序构建与必然崩溃的平衡",
                representative_works=["《信条》", "《盗梦空间》", "《星际穿越》"]
            ),
            DirectorTension(
                director="林奇",
                tension_pair=("表层", "潜意识"),
                tension_type=TensionType.PERCEPTUAL,
                alpha=0.3,
                description="日常表象下涌动的潜意识暗流",
                representative_works=["《穆赫兰道》", "《双峰》"]
            )
        ]

        for director in initial_directors:
            self.director_tensions[director.director] = director

    def add_director_tension(self, tension: DirectorTension) -> None:
        """添加导演张力"""
        self.director_tensions[tension.director] = tension

    def get_director_tension(self, director: str) -> Optional[DirectorTension]:
        """获取导演张力"""
        return self.director_tensions.get(director)

    def search_by_tension_type(self, tension_type: TensionType) -> List[DirectorTension]:
        """按张力类型搜索"""
        return [
            tension for tension in self.director_tensions.values()
            if tension.tension_type == tension_type
        ]

    def add_concept(self, concept: TheoreticalConcept) -> None:
        """添加理论概念"""
        self.theoretical_concepts[concept.concept_id] = concept

    def get_concept(self, concept_id: str) -> Optional[TheoreticalConcept]:
        """获取理论概念"""
        return self.theoretical_concepts.get(concept_id)

    def get_related_concepts(self, concept_id: str, depth: int = 1) -> List[TheoreticalConcept]:
        """获取相关概念网络"""
        if depth <= 0:
            return []

        concept = self.get_concept(concept_id)
        if not concept:
            return []

        related = []
        for related_id in concept.related_concepts:
            related_concept = self.get_concept(related_id)
            if related_concept:
                related.append(related_concept)
                if depth > 1:
                    related.extend(self.get_related_concepts(related_id, depth - 1))

        return related
