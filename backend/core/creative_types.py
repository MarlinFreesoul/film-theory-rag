"""
Creative Types - 共享类型定义

定义创作流程的核心枚举和数据类型
避免循环导入
"""

from dataclasses import dataclass
from typing import List
from enum import Enum


class CreativeStage(Enum):
    """五阶段创作流"""
    CLARIFY = "明确"      # 明确阶段：理清主题和概念
    FOCUS = "聚焦"        # 聚焦阶段：确定核心方向
    DIVERGE = "发散"      # 发散阶段：探索可能性
    CONVERGE = "收束"     # 收束阶段：做出选择
    ORGANIZE = "整理"     # 整理阶段：结构化呈现


@dataclass
class CreatorState:
    """
    创作者状态

    Attributes:
        stage: 当前创作阶段
        keywords: 关键词列表（主题、张力等）
        structure_dimension: 结构维度（前置/中置/后置）
        progress: 创作进度（0-1）
        context: 原始用户输入
    """
    stage: CreativeStage
    keywords: List[str]
    structure_dimension: str
    progress: float
    context: str

    def to_dict(self):
        """转换为字典"""
        return {
            'stage': self.stage.value,
            'keywords': self.keywords,
            'structure_dimension': self.structure_dimension,
            'progress': self.progress,
            'context': self.context
        }
