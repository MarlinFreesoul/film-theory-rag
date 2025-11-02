"""
Theory Module - 理论状态库模块

功能：
- 响应状态变化事件
- 基于关键词检索相关理论
- 发布理论激发内容
"""

import yaml
from typing import List
from pathlib import Path
from .base import KnowledgeModule, Inspiration


class TheoryModule(KnowledgeModule):
    """理论状态库模块"""

    def __init__(self, event_bus, yaml_path: str):
        # 加载理论库
        with open(yaml_path, 'r', encoding='utf-8') as f:
            knowledge_base = yaml.safe_load(f)

        super().__init__(event_bus, knowledge_base, 'TheoryModule')

    def on_state_changed(self, event):
        """响应状态变化事件"""
        current_state = event.data.get('current')

        if not current_state:
            return

        keywords = current_state.get('keywords', [])

        if not keywords:
            print(f"[{self.module_name}] No keywords, skipping")
            return

        # 搜索相关理论
        inspirations = self.search(keywords, current_state)

        # 发布激发内容
        if inspirations:
            self.publish_inspiration(inspirations)

    def search(self, keywords: List[str], state) -> List[Inspiration]:
        """搜索理论库"""
        results = []

        # 遍历理论库
        for theory in self.knowledge_base.get('theories', []):
            relevance = self._calculate_relevance(theory, keywords)

            if relevance > 0.2:  # 相关度阈值
                # 构建内容：描述 + 应用指导
                content_parts = [theory.get('description', '')]

                # 添加应用指导
                how_to_apply = theory.get('how_to_apply', [])
                if how_to_apply:
                    content_parts.append('\n\n【如何应用】')
                    for item in how_to_apply:
                        content_parts.append(f"\n▸ {item.get('title', '')}")
                        content_parts.append(f"  {item.get('tip', '')}")
                        if 'example' in item:
                            content_parts.append(f"  例如：{item.get('example', '')}")

                # 添加适用场景
                when_to_use = theory.get('when_to_use', [])
                if when_to_use:
                    content_parts.append('\n\n【适用于】')
                    for scenario in when_to_use:
                        content_parts.append(f'✓ {scenario}')

                # 添加常见误区
                common_mistakes = theory.get('common_mistakes', [])
                if common_mistakes:
                    content_parts.append('\n\n【避免误区】')
                    for mistake in common_mistakes:
                        content_parts.append(f'⚠ {mistake}')

                results.append(Inspiration(
                    type='theory',
                    title=theory.get('name', ''),
                    content='\n'.join(content_parts),
                    relevance_score=relevance,
                    source='theory_database',
                    metadata={
                        'category': theory.get('category'),
                        'keywords': theory.get('keywords', []),
                        'related_directors': theory.get('related_directors', []),
                        'how_to_apply': how_to_apply,
                        'when_to_use': when_to_use,
                        'common_mistakes': common_mistakes
                    }
                ))

        # 按相关度排序
        results.sort(key=lambda x: x.relevance_score, reverse=True)

        return results[:3]  # 最多返回3个
