"""
作品记忆库 (Work Memory Base)

基于WP02的认知共振理论：
- 多媒体激发数据（图像、音频、视频、文本）
- 作品片段与张力的关联
- 支持按心境检索作品片段
"""

from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field, HttpUrl
from enum import Enum
from datetime import datetime


class MediaType(str, Enum):
    """媒体类型"""
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    TEXT = "text"


class ThreeStructureLayer(str, Enum):
    """三结构层次（与theory_state保持一致）"""
    L1 = "第一结构"  # 故事剧情
    L2 = "第二结构"  # 隐喻象征
    L3 = "第三结构"  # 创作意图


class MediaFragment(BaseModel):
    """多媒体片段"""
    fragment_id: str = Field(..., description="片段ID")
    media_type: MediaType = Field(..., description="媒体类型")
    source_work: str = Field(..., description="来源作品")
    director: str = Field(..., description="导演")
    content_path: str = Field(..., description="内容路径或URL")
    duration_seconds: Optional[float] = Field(None, description="时长（秒）- 音频/视频")
    timestamp_start: Optional[float] = Field(None, description="起始时间戳（秒）- 视频片段")
    timestamp_end: Optional[float] = Field(None, description="结束时间戳（秒）- 视频片段")
    description: str = Field(..., description="片段描述")
    tags: List[str] = Field(default_factory=list, description="标签")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")


class TensionAssociation(BaseModel):
    """张力关联"""
    tension_left: str = Field(..., description="张力左侧")
    tension_right: str = Field(..., description="张力右侧")
    balance_point: float = Field(..., ge=0.0, le=1.0, description="平衡点（0=完全左，1=完全右）")
    confidence: float = Field(..., ge=0.0, le=1.0, description="关联置信度")


class WorkFragment(BaseModel):
    """作品片段（带结构层次标注）"""
    fragment: MediaFragment = Field(..., description="媒体片段")
    structure_layer: ThreeStructureLayer = Field(..., description="所属结构层次")
    tension_associations: List[TensionAssociation] = Field(
        default_factory=list,
        description="张力关联列表"
    )
    keywords: List[str] = Field(default_factory=list, description="关键词")
    emotional_tags: List[str] = Field(default_factory=list, description="情感标签")


class WorkMemoryBase:
    """
    作品记忆库核心类

    功能：
    1. 管理多媒体片段数据
    2. 支持按张力检索片段
    3. 支持按结构层次检索
    4. 支持按情感标签检索
    5. 多模态激发素材管理
    """

    def __init__(self):
        self.work_fragments: Dict[str, WorkFragment] = {}
        self._load_initial_works()

    def _load_initial_works(self):
        """加载初始作品数据"""
        # 示例：侯孝贤《悲情城市》片段
        example_fragment = MediaFragment(
            fragment_id="hou_city_of_sadness_001",
            media_type=MediaType.VIDEO,
            source_work="悲情城市",
            director="侯孝贤",
            content_path="data/media/hou/city_of_sadness_opening.mp4",
            duration_seconds=180.0,
            timestamp_start=0.0,
            timestamp_end=180.0,
            description="开场长镜头：林家客厅，静止的家庭聚会与时代变迁的对比",
            tags=["长镜头", "固定机位", "家庭聚会", "时代背景"]
        )

        example_work = WorkFragment(
            fragment=example_fragment,
            structure_layer=ThreeStructureLayer.L2,  # 隐喻层
            tension_associations=[
                TensionAssociation(
                    tension_left="静止",
                    tension_right="流逝",
                    balance_point=0.8,  # 偏向静止
                    confidence=0.9
                )
            ],
            keywords=["时间", "家庭", "历史", "凝视"],
            emotional_tags=["沉静", "哀愁", "怀旧"]
        )

        self.work_fragments[example_fragment.fragment_id] = example_work

    def add_work_fragment(self, work_fragment: WorkFragment) -> None:
        """添加作品片段"""
        self.work_fragments[work_fragment.fragment.fragment_id] = work_fragment

    def get_fragment(self, fragment_id: str) -> Optional[WorkFragment]:
        """获取片段"""
        return self.work_fragments.get(fragment_id)

    def search_by_tension(
        self,
        tension_left: str,
        tension_right: str,
        balance_range: tuple[float, float] = (0.0, 1.0),
        min_confidence: float = 0.5
    ) -> List[WorkFragment]:
        """
        按张力搜索片段

        Args:
            tension_left: 张力左侧
            tension_right: 张力右侧
            balance_range: 平衡点范围 (min, max)
            min_confidence: 最小置信度
        """
        results = []
        for fragment in self.work_fragments.values():
            for assoc in fragment.tension_associations:
                if (assoc.tension_left == tension_left and
                    assoc.tension_right == tension_right and
                    balance_range[0] <= assoc.balance_point <= balance_range[1] and
                    assoc.confidence >= min_confidence):
                    results.append(fragment)
                    break
        return results

    def search_by_structure_layer(
        self,
        layer: ThreeStructureLayer
    ) -> List[WorkFragment]:
        """按结构层次搜索"""
        return [
            fragment for fragment in self.work_fragments.values()
            if fragment.structure_layer == layer
        ]

    def search_by_emotional_tags(
        self,
        tags: List[str],
        match_all: bool = False
    ) -> List[WorkFragment]:
        """
        按情感标签搜索

        Args:
            tags: 情感标签列表
            match_all: True=必须匹配所有标签，False=匹配任意标签
        """
        results = []
        for fragment in self.work_fragments.values():
            if match_all:
                if all(tag in fragment.emotional_tags for tag in tags):
                    results.append(fragment)
            else:
                if any(tag in fragment.emotional_tags for tag in tags):
                    results.append(fragment)
        return results

    def search_by_director(self, director: str) -> List[WorkFragment]:
        """按导演搜索"""
        return [
            fragment for fragment in self.work_fragments.values()
            if fragment.fragment.director == director
        ]

    def get_fragments_by_media_type(self, media_type: MediaType) -> List[WorkFragment]:
        """按媒体类型获取片段"""
        return [
            fragment for fragment in self.work_fragments.values()
            if fragment.fragment.media_type == media_type
        ]
