"""
Film Theory RAG Knowledge Base
电影理论RAG知识库核心模块

基于三篇工作论文的理论架构：
- WP01: 马尔可夫三状态模型
- WP02: 认知共振与五阶段创作流
- WP03: 动态充分性与三维导航
"""

__version__ = "0.1.0"
__author__ = "Marlin阿杰"

from .theory_state import TheoryStateBase
from .work_memory import WorkMemoryBase
from .creator_profile import CreatorProfileBase

__all__ = [
    "TheoryStateBase",
    "WorkMemoryBase",
    "CreatorProfileBase"
]
