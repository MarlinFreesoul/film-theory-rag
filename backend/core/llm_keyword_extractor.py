"""
LLM Keyword Extractor - 基于LLM的语义关键词提取

功能：
- 使用Claude Haiku提取电影创作相关的关键词
- 理解用户的自然语言表达
- 支持上下文融合
"""

import os
from typing import List
import anthropic
from .usage_tracker import get_tracker


class LLMKeywordExtractor:
    """LLM驱动的关键词提取器"""

    def __init__(self, api_key: str = None):
        """
        初始化提取器

        Args:
            api_key: Anthropic API密钥，如果不提供则从环境变量读取
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')

        if not self.api_key:
            print("[LLMKeywordExtractor] Warning: No API key provided, will use fallback")
            self.client = None
        else:
            self.client = anthropic.Anthropic(api_key=self.api_key)
            print("[LLMKeywordExtractor] Initialized with Claude Haiku")

    def extract_keywords(self, user_input: str, context_keywords: List[str] = None) -> List[str]:
        """
        从用户输入中提取语义关键词

        Args:
            user_input: 用户输入的文本
            context_keywords: 上下文已有的关键词

        Returns:
            提取到的关键词列表
        """
        if not self.client:
            # 降级：使用简单的规则提取
            return self._fallback_extract(user_input)

        try:
            context_keywords = context_keywords or []

            # 构建提示词
            prompt = self._build_prompt(user_input, context_keywords)

            # 调用Claude Haiku
            message = self.client.messages.create(
                model="claude-3-haiku-20240307",  # 最便宜最快的模型
                max_tokens=200,  # 只需要关键词，不需要长文本
                temperature=0.3,  # 低温度，保持稳定
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # 记录用量
            usage = message.usage
            tracker = get_tracker()
            tracker.record(
                model="claude-3-haiku-20240307",
                input_tokens=usage.input_tokens,
                output_tokens=usage.output_tokens,
                purpose="keyword_extraction"
            )

            # 解析响应
            response_text = message.content[0].text.strip()
            keywords = self._parse_keywords(response_text)

            print(f"[LLMKeywordExtractor] Extracted: {keywords}")
            return keywords

        except Exception as e:
            print(f"[LLMKeywordExtractor] Error: {e}, using fallback")
            return self._fallback_extract(user_input)

    def _build_prompt(self, user_input: str, context_keywords: List[str]) -> str:
        """构建提示词"""

        context_part = ""
        if context_keywords:
            context_part = f"\n上下文已有关键词：{', '.join(context_keywords)}"

        prompt = f"""你是电影创作助手，从用户输入中提取电影创作相关的关键词。

用户输入：{user_input}{context_part}

请从以下维度提取关键词：
1. 主题：记忆、时间、孤独、爱情、死亡、童年、战争、家庭等
2. 情绪：忧郁、怀旧、恐惧、喜悦、悲伤、紧张等
3. 风格：现代、古典、未来、乡土、城市、自然等
4. 技法：长镜头、蒙太奇、固定镜头、跟拍、特写等
5. 视觉：色彩、光线、构图、景别等

只返回关键词，用逗号分隔，不要解释。如果用户在细化之前的想法，要保留上下文关键词。

示例：
用户："我在构思一个关于记忆消逝的场景" → 记忆,时间,消逝
用户："我想要更现代的感觉" (上下文:记忆) → 记忆,现代,城市,当代
用户："色彩上该怎么处理？" (上下文:记忆,现代) → 记忆,现代,色彩,配色
"""

        return prompt

    def _parse_keywords(self, response_text: str) -> List[str]:
        """解析LLM返回的关键词"""
        # 移除可能的前缀
        response_text = response_text.replace('关键词：', '').replace('Keywords:', '')

        # 分割并清理
        keywords = [kw.strip() for kw in response_text.split(',')]
        keywords = [kw for kw in keywords if kw and len(kw) > 0]

        # 去重但保持顺序
        seen = set()
        unique_keywords = []
        for kw in keywords:
            if kw not in seen:
                seen.add(kw)
                unique_keywords.append(kw)

        return unique_keywords[:5]  # 最多返回5个关键词

    def _fallback_extract(self, user_input: str) -> List[str]:
        """降级方案：简单的规则提取"""
        # 简单的关键词列表（兜底方案）
        keyword_candidates = [
            # 主题词
            '记忆', '时间', '孤独', '爱情', '死亡', '童年', '战争', '家庭',
            # 情绪词
            '忧郁', '怀旧', '恐惧', '喜悦', '悲伤', '孤独',
            # 风格词
            '现代', '古典', '未来', '乡土', '城市', '自然',
            # 技法词
            '长镜头', '蒙太奇', '固定镜头', '跟拍',
            # 视觉词
            '色彩', '光线', '构图', '景别'
        ]

        keywords = []
        for kw in keyword_candidates:
            if kw in user_input:
                keywords.append(kw)

        return keywords if keywords else ['记忆']  # 至少返回一个


# 全局单例（可选，减少重复初始化）
_extractor_instance = None

def get_extractor(api_key: str = None) -> LLMKeywordExtractor:
    """获取全局提取器实例"""
    global _extractor_instance
    if _extractor_instance is None:
        _extractor_instance = LLMKeywordExtractor(api_key=api_key)
    return _extractor_instance
