"""
渐进式内容返回控制器 - 智能体的决策大脑

这个控制器决定每一轮对话应该返回什么内容,实现:
1. 渐进式内容释放 (不是一次性倾泻)
2. 阶段差异化策略 (不同阶段返回不同内容)
3. 用户意图感知 (检测不满、困惑、满意等情绪)
4. 自适应调整 (根据用户反馈调整策略)
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class UserSentiment(Enum):
    """用户情绪检测"""
    SATISFIED = "satisfied"        # 满意 - 继续当前策略
    CONFUSED = "confused"          # 困惑 - 需要澄清
    FRUSTRATED = "frustrated"      # 挫败 - 需要改变策略
    CURIOUS = "curious"           # 好奇 - 可以加快节奏
    NEUTRAL = "neutral"           # 中性 - 正常推进


@dataclass
class ContentPlan:
    """内容返回计划"""
    # 是否返回各类内容
    return_keywords: bool = False
    return_theory: bool = False
    return_works: bool = False
    return_scenes: bool = False
    return_question: bool = True  # 引导问题始终返回

    # 数量限制
    theory_limit: int = 0
    works_limit: int = 0
    scenes_limit: int = 0

    # 场景索引 (用于逐个返回场景)
    scene_index: int = 0

    # 特殊指令
    explain_process: bool = False  # 是否需要解释创作流程
    adjust_strategy: bool = False  # 是否需要调整策略

    # 返回理由 (用于调试和日志)
    reason: str = ""


class ProgressiveContentController:
    """渐进式内容返回控制器 - 智能体的决策核心"""

    # 阶段内容策略配置
    STAGE_STRATEGIES = {
        '明确': {
            'phase': 'clarify',
            'focus': 'keywords',
            'max_theory': 0,
            'max_works': 0,
            'max_scenes': 0,
            'description': '明确创作意图,提取核心关键词'
        },
        '聚焦': {
            'phase': 'focus',
            'focus': 'theory',
            'max_theory': 2,
            'max_works': 0,
            'max_scenes': 0,
            'description': '聚焦理论框架,建立概念基础'
        },
        '发散': {
            'phase': 'diverge',
            'focus': 'works',
            'max_theory': 0,
            'max_works': 3,
            'max_scenes': 0,
            'description': '发散作品参考,拓宽创作视野'
        },
        '收敛': {
            'phase': 'converge',
            'focus': 'scenes',
            'max_theory': 0,
            'max_works': 0,
            'max_scenes': 1,  # 一次一个场景
            'description': '收敛到具体场景,逐步构建视觉'
        },
        '整理': {
            'phase': 'organize',
            'focus': 'summary',
            'max_theory': 0,
            'max_works': 0,
            'max_scenes': 3,  # 展示所有场景
            'description': '整理创作成果,形成完整方案'
        }
    }

    def __init__(self):
        self.last_plan: Optional[ContentPlan] = None

    def plan_content(
        self,
        turn_number: int,
        stage: str,
        user_input: str,
        conversation_history: List[Dict[str, Any]] = None
    ) -> ContentPlan:
        """
        智能决策:根据多个因素决定返回什么内容

        Args:
            turn_number: 当前轮次
            stage: 当前阶段 (明确/聚焦/发散/收敛/整理)
            user_input: 用户最新输入
            conversation_history: 对话历史

        Returns:
            ContentPlan: 内容返回计划
        """
        # 1. 检测用户情绪
        sentiment = self._detect_user_sentiment(user_input)

        # 2. 如果用户挫败,立即调整策略
        if sentiment == UserSentiment.FRUSTRATED:
            return self._handle_frustrated_user(turn_number, stage, user_input)

        # 3. 如果用户困惑,提供解释
        if sentiment == UserSentiment.CONFUSED:
            return self._handle_confused_user(turn_number, stage)

        # 4. 正常流程:基于轮次和阶段决策
        return self._plan_by_turn_and_stage(turn_number, stage, sentiment)

    def _detect_user_sentiment(self, user_input: str) -> UserSentiment:
        """
        检测用户情绪 (简单版本,可以后续用LLM增强)
        """
        text = user_input.lower()

        # 挫败感关键词
        frustrated_keywords = [
            '为什么', '没有结果', '不对', '不行', '错了',
            '不是这样', '不满意', '没用', '怎么回事',
            '一直', '始终', '总是', '还是'
        ]

        # 困惑关键词
        confused_keywords = [
            '什么意思', '不懂', '不明白', '怎么', '如何',
            '能解释', '是什么', '看不懂', '不理解'
        ]

        # 满意/好奇关键词
        satisfied_keywords = [
            '好的', '很好', '不错', '对', '是的', '继续',
            '有意思', '喜欢', '想看', '想要', '可以'
        ]

        if any(kw in text for kw in frustrated_keywords):
            return UserSentiment.FRUSTRATED

        if any(kw in text for kw in confused_keywords):
            return UserSentiment.CONFUSED

        if any(kw in text for kw in satisfied_keywords):
            return UserSentiment.SATISFIED

        # 检查是否是深入问题 (好奇)
        if '?' in text or '?' in text or len(text) > 20:
            return UserSentiment.CURIOUS

        return UserSentiment.NEUTRAL

    def _handle_frustrated_user(
        self,
        turn_number: int,
        stage: str,
        user_input: str
    ) -> ContentPlan:
        """
        处理挫败的用户 - 改变策略

        如果用户说"为什么没有结果",说明:
        1. 用户期待更具体的东西
        2. 当前返回的内容不够实用
        3. 需要直接给场景或作品
        """
        plan = ContentPlan(
            return_question=True,
            explain_process=True,
            adjust_strategy=True,
            reason=f"检测到用户挫败感,调整策略 (Turn {turn_number})"
        )

        # 策略:直接跳到场景生成
        plan.return_scenes = True
        plan.scenes_limit = 2  # 给2个场景

        # 同时给一些作品参考
        plan.return_works = True
        plan.works_limit = 2

        return plan

    def _handle_confused_user(
        self,
        turn_number: int,
        stage: str
    ) -> ContentPlan:
        """
        处理困惑的用户 - 提供解释
        """
        return ContentPlan(
            return_question=True,
            explain_process=True,
            reason=f"检测到用户困惑,提供流程解释 (Turn {turn_number})"
        )

    def _plan_by_turn_and_stage(
        self,
        turn_number: int,
        stage: str,
        sentiment: UserSentiment
    ) -> ContentPlan:
        """
        基于轮次和阶段的正常决策流程

        核心策略:
        - Turn 1: 仅关键词 + 问题 (建立意图)
        - Turn 2-3: 根据阶段返回理论或作品 (建立框架)
        - Turn 4+: 逐个返回场景 (具体创作)
        """
        strategy = self.STAGE_STRATEGIES.get(stage, self.STAGE_STRATEGIES['明确'])

        plan = ContentPlan(
            return_question=True,
            reason=f"Turn {turn_number}, Stage: {stage}, Sentiment: {sentiment.value}"
        )

        # Turn 1: 明确阶段 - 仅返回关键词
        if turn_number == 1:
            plan.return_keywords = True
            plan.reason += " | Turn 1: 仅关键词+引导问题"
            return plan

        # Turn 2: 根据阶段决定
        if turn_number == 2:
            if stage in ['明确', '聚焦']:
                # 聚焦阶段:返回理论
                plan.return_theory = True
                plan.theory_limit = 2
                plan.reason += " | Turn 2: 返回理论框架"
            else:
                # 如果已经进入发散/收敛,返回作品
                plan.return_works = True
                plan.works_limit = 2
                plan.reason += " | Turn 2: 返回作品参考"
            return plan

        # Turn 3: 补充理论或作品
        if turn_number == 3:
            if stage in ['明确', '聚焦']:
                # 补充作品
                plan.return_works = True
                plan.works_limit = 2
                plan.reason += " | Turn 3: 补充作品参考"
            else:
                # 进入场景生成
                plan.return_scenes = True
                plan.scenes_limit = 1
                plan.scene_index = 0
                plan.reason += " | Turn 3: 开始场景生成"
            return plan

        # Turn 4+: 逐个返回场景
        if turn_number >= 4:
            # 收敛阶段:逐个返回场景
            if stage in ['收敛', '发散']:
                plan.return_scenes = True
                plan.scenes_limit = 1
                plan.scene_index = turn_number - 4
                plan.reason += f" | Turn {turn_number}: 返回场景 #{plan.scene_index + 1}"

            # 整理阶段:返回所有场景总结
            elif stage == '整理':
                plan.return_scenes = True
                plan.scenes_limit = 10  # 返回所有
                plan.reason += f" | Turn {turn_number}: 整理阶段,展示所有场景"

            # 如果还在明确/聚焦,给更多理论或作品
            else:
                if turn_number % 2 == 0:
                    plan.return_theory = True
                    plan.theory_limit = 1
                else:
                    plan.return_works = True
                    plan.works_limit = 2
                plan.reason += f" | Turn {turn_number}: 继续建立框架"

            return plan

        return plan

    def should_show_progress_explanation(self, turn_number: int) -> bool:
        """
        是否应该向用户解释当前进度

        在某些时刻,主动告诉用户"我们现在在哪里,接下来要做什么"
        """
        # Turn 1, 4, 7: 每3轮提醒一次
        return turn_number in [1, 4, 7, 10]

    def get_progress_message(self, turn_number: int, stage: str) -> str:
        """
        生成进度说明消息

        例如: "我们现在处于'聚焦'阶段,正在为你寻找理论框架。接下来我会问你一些问题来明确方向。"
        """
        strategy = self.STAGE_STRATEGIES.get(stage, self.STAGE_STRATEGIES['明确'])

        messages = {
            1: f"我们开始创作之旅!现在是'{stage}'阶段,我会先帮你提炼核心关键词。",
            4: f"很好!我们已经进入'{stage}'阶段。{strategy['description']}。让我们一步步深入。",
            7: f"进展顺利!当前是'{stage}'阶段,{strategy['description']}。继续保持这个节奏。",
            10: f"我们快要完成了!'{stage}'阶段即将收尾。"
        }

        return messages.get(turn_number, "")


# 全局单例
_controller_instance = None

def get_progressive_controller() -> ProgressiveContentController:
    """获取控制器单例"""
    global _controller_instance
    if _controller_instance is None:
        _controller_instance = ProgressiveContentController()
    return _controller_instance
