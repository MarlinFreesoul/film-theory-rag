"""
Intent Analyzer - 用户意图分析器

功能：
- 分析用户输入是新话题还是细化
- 提取关键词和约束条件
- 支持规则和LLM两种实现

设计：
- ABC抽象基类：定义统一接口
- RuleBasedAnalyzer：MVP版本，基于规则
- LLMBasedAnalyzer：未来版本，基于外部LLM（接口预留）
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class RefinementIntent:
    """细化意图"""
    is_refinement: bool  # 是否是细化（而非新话题）
    new_keywords: List[str]  # 新增关键词
    excluded_keywords: List[str]  # 排除关键词
    dimension_shift: Optional[str]  # 维度切换（如"色彩"、"构图"）
    refinement_type: Optional[str]  # 细化类型："add"、"exclude"、"replace"


class IntentAnalyzer(ABC):
    """意图分析器抽象基类"""

    @abstractmethod
    def analyze_refinement(self, new_input: str, context_keywords: List[str]) -> RefinementIntent:
        """
        分析用户细化意图

        Args:
            new_input: 用户新输入
            context_keywords: 上下文已有关键词

        Returns:
            RefinementIntent: 细化意图分析结果
        """
        pass


class RuleBasedAnalyzer(IntentAnalyzer):
    """基于规则的意图分析器（MVP版本）"""

    # 细化关键词模式
    REFINEMENT_PATTERNS = {
        'add': ['更', '还要', '加上', '另外', '同时'],
        'exclude': ['不要', '不是', '去掉', '排除', '换掉'],
        'replace': ['改成', '换成', '变成', '而是']
    }

    # 维度关键词
    DIMENSION_KEYWORDS = {
        '色彩': ['色彩', '颜色', '色调', '配色', '冷暖'],
        '构图': ['构图', '画面', '取景', '角度', '景别'],
        '光线': ['光线', '光影', '明暗', '照明', '自然光'],
        '时间': ['时间', '时长', '节奏', '速度', '剪辑'],
        '声音': ['声音', '音效', '配乐', '音乐', '氛围']
    }

    def analyze_refinement(self, new_input: str, context_keywords: List[str]) -> RefinementIntent:
        """分析用户细化意图"""

        # 1. 判断是否是细化
        is_refinement = self._is_refinement_input(new_input)

        # 2. 提取新关键词
        new_keywords = self._extract_keywords(new_input)

        # 3. 识别排除关键词
        excluded = self._extract_excluded_keywords(new_input)

        # 4. 检测维度切换
        dimension = self._detect_dimension_shift(new_input)

        # 5. 判断细化类型
        refinement_type = self._detect_refinement_type(new_input)

        return RefinementIntent(
            is_refinement=is_refinement,
            new_keywords=new_keywords,
            excluded_keywords=excluded,
            dimension_shift=dimension,
            refinement_type=refinement_type
        )

    def _is_refinement_input(self, user_input: str) -> bool:
        """判断是否是细化输入"""
        # 如果包含细化关键词，认为是细化
        for patterns in self.REFINEMENT_PATTERNS.values():
            for pattern in patterns:
                if pattern in user_input:
                    return True

        # 如果包含维度关键词，也认为是细化
        for keywords in self.DIMENSION_KEYWORDS.values():
            for kw in keywords:
                if kw in user_input:
                    return True

        # 否则认为是新话题
        return False

    def _extract_keywords(self, user_input: str) -> List[str]:
        """提取关键词（简单实现）"""
        # 简单的关键词列表
        keyword_candidates = [
            # 主题词
            '记忆', '时间', '孤独', '爱情', '死亡', '童年', '战争', '家庭',
            # 情绪词
            '忧郁', '怀旧', '恐惧', '喜悦', '悲伤', '孤独',
            # 风格词
            '现代', '古典', '未来', '乡土', '城市', '自然',
            # 技法词
            '长镜头', '蒙太奇', '固定镜头', '跟拍'
        ]

        keywords = []
        for kw in keyword_candidates:
            if kw in user_input:
                keywords.append(kw)

        return keywords

    def _extract_excluded_keywords(self, user_input: str) -> List[str]:
        """提取排除关键词"""
        excluded = []

        # 检查"不要XX"模式
        for pattern in self.REFINEMENT_PATTERNS['exclude']:
            if pattern in user_input:
                # 简单实现：提取"不要"后面的词
                # 实际应该用更复杂的NLP
                pass

        return excluded

    def _detect_dimension_shift(self, user_input: str) -> Optional[str]:
        """检测维度切换"""
        for dimension, keywords in self.DIMENSION_KEYWORDS.items():
            for kw in keywords:
                if kw in user_input:
                    return dimension
        return None

    def _detect_refinement_type(self, user_input: str) -> Optional[str]:
        """检测细化类型"""
        for ref_type, patterns in self.REFINEMENT_PATTERNS.items():
            for pattern in patterns:
                if pattern in user_input:
                    return ref_type
        return None


class LLMBasedAnalyzer(IntentAnalyzer):
    """
    基于LLM的意图分析器（未来版本）

    接口已预留，可以后续实现：
    - 调用OpenAI/Claude等LLM API
    - 更精准的意图理解
    - 上下文语义分析
    """

    def __init__(self, llm_client=None):
        """
        Args:
            llm_client: LLM客户端（OpenAI/Anthropic/etc）
        """
        self.llm_client = llm_client

    def analyze_refinement(self, new_input: str, context_keywords: List[str]) -> RefinementIntent:
        """使用LLM分析意图"""
        if not self.llm_client:
            raise NotImplementedError("LLM client not configured")

        # TODO: 调用LLM API
        # prompt = f"分析用户意图：\n上下文关键词：{context_keywords}\n新输入：{new_input}"
        # response = self.llm_client.complete(prompt)

        # 暂时返回默认值
        return RefinementIntent(
            is_refinement=False,
            new_keywords=[],
            excluded_keywords=[],
            dimension_shift=None,
            refinement_type=None
        )
