"""
Guiding Dialogue Module - 引导性对话模块

基于论文第4节"五阶段创作流模型"实现：
1. 检测用户当前处于哪个阶段
2. 生成该阶段对应的引导性问题
3. 驱动认知共振循环

五阶段：
- CLARIFY（明确）：识别哲学内核
- FOCUS（聚焦）：具体化创作场景
- DIVERGE（发散）：探索可能性
- CONVERGE（收束）：深化特定方向
- ORGANIZE（整理）：生成可执行方案
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from .creative_types import CreativeStage, CreatorState


@dataclass
class GuidingQuestion:
    """引导性问题"""
    question: str  # 问题文本
    purpose: str   # 问题目的（解释为什么问这个）
    stage: CreativeStage  # 对应的阶段
    priority: float = 0.5  # 优先级（0-1）


class StageDetector:
    """
    五阶段检测器

    基于对话历史和当前状态，判断用户处于哪个创作阶段
    """

    def __init__(self):
        # 阶段特征关键词（简单规则版本，后续可用LLM增强）
        self.stage_patterns = {
            CreativeStage.CLARIFY: {
                'indicators': ['想拍', '想做', '想法', '主题', '探讨', '想表达', '为什么'],
                'missing': ['场景', '镜头', '具体'],  # 缺少具体化元素
            },
            CreativeStage.FOCUS: {
                'indicators': ['场景', '地点', '人物', '什么时候', '哪里', '多久'],
                'has_core': True,  # 已有核心主题
            },
            CreativeStage.DIVERGE: {
                'indicators': ['还可以', '或者', '如果', '会怎样', '其他方法', '别的'],
                'questions': ['?'],  # 用户开始主动提问
            },
            CreativeStage.CONVERGE: {
                'indicators': ['就这个', '确定', '选择', '决定', '深入', '具体怎么'],
                'has_variants': True,  # 已经探索过多个方案
            },
            CreativeStage.ORGANIZE: {
                'indicators': ['脚本', '整理', '梳理', '怎么执行', '怎么拍'],
                'clear_direction': True,  # 方向已明确
            }
        }

    def detect_stage(
        self,
        user_input: str,
        current_state: CreatorState,
        turn_number: int,
        context_keywords: List[str]
    ) -> CreativeStage:
        """
        检测用户当前处于哪个阶段

        Args:
            user_input: 用户当前输入
            current_state: 当前创作者状态
            turn_number: 对话轮数
            context_keywords: 上下文关键词

        Returns:
            检测到的创作阶段
        """

        # 第一轮对话：通常是CLARIFY（明确）
        if turn_number == 1:
            # 但如果用户一开始就很具体，可能直接到FOCUS
            if self._has_concrete_scenario(user_input):
                return CreativeStage.FOCUS
            return CreativeStage.CLARIFY

        # 检测是否在提问（发散的信号）
        if '?' in user_input or any(word in user_input for word in ['吗', '呢', '如何', '怎样']):
            if len(context_keywords) > 0:  # 已有上下文
                return CreativeStage.DIVERGE

        # 检测是否有具体场景描述（聚焦）
        if self._has_concrete_scenario(user_input):
            if turn_number <= 3:
                return CreativeStage.FOCUS
            else:
                # 后期的具体化可能是收束
                return CreativeStage.CONVERGE

        # 检测是否在做选择（收束）
        if any(word in user_input for word in ['就', '确定', '选', '决定', '要这个']):
            return CreativeStage.CONVERGE

        # 检测是否在讨论执行（整理）
        if any(word in user_input for word in ['怎么拍', '脚本', '执行', '具体步骤']):
            return CreativeStage.ORGANIZE

        # 默认：根据轮数推断
        if turn_number <= 2:
            return CreativeStage.CLARIFY
        elif turn_number <= 4:
            return CreativeStage.FOCUS
        elif turn_number <= 6:
            return CreativeStage.DIVERGE
        else:
            return CreativeStage.CONVERGE

    def _has_concrete_scenario(self, text: str) -> bool:
        """检测是否包含具体场景描述"""
        concrete_markers = [
            '场景', '镜头', '画面', '地点', '房间', '街道',
            '人物', '角色', '主角', '配角',
            '开头', '结尾', '中间', '第一个', '最后',
            '分钟', '秒', '时长'
        ]
        return any(marker in text for marker in concrete_markers)


class GuidingQuestionGenerator:
    """
    引导性问题生成器

    基于当前阶段和创作者状态，生成引导性问题
    """

    def __init__(self):
        # 预定义的问题模板（按阶段分类）
        self.question_templates = self._init_templates()

    def _init_templates(self) -> Dict[CreativeStage, List[Dict[str, str]]]:
        """初始化问题模板"""
        return {
            # 明确阶段：递进式问题链（现象→情感→价值→哲学）
            CreativeStage.CLARIFY: [
                {
                    'layer': 'phenomenon',
                    'questions': [
                        "最近什么让你印象深刻？",
                        "能描述一个具体的时刻吗？",
                        "什么触动了你想要创作的念头？"
                    ],
                    'purpose': '引导用户回忆具体经验'
                },
                {
                    'layer': 'emotion',
                    'questions': [
                        "那个时刻的感觉是什么？",
                        "这种感觉是愉悦的、痛苦的，还是复杂的？",
                        "这种情绪有多强烈？"
                    ],
                    'purpose': '识别情感基调'
                },
                {
                    'layer': 'value',
                    'questions': [
                        "为什么这个时刻对你重要？",
                        "你希望通过电影传达什么？",
                        "你想让观众感受到什么？"
                    ],
                    'purpose': '提取价值判断'
                },
                {
                    'layer': 'philosophy',
                    'questions': [
                        "这触及了什么根本性的问题？",
                        "这与你对世界/人性的理解有什么关系？",
                        "如果用一个词概括这种张力，会是什么？"
                    ],
                    'purpose': '揭示哲学内核'
                }
            ],

            # 聚焦阶段：锚定问题（抽象→具体）
            CreativeStage.FOCUS: [
                {
                    'category': 'scenario',
                    'questions': [
                        "如果只能拍一个场景来体现这个想法，会是什么？",
                        "这个场景发生在什么空间？室内还是室外？",
                        "这个场景的持续时间是多久？"
                    ],
                    'purpose': '将抽象内核锚定到具体场景'
                },
                {
                    'category': 'character',
                    'questions': [
                        "画面里有几个人物？",
                        "他们在做什么？",
                        "他们之间是什么关系？"
                    ],
                    'purpose': '明确人物和行动'
                },
                {
                    'category': 'visual',
                    'questions': [
                        "用什么样的镜头？固定还是运动？",
                        "焦点在哪里？前景还是背景？",
                        "光线是什么感觉？"
                    ],
                    'purpose': '初步视觉策略'
                }
            ],

            # 发散阶段："如果...会怎样"
            CreativeStage.DIVERGE: [
                {
                    'dimension': 'time',
                    'questions': [
                        "如果时长压缩到30秒会怎样？",
                        "如果扩展到10分钟会怎样？",
                        "如果用慢动作会怎样？"
                    ],
                    'purpose': '探索时间维度的变体'
                },
                {
                    'dimension': 'viewpoint',
                    'questions': [
                        "如果从天花板俯拍会怎样？",
                        "如果贴近某个人的视角会怎样？",
                        "如果用第一人称主观镜头会怎样？"
                    ],
                    'purpose': '探索视点的可能性'
                },
                {
                    'dimension': 'sound',
                    'questions': [
                        "如果完全没有声音会怎样？",
                        "如果放大某个细微声音会怎样？",
                        "如果加入音乐会怎样？什么风格的？"
                    ],
                    'purpose': '探索声音设计'
                },
                {
                    'dimension': 'moment',
                    'questions': [
                        "如果拍清晨会怎样？",
                        "如果拍深夜会怎样？",
                        "如果拍季节转换会怎样？"
                    ],
                    'purpose': '探索时刻选择'
                }
            ],

            # 收束阶段：评估和深化
            CreativeStage.CONVERGE: [
                {
                    'category': 'evaluation',
                    'questions': [
                        "这个方案最打动你的是什么？",
                        "它和你最初的想法契合吗？",
                        "还有什么让你不确定的地方？"
                    ],
                    'purpose': '评估方案与内核的契合度'
                },
                {
                    'category': 'detail',
                    'questions': [
                        "能再具体描述一下XX吗？",
                        "这段时间里，画面有哪些变化？",
                        "开头和结尾分别是什么？"
                    ],
                    'purpose': '填充细节'
                },
                {
                    'category': 'consistency',
                    'questions': [
                        "XX和YY会不会产生矛盾？",
                        "这个选择是有意为之，还是需要调整？",
                        "如果删掉XX，会失去什么？"
                    ],
                    'purpose': '检验一致性'
                }
            ],

            # 整理阶段：执行性问题
            CreativeStage.ORGANIZE: [
                {
                    'category': 'execution',
                    'questions': [
                        "需要我生成分镜头脚本吗？",
                        "需要补充哪些技术规格？",
                        "这个场景还有其他部分需要设计吗？"
                    ],
                    'purpose': '准备可执行文档'
                },
                {
                    'category': 'next_step',
                    'questions': [
                        "如果还有其他场景，要继续探讨吗？",
                        "想深化这个场景的某个细节吗？",
                        "还是已经可以进入拍摄了？"
                    ],
                    'purpose': '确认下一步行动'
                }
            ]
        }

    def generate_questions(
        self,
        stage: CreativeStage,
        creator_state: CreatorState,
        turn_number: int
    ) -> List[GuidingQuestion]:
        """
        生成该阶段的引导性问题

        Args:
            stage: 当前阶段
            creator_state: 创作者状态
            turn_number: 对话轮数

        Returns:
            生成的引导性问题列表（优先级排序）
        """

        questions = []
        templates = self.question_templates.get(stage, [])

        if stage == CreativeStage.CLARIFY:
            # 明确阶段：递进式提问
            questions = self._generate_clarify_questions(templates, creator_state, turn_number)

        elif stage == CreativeStage.FOCUS:
            # 聚焦阶段：锚定问题
            questions = self._generate_focus_questions(templates, creator_state)

        elif stage == CreativeStage.DIVERGE:
            # 发散阶段："如果...会怎样"
            questions = self._generate_diverge_questions(templates, creator_state)

        elif stage == CreativeStage.CONVERGE:
            # 收束阶段：评估和深化
            questions = self._generate_converge_questions(templates, creator_state)

        elif stage == CreativeStage.ORGANIZE:
            # 整理阶段：执行性问题
            questions = self._generate_organize_questions(templates, creator_state)

        # 按优先级排序
        questions.sort(key=lambda q: q.priority, reverse=True)

        return questions[:3]  # 最多返回3个问题

    def _generate_clarify_questions(
        self,
        templates: List[Dict],
        state: CreatorState,
        turn: int
    ) -> List[GuidingQuestion]:
        """生成明确阶段的问题（递进式）"""
        questions = []

        # 根据轮数选择层次
        if turn == 1:
            # 第一轮：现象层
            layer = templates[0]
            for q in layer['questions'][:1]:  # 只取第一个
                questions.append(GuidingQuestion(
                    question=q,
                    purpose=layer['purpose'],
                    stage=CreativeStage.CLARIFY,
                    priority=1.0
                ))
        elif turn == 2:
            # 第二轮：情感层
            layer = templates[1]
            for q in layer['questions'][:1]:
                questions.append(GuidingQuestion(
                    question=q,
                    purpose=layer['purpose'],
                    stage=CreativeStage.CLARIFY,
                    priority=0.9
                ))
        elif turn == 3:
            # 第三轮：价值层
            layer = templates[2]
            for q in layer['questions'][:1]:
                questions.append(GuidingQuestion(
                    question=q,
                    purpose=layer['purpose'],
                    stage=CreativeStage.CLARIFY,
                    priority=0.8
                ))
        else:
            # 第四轮+：哲学层
            layer = templates[3]
            for q in layer['questions'][:1]:
                questions.append(GuidingQuestion(
                    question=q,
                    purpose=layer['purpose'],
                    stage=CreativeStage.CLARIFY,
                    priority=0.7
                ))

        return questions

    def _generate_focus_questions(
        self,
        templates: List[Dict],
        state: CreatorState
    ) -> List[GuidingQuestion]:
        """生成聚焦阶段的问题（锚定）"""
        questions = []

        # 场景锚定（优先级最高）
        scenario_template = templates[0]
        questions.append(GuidingQuestion(
            question=scenario_template['questions'][0],
            purpose=scenario_template['purpose'],
            stage=CreativeStage.FOCUS,
            priority=1.0
        ))

        # 人物和视觉（次优先）
        if len(templates) > 1:
            char_template = templates[1]
            questions.append(GuidingQuestion(
                question=char_template['questions'][0],
                purpose=char_template['purpose'],
                stage=CreativeStage.FOCUS,
                priority=0.8
            ))

        return questions

    def _generate_diverge_questions(
        self,
        templates: List[Dict],
        state: CreatorState
    ) -> List[GuidingQuestion]:
        """生成发散阶段的问题（探索变体）"""
        questions = []

        # 从不同维度选择问题
        for template in templates[:2]:  # 选2个维度
            questions.append(GuidingQuestion(
                question=template['questions'][0],
                purpose=template['purpose'],
                stage=CreativeStage.DIVERGE,
                priority=0.8
            ))

        return questions

    def _generate_converge_questions(
        self,
        templates: List[Dict],
        state: CreatorState
    ) -> List[GuidingQuestion]:
        """生成收束阶段的问题（评估和深化）"""
        questions = []

        # 先评估
        if templates:
            eval_template = templates[0]
            questions.append(GuidingQuestion(
                question=eval_template['questions'][0],
                purpose=eval_template['purpose'],
                stage=CreativeStage.CONVERGE,
                priority=1.0
            ))

        return questions

    def _generate_organize_questions(
        self,
        templates: List[Dict],
        state: CreatorState
    ) -> List[GuidingQuestion]:
        """生成整理阶段的问题（执行）"""
        questions = []

        if templates:
            exec_template = templates[0]
            questions.append(GuidingQuestion(
                question=exec_template['questions'][0],
                purpose=exec_template['purpose'],
                stage=CreativeStage.ORGANIZE,
                priority=1.0
            ))

        return questions


# 全局单例
_detector_instance = None
_generator_instance = None

def get_stage_detector() -> StageDetector:
    """获取五阶段检测器实例"""
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = StageDetector()
    return _detector_instance

def get_question_generator() -> GuidingQuestionGenerator:
    """获取问题生成器实例"""
    global _generator_instance
    if _generator_instance is None:
        _generator_instance = GuidingQuestionGenerator()
    return _generator_instance
