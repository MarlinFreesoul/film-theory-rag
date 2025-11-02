"""
State Tracker - 创作者状态追踪器

核心功能：
- 分析用户输入，识别创作状态（阶段、关键词、结构维度）
- 发布状态变化事件，触发相关模块响应
- 基于五阶段创作流理论
- 支持多轮对话的上下文融合
"""

from typing import List, Optional, TYPE_CHECKING
from .intent_analyzer import IntentAnalyzer, RuleBasedAnalyzer
from .llm_keyword_extractor import LLMKeywordExtractor
from .creative_types import CreativeStage, CreatorState

# 延迟导入避免循环依赖
if TYPE_CHECKING:
    from .guiding_dialogue import GuidingQuestion


class StateTracker:
    """
    状态追踪器

    负责：
    1. 分析用户输入
    2. 识别创作状态
    3. 发布状态变化事件
    """

    def __init__(self, event_bus, intent_analyzer: Optional[IntentAnalyzer] = None, llm_extractor: Optional[LLMKeywordExtractor] = None):
        self.event_bus = event_bus
        self.current_state: Optional[CreatorState] = None

        # 意图分析器（支持依赖注入，默认使用规则版本）
        self.intent_analyzer = intent_analyzer or RuleBasedAnalyzer()

        # LLM关键词提取器（支持依赖注入）
        self.llm_extractor = llm_extractor
        if self.llm_extractor:
            print("[StateTracker] Using LLM keyword extraction")

        # 五阶段检测和引导（延迟导入避免循环依赖）
        from .guiding_dialogue import get_stage_detector, get_question_generator
        self.stage_detector = get_stage_detector()
        self.question_generator = get_question_generator()
        print("[StateTracker] Five-stage guiding dialogue enabled")

        # 关键词映射表（MVP版本：简单匹配）
        self.keyword_map = {
            '记忆': ['记忆', '回忆', '往事', '过去', '遗忘', '追忆'],
            '时间': ['时间', '流逝', '岁月', '年代', '瞬间', '永恒'],
            '空间': ['空间', '场所', '地点', '环境', '房间', '街道'],
            '人物': ['人物', '角色', '关系', '对话', '性格', '情感'],
            '冲突': ['冲突', '矛盾', '对立', '张力', '撕裂', '挣扎'],
            '寻找': ['寻找', '追寻', '探索', '迷失', '找寻', '追问'],
        }

        # 阶段识别关键词
        self.stage_keywords = {
            CreativeStage.CLARIFY: ['想法', '概念', '主题', '是什么', '想做', '探讨'],
            CreativeStage.FOCUS: ['构思', '聚焦', '确定', '选择', '决定', '要'],
            CreativeStage.DIVERGE: ['发散', '探索', '可能性', '如果', '还可以', '或者'],
            CreativeStage.CONVERGE: ['收束', '决定', '确定', '选定', '就这个', '敲定'],
            CreativeStage.ORGANIZE: ['整理', '梳理', '结构', '组织', '框架', '安排'],
        }

        # 结构维度关键词
        self.structure_keywords = {
            '前置': ['开头', '起始', '引入', '开场', '序幕'],
            '中置': ['中间', '发展', '过程', '展开'],
            '后置': ['结尾', '收尾', '总结', '结局', '尾声'],
        }

    def analyze_input(self, user_input: str, context_keywords: List[str] = None, turn_number: int = 1) -> CreatorState:
        """
        分析用户输入，识别创作状态（支持上下文融合 + 五阶段检测）

        Args:
            user_input: 用户输入的文本
            context_keywords: 上下文关键词（来自历史对话）
            turn_number: 当前对话轮数（用于五阶段检测）

        Returns:
            CreatorState: 识别出的创作状态
        """
        context_keywords = context_keywords or []

        # 使用意图分析器分析细化意图
        refinement = self.intent_analyzer.analyze_refinement(user_input, context_keywords)

        # 提取当前输入的关键词
        if self.llm_extractor:
            # 使用LLM提取语义关键词
            current_keywords = self.llm_extractor.extract_keywords(user_input, context_keywords)
            print(f"[StateTracker] LLM extracted keywords: {current_keywords}")
        else:
            # 降级：使用规则提取
            current_keywords = self._extract_keywords(user_input)
            print(f"[StateTracker] Rule extracted keywords: {current_keywords}")

        # 融合关键词
        if refinement.is_refinement and context_keywords:
            # 如果是细化，融合上下文关键词
            keywords = self._merge_keywords(
                context_keywords,
                current_keywords,
                refinement
            )
        else:
            # 如果是新话题，只用当前关键词
            keywords = current_keywords

        # 使用旧的阶段检测（兼容）
        old_stage = self._detect_stage(user_input)

        # 创建临时状态用于五阶段检测
        temp_state = CreatorState(
            stage=old_stage,
            keywords=keywords,
            structure_dimension='',
            progress=0,
            context=user_input
        )

        # 使用新的五阶段检测器（优先）
        stage = self.stage_detector.detect_stage(
            user_input=user_input,
            current_state=temp_state,
            turn_number=turn_number,
            context_keywords=context_keywords
        )

        print(f"[StateTracker] Detected stage: {stage.value} (turn {turn_number})")

        structure_dim = self._detect_structure(user_input)
        progress = self._estimate_progress(stage)

        new_state = CreatorState(
            stage=stage,
            keywords=keywords,
            structure_dimension=structure_dim,
            progress=progress,
            context=user_input
        )

        # 发布状态变化事件
        if self._has_state_changed(new_state):
            self.event_bus.publish(
                event_type='state_changed',
                data={
                    'previous': self.current_state.to_dict() if self.current_state else None,
                    'current': new_state.to_dict()
                },
                source='state_tracker'
            )

        self.current_state = new_state
        return new_state

    def generate_guiding_questions(self, turn_number: int) -> List['GuidingQuestion']:
        """
        生成当前阶段的引导性问题

        Args:
            turn_number: 当前对话轮数

        Returns:
            引导性问题列表
        """
        if not self.current_state:
            return []

        questions = self.question_generator.generate_questions(
            stage=self.current_state.stage,
            creator_state=self.current_state,
            turn_number=turn_number
        )

        print(f"[StateTracker] Generated {len(questions)} guiding questions for stage {self.current_state.stage.value}")

        return questions

    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        found = []

        for main_keyword, patterns in self.keyword_map.items():
            if any(pattern in text for pattern in patterns):
                found.append(main_keyword)

        return found

    def _detect_stage(self, text: str) -> CreativeStage:
        """检测创作阶段"""
        # 计算每个阶段的匹配分数
        scores = {}

        for stage, keywords in self.stage_keywords.items():
            score = sum(1 for kw in keywords if kw in text)
            scores[stage] = score

        # 返回得分最高的阶段
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)

        # 默认返回聚焦阶段
        return CreativeStage.FOCUS

    def _detect_structure(self, text: str) -> str:
        """检测结构维度"""
        for dimension, keywords in self.structure_keywords.items():
            if any(kw in text for kw in keywords):
                return dimension

        return '中置'  # 默认

    def _estimate_progress(self, stage: CreativeStage) -> float:
        """根据阶段估算进度"""
        stage_progress = {
            CreativeStage.CLARIFY: 0.2,
            CreativeStage.FOCUS: 0.4,
            CreativeStage.DIVERGE: 0.5,
            CreativeStage.CONVERGE: 0.7,
            CreativeStage.ORGANIZE: 0.9,
        }
        return stage_progress.get(stage, 0.5)

    def _merge_keywords(self, context_keywords: List[str], current_keywords: List[str], refinement) -> List[str]:
        """
        融合上下文关键词和当前关键词

        Args:
            context_keywords: 上下文关键词
            current_keywords: 当前输入的关键词
            refinement: 细化意图分析结果

        Returns:
            融合后的关键词列表
        """
        merged = set()

        # 1. 添加上下文关键词（保留历史）
        for kw in context_keywords:
            if kw not in refinement.excluded_keywords:
                merged.add(kw)

        # 2. 添加新关键词
        for kw in current_keywords:
            merged.add(kw)

        # 3. 添加意图分析器提取的新关键词
        for kw in refinement.new_keywords:
            merged.add(kw)

        return list(merged)

    def _has_state_changed(self, new_state: CreatorState) -> bool:
        """判断状态是否发生变化"""
        if self.current_state is None:
            return True

        # 比较关键属性
        return (
            self.current_state.stage != new_state.stage or
            set(self.current_state.keywords) != set(new_state.keywords) or
            self.current_state.structure_dimension != new_state.structure_dimension
        )

    def get_current_state(self) -> Optional[CreatorState]:
        """获取当前状态"""
        return self.current_state
