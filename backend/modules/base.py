"""
Knowledge Module Base - 知识模块基类

设计理念：
- 所有知识模块继承此基类
- 依赖倒置：模块依赖EventBus抽象，不依赖具体实现
- 模块独立响应状态变化事件
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class Inspiration:
    """
    激发内容

    Attributes:
        type: 类型（theory/work/director）
        title: 标题
        content: 内容
        relevance_score: 相关度分数（0-1）
        source: 来源
        metadata: 元数据
    """
    type: str
    title: str
    content: str
    relevance_score: float
    source: str
    metadata: Dict[str, Any] = None

    def to_dict(self):
        """转换为字典"""
        return {
            'type': self.type,
            'title': self.title,
            'content': self.content,
            'relevance_score': self.relevance_score,
            'source': self.source,
            'metadata': self.metadata
        }


class KnowledgeModule(ABC):
    """
    知识模块基类

    所有知识模块（理论库、作品库、导演库）继承此类
    """

    def __init__(self, event_bus, knowledge_base, module_name: str):
        self.event_bus = event_bus
        self.knowledge_base = knowledge_base
        self.module_name = module_name

        # 订阅状态变化事件
        self.event_bus.subscribe('state_changed', self.on_state_changed)

        print(f"[{self.module_name}] Module initialized")

    @abstractmethod
    def on_state_changed(self, event):
        """
        响应状态变化事件

        子类必须实现此方法
        """
        pass

    @abstractmethod
    def search(self, keywords: List[str], state) -> List[Inspiration]:
        """
        搜索相关内容

        Args:
            keywords: 关键词列表
            state: 创作者状态

        Returns:
            inspirations: 激发内容列表
        """
        pass

    def _calculate_relevance(self, item: Dict, keywords: List[str]) -> float:
        """
        计算相关度（简单版本）

        MVP实现：基于关键词匹配计分
        """
        score = 0.0
        item_text = str(item).lower()

        for keyword in keywords:
            if keyword.lower() in item_text:
                score += 0.3

        return min(score, 1.0)

    def publish_inspiration(self, inspirations: List[Inspiration]):
        """发布激发内容"""
        if inspirations:
            self.event_bus.publish(
                event_type='inspiration_found',
                data={
                    'inspirations': [insp.to_dict() for insp in inspirations],
                    'module': self.module_name
                },
                source=self.module_name
            )

            print(f"[{self.module_name}] Published {len(inspirations)} inspirations")
