"""
创作者状态库 (Creator Profile Base)

基于WP03的动态充分性原则：
- 创作者角色动态构建
- 五阶段创作流追踪
- 三维空间导航状态
"""

from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


class CreativeStage(str, Enum):
    """五阶段创作流（来自WP02）"""
    CLARIFICATION = "明确"  # 明确核心张力与创作意图
    FOCUSING = "聚焦"  # 聚焦到具体场景/情节
    DIVERGENCE = "发散"  # 发散可能性探索
    CONVERGENCE = "收束"  # 收束到最优方案
    ORGANIZATION = "整理"  # 整理成完整结构


class StructureLevel(str, Enum):
    """三结构层次"""
    L1 = "第一结构"  # 故事剧情
    L2 = "第二结构"  # 隐喻象征
    L3 = "第三结构"  # 创作意图


class CognitiveStyle(str, Enum):
    """认知风格"""
    VISUAL_DOMINANT = "视觉优先"
    AUDITORY_DOMINANT = "听觉优先"
    CONCEPTUAL_DOMINANT = "概念优先"
    MULTIMODAL_BALANCED = "多模态平衡"


class ExperienceLevel(str, Enum):
    """经验水平"""
    BEGINNER = "初级"
    INTERMEDIATE = "中级"
    ADVANCED = "高级"
    EXPERT = "专家"


class StimulusPreference(BaseModel):
    """激发偏好（来自WP03动态充分性）"""
    visual_effect: float = Field(..., ge=0.0, le=1.0, description="视觉刺激效果")
    auditory_effect: float = Field(..., ge=0.0, le=1.0, description="听觉刺激效果")
    textual_effect: float = Field(..., ge=0.0, le=1.0, description="文本概念效果")
    sufficiency_threshold: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="充分性阈值（多高算'够了'）"
    )


class CreativePosition(BaseModel):
    """三维创作空间位置（来自WP03）"""
    structure_level: StructureLevel = Field(..., description="当前结构层次")
    creative_stage: CreativeStage = Field(..., description="当前创作阶段")
    progress: float = Field(..., ge=0.0, le=1.0, description="当前阶段进度")

    def __repr__(self):
        return f"({self.structure_level}, {self.creative_stage}, {self.progress:.1%})"


class TensionPair(BaseModel):
    """创作者核心张力对"""
    left: str = Field(..., description="张力左侧")
    right: str = Field(..., description="张力右侧")
    current_balance: float = Field(..., ge=0.0, le=1.0, description="当前平衡点")
    description: str = Field(..., description="张力描述")


class CreatorProfile(BaseModel):
    """创作者画像（动态构建的角色）"""
    creator_id: str = Field(..., description="创作者ID")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

    # Personality 部分
    core_tensions: List[TensionPair] = Field(
        default_factory=list,
        description="核心张力列表"
    )
    cognitive_style: CognitiveStyle = Field(
        default=CognitiveStyle.MULTIMODAL_BALANCED,
        description="认知风格"
    )
    experience_level: ExperienceLevel = Field(
        default=ExperienceLevel.BEGINNER,
        description="经验水平"
    )
    current_mood: str = Field(
        default="平静",
        description="当前心境描述"
    )

    # Principle 部分
    stimulus_preference: StimulusPreference = Field(
        ...,
        description="激发偏好（动态充分性的核心）"
    )
    thinking_pace: str = Field(
        default="需要留白时间",
        description="思考节奏（慢协商设计）"
    )

    # Knowledge 部分（当前状态）
    current_position: CreativePosition = Field(
        ...,
        description="三维创作空间当前位置"
    )
    completed_stages: List[Dict] = Field(
        default_factory=list,
        description="已完成阶段历史"
    )
    stagnation_count: int = Field(
        default=0,
        description="卡点计数（用于触发三结构切换）"
    )
    idle_seconds: float = Field(
        default=0.0,
        description="操作停滞时间（秒）"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "creator_id": "creator_001",
                "core_tensions": [
                    {
                        "left": "连接",
                        "right": "孤独",
                        "current_balance": 0.6,
                        "description": "在人际连接与孤独自省之间寻找平衡"
                    }
                ],
                "cognitive_style": "视觉优先",
                "experience_level": "中级",
                "current_mood": "困惑中寻找方向",
                "stimulus_preference": {
                    "visual_effect": 0.9,
                    "auditory_effect": 0.6,
                    "textual_effect": 0.7,
                    "sufficiency_threshold": 0.75
                },
                "thinking_pace": "需要留白时间",
                "current_position": {
                    "structure_level": "第二结构",
                    "creative_stage": "聚焦",
                    "progress": 0.3
                }
            }
        }


class CreatorProfileBase:
    """
    创作者状态库核心类

    功能：
    1. 管理创作者画像数据
    2. 追踪创作进度（三维空间导航）
    3. 动态更新激发偏好
    4. 检测卡点与触发条件
    5. 支持慢协商设计哲学
    """

    def __init__(self):
        self.creator_profiles: Dict[str, CreatorProfile] = {}

    def create_profile(self, creator_id: str) -> CreatorProfile:
        """创建新的创作者画像"""
        profile = CreatorProfile(
            creator_id=creator_id,
            stimulus_preference=StimulusPreference(
                visual_effect=0.7,
                auditory_effect=0.7,
                textual_effect=0.7,
                sufficiency_threshold=0.7
            ),
            current_position=CreativePosition(
                structure_level=StructureLevel.L3,
                creative_stage=CreativeStage.CLARIFICATION,
                progress=0.0
            )
        )
        self.creator_profiles[creator_id] = profile
        return profile

    def get_profile(self, creator_id: str) -> Optional[CreatorProfile]:
        """获取创作者画像"""
        return self.creator_profiles.get(creator_id)

    def update_position(
        self,
        creator_id: str,
        structure_level: Optional[StructureLevel] = None,
        creative_stage: Optional[CreativeStage] = None,
        progress: Optional[float] = None
    ) -> None:
        """更新创作位置"""
        profile = self.get_profile(creator_id)
        if not profile:
            return

        if structure_level:
            profile.current_position.structure_level = structure_level
        if creative_stage:
            profile.current_position.creative_stage = creative_stage
        if progress is not None:
            profile.current_position.progress = progress

        profile.updated_at = datetime.now()

    def record_stagnation(self, creator_id: str) -> bool:
        """
        记录卡点事件

        Returns:
            是否触发三结构切换（卡点阈值）
        """
        profile = self.get_profile(creator_id)
        if not profile:
            return False

        profile.stagnation_count += 1
        profile.updated_at = datetime.now()

        # 触发阈值：连续3次卡点
        return profile.stagnation_count >= 3

    def update_idle_time(self, creator_id: str, seconds: float) -> bool:
        """
        更新操作停滞时间

        Returns:
            是否触发操作停滞检测（来自WP03的"时间静默也是认知状态的信号"）
        """
        profile = self.get_profile(creator_id)
        if not profile:
            return False

        profile.idle_seconds = seconds
        profile.updated_at = datetime.now()

        # 触发阈值：停滞超过120秒
        return seconds >= 120.0

    def reset_stagnation(self, creator_id: str) -> None:
        """重置卡点计数（成功推进后）"""
        profile = self.get_profile(creator_id)
        if profile:
            profile.stagnation_count = 0
            profile.idle_seconds = 0.0
            profile.updated_at = datetime.now()

    def calculate_stimulus_sufficiency(
        self,
        creator_id: str,
        visual_count: int,
        auditory_count: int,
        textual_count: int
    ) -> Tuple[float, bool]:
        """
        计算当前激发的充分性（WP03核心算法）

        Returns:
            (sufficiency_score, is_sufficient)
        """
        profile = self.get_profile(creator_id)
        if not profile:
            return 0.0, False

        pref = profile.stimulus_preference

        # 加权计算充分性得分
        score = (
            visual_count * pref.visual_effect +
            auditory_count * pref.auditory_effect +
            textual_count * pref.textual_effect
        ) / 3.0

        # 归一化到[0, 1]
        normalized_score = min(1.0, score)

        # 判断是否充分
        is_sufficient = normalized_score >= pref.sufficiency_threshold

        return normalized_score, is_sufficient

    def complete_stage(self, creator_id: str) -> None:
        """完成当前阶段，进入下一阶段"""
        profile = self.get_profile(creator_id)
        if not profile:
            return

        # 记录完成的阶段
        profile.completed_stages.append({
            "structure_level": profile.current_position.structure_level,
            "stage": profile.current_position.creative_stage,
            "completed_at": datetime.now().isoformat()
        })

        # 重置卡点
        self.reset_stagnation(creator_id)

        # 更新时间
        profile.updated_at = datetime.now()
