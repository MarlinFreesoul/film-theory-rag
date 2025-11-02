"""
Visualization Generator - 视觉化文本生成器

基于论文02的"多媒体催化"理论实现
核心功能：把抽象张力转化为可感知的视觉化场景描述

设计原则（来自论文）：
- 感知先行：激活感官，而非概念
- 张力对应：视觉元素体现同构的张力
- 简约性：单一焦点，避免信息过载
- 时间性：持续时间本身是信息
- 未完成性：留下阐释空间
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import anthropic
import os


@dataclass
class VisualScene:
    """视觉化场景"""
    title: str  # 场景标题（简短）
    visual: str  # 画面描述
    sound: str  # 声音描述
    duration: str  # 持续时间
    purpose: str  # 激发目的（为什么这个场景能激发创意）
    tension: str  # 对应的张力


class VisualizationGenerator:
    """
    视觉化文本生成器

    功能：
    1. 接收用户的关键词和状态
    2. 结合知识库的理论和作品
    3. 生成可感知的视觉化场景描述

    不是：
    - 不是返回理论文字
    - 不是生成完整剧本
    - 不是预设流程

    而是：
    - 生成可以"看到""听到"的具体描述
    - 激活用户的感知-情感通路
    - 等待用户的创意涌现
    """

    def __init__(self):
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")

        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-3-5-haiku-20241022"

        print("[VisualizationGenerator] Initialized with Claude Haiku")

    def generate_visual_scenes(
        self,
        user_input: str,
        keywords: List[str],
        stage: str,
        inspirations: List[Dict[str, Any]] = None
    ) -> List[VisualScene]:
        """
        生成视觉化场景描述

        Args:
            user_input: 用户输入的原始文本
            keywords: 提取的关键词（张力、主题等）
            stage: 当前创作阶段
            inspirations: 知识库检索到的激发内容（理论+作品）

        Returns:
            视觉化场景列表（2-3个）
        """

        # 构建prompt（基于论文的多媒体激发原则）
        prompt = self._build_prompt(user_input, keywords, stage, inspirations)

        # 调用Claude生成
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.8,  # 适当提高创造性
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            response_text = message.content[0].text

            # 解析返回的场景
            scenes = self._parse_scenes(response_text, keywords)

            print(f"[VisualizationGenerator] Generated {len(scenes)} visual scenes")
            return scenes

        except Exception as e:
            print(f"[VisualizationGenerator] Error: {e}")
            return []

    def _build_prompt(
        self,
        user_input: str,
        keywords: List[str],
        stage: str,
        inspirations: List[Dict[str, Any]]
    ) -> str:
        """构建生成视觉化场景的prompt"""

        # 提取知识库内容作为参考
        theory_refs = []
        work_refs = []

        if inspirations:
            for insp in inspirations[:3]:  # 只用前3个最相关的
                if insp.get('type') == 'theory':
                    theory_refs.append(f"- {insp.get('title')}: {insp.get('content', '')[:100]}")
                elif insp.get('type') == 'work':
                    work_refs.append(f"- {insp.get('title')}: {insp.get('content', '')[:100]}")

        theory_context = "\n".join(theory_refs) if theory_refs else "无"
        work_context = "\n".join(work_refs) if work_refs else "无"

        prompt = f"""你是一个电影创作的视觉化助手。你的任务是把用户的抽象想法转化为可以"看到""听到"的具体场景描述。

**核心原则**（来自认知共振理论）：
- 感知先行：直接描述视觉和听觉，不要解释概念
- 张力对应：场景要体现用户想法中的内在张力
- 简约性：单一焦点，避免复杂
- 时间性：明确持续时间（5-30秒）
- 未完成性：留下想象空间，不要给完整答案

**用户输入**：
{user_input}

**识别的关键词**：
{', '.join(keywords)}

**当前创作阶段**：
{stage}

**相关理论参考**：
{theory_context}

**相关作品参考**：
{work_context}

**你的任务**：
生成2-3个视觉化场景描述，每个场景包含：

1. **标题**：3-5个字的简短标题
2. **画面**：详细的视觉描述（镜头、主体、背景、光线、运动）
3. **声音**：声音设计（环境音、音效、音乐）
4. **时长**：具体的持续时间（如"15秒""1分钟"）
5. **激发目的**：这个场景为什么能激发用户的创意（1句话）
6. **对应张力**：这个场景体现了什么张力（如"瞬间↔永恒""记忆↔遗忘"）

**重要**：
- 不要解释理论，而是用视觉元素体现理论
- 不要生成完整剧本，而是生成单个可感知的"片段"
- 每个场景都应该是独立的、具体的、可以直接想象的

**输出格式**（严格按此格式）：

---场景1---
标题：[3-5字]
画面：[详细描述]
声音：[声音设计]
时长：[具体时间]
激发目的：[1句话]
对应张力：[张力描述]

---场景2---
...

请生成2-3个场景。
"""

        return prompt

    def _parse_scenes(self, response_text: str, keywords: List[str]) -> List[VisualScene]:
        """解析Claude返回的场景描述"""

        scenes = []

        # 按场景分割
        scene_blocks = response_text.split('---场景')

        for block in scene_blocks[1:]:  # 跳过第一个空块
            try:
                lines = [line.strip() for line in block.split('\n') if line.strip()]

                # 解析各个字段
                scene_data = {}
                for line in lines:
                    if line.startswith('标题：'):
                        scene_data['title'] = line.replace('标题：', '').strip()
                    elif line.startswith('画面：'):
                        scene_data['visual'] = line.replace('画面：', '').strip()
                    elif line.startswith('声音：'):
                        scene_data['sound'] = line.replace('声音：', '').strip()
                    elif line.startswith('时长：'):
                        scene_data['duration'] = line.replace('时长：', '').strip()
                    elif line.startswith('激发目的：'):
                        scene_data['purpose'] = line.replace('激发目的：', '').strip()
                    elif line.startswith('对应张力：'):
                        scene_data['tension'] = line.replace('对应张力：', '').strip()

                # 创建场景对象
                if all(k in scene_data for k in ['title', 'visual', 'sound', 'duration', 'purpose', 'tension']):
                    scene = VisualScene(
                        title=scene_data['title'],
                        visual=scene_data['visual'],
                        sound=scene_data['sound'],
                        duration=scene_data['duration'],
                        purpose=scene_data['purpose'],
                        tension=scene_data['tension']
                    )
                    scenes.append(scene)

            except Exception as e:
                print(f"[VisualizationGenerator] Failed to parse scene: {e}")
                continue

        return scenes
