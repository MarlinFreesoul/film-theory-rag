"""
Work Module - 作品记忆库模块

功能：
- 响应状态变化事件
- 基于关键词检索相关作品片段
- 发布作品激发内容
"""

import yaml
from typing import List
from .base import KnowledgeModule, Inspiration


class WorkModule(KnowledgeModule):
    """作品记忆库模块"""

    def __init__(self, event_bus, yaml_path: str):
        # 加载作品库
        with open(yaml_path, 'r', encoding='utf-8') as f:
            knowledge_base = yaml.safe_load(f)

        super().__init__(event_bus, knowledge_base, 'WorkModule')

    def on_state_changed(self, event):
        """响应状态变化事件"""
        current_state = event.data.get('current')

        if not current_state:
            return

        keywords = current_state.get('keywords', [])

        if not keywords:
            print(f"[{self.module_name}] No keywords, skipping")
            return

        # 搜索相关作品
        inspirations = self.search(keywords, current_state)

        # 发布激发内容
        if inspirations:
            self.publish_inspiration(inspirations)

    def search(self, keywords: List[str], state) -> List[Inspiration]:
        """搜索作品库"""
        results = []

        # 遍历导演和作品
        for director_data in self.knowledge_base.get('directors', []):
            director = director_data.get('name', '')
            core_tension = director_data.get('core_tension', '')

            for work in director_data.get('works', []):
                relevance = self._calculate_relevance(work, keywords)

                if relevance > 0.2:  # 相关度阈值
                    # 构建内容：描述 + 可执行建议
                    content_parts = [work.get('scene_description', '')]

                    # 添加可执行建议
                    actionable_tips = work.get('actionable_tips', [])
                    if actionable_tips:
                        content_parts.append('\n\n【如何拍摄】')
                        for tip in actionable_tips:
                            content_parts.append(f'• {tip}')

                    # 添加适用场景
                    when_to_use = work.get('when_to_use', [])
                    if when_to_use:
                        content_parts.append('\n\n【适用于】')
                        for scenario in when_to_use:
                            content_parts.append(f'✓ {scenario}')

                    results.append(Inspiration(
                        type='work',
                        title=f"{director} - {work.get('title', '')} ({work.get('year', '')})",
                        content='\n'.join(content_parts),
                        relevance_score=relevance,
                        source='work_database',
                        metadata={
                            'director': director,
                            'core_tension': core_tension,
                            'theme': work.get('theme'),
                            'keywords': work.get('keywords', []),
                            'structure_analysis': work.get('structure_analysis', {}),
                            'actionable_tips': actionable_tips,
                            'when_to_use': when_to_use,
                            'avoid_when': work.get('avoid_when', [])
                        }
                    ))

        # 按相关度排序
        results.sort(key=lambda x: x.relevance_score, reverse=True)

        return results[:3]  # 最多返回3个
