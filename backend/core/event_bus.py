"""
Event Bus - 轻量级事件总线

核心设计理念：
- 发布-订阅模式实现模块解耦
- 依赖倒置：所有模块依赖抽象（EventBus），而非具体实现
- 事件历史：保留事件记录，便于调试和分析
"""

from typing import Callable, Dict, List, Any
from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class Event:
    """事件对象"""
    id: str
    type: str
    data: Dict[str, Any]
    timestamp: datetime
    source: str = None

    def __repr__(self):
        return f"Event(type={self.type}, source={self.source}, id={self.id[:8]}...)"


class EventBus:
    """
    轻量级事件总线

    使用方式:
        # 创建事件总线
        bus = EventBus()

        # 订阅事件
        def handler(event):
            print(f"Received: {event.type}")

        bus.subscribe('user_input', handler)

        # 发布事件
        bus.publish('user_input', {'content': 'hello'})
    """

    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._event_history: List[Event] = []
        self._max_history = 100  # 最多保留100个事件

    def subscribe(self, event_type: str, handler: Callable) -> None:
        """
        订阅事件

        Args:
            event_type: 事件类型
            handler: 回调函数，接收 Event 对象作为参数
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []

        if handler not in self._subscribers[event_type]:
            self._subscribers[event_type].append(handler)
            print(f"[EventBus] Subscribed {handler.__name__} to '{event_type}'")

    def unsubscribe(self, event_type: str, handler: Callable) -> None:
        """取消订阅"""
        if event_type in self._subscribers:
            if handler in self._subscribers[event_type]:
                self._subscribers[event_type].remove(handler)
                print(f"[EventBus] Unsubscribed {handler.__name__} from '{event_type}'")

    def publish(self, event_type: str, data: Dict[str, Any], source: str = None) -> str:
        """
        发布事件

        Args:
            event_type: 事件类型
            data: 事件数据
            source: 事件来源（可选）

        Returns:
            event_id: 事件唯一ID
        """
        # 创建事件对象
        event = Event(
            id=str(uuid.uuid4()),
            type=event_type,
            data=data,
            timestamp=datetime.now(),
            source=source
        )

        # 保存到历史
        self._event_history.append(event)

        # 限制历史大小
        if len(self._event_history) > self._max_history:
            self._event_history = self._event_history[-self._max_history:]

        # 通知所有订阅者
        if event_type in self._subscribers:
            print(f"[EventBus] Publishing '{event_type}' to {len(self._subscribers[event_type])} subscribers")

            for handler in self._subscribers[event_type]:
                try:
                    handler(event)
                except Exception as e:
                    print(f"[EventBus] Error in handler {handler.__name__}: {e}")
        else:
            print(f"[EventBus] No subscribers for '{event_type}'")

        return event.id

    def get_history(self, event_type: str = None, limit: int = 10) -> List[Event]:
        """
        获取事件历史

        Args:
            event_type: 事件类型过滤（可选）
            limit: 返回数量限制

        Returns:
            events: 事件列表（最新的在前）
        """
        if event_type:
            events = [e for e in self._event_history if e.type == event_type]
        else:
            events = self._event_history

        # 返回最新的N个事件
        return list(reversed(events[-limit:]))

    def clear_history(self) -> None:
        """清空事件历史"""
        self._event_history.clear()
        print("[EventBus] History cleared")

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            'total_events': len(self._event_history),
            'event_types': list(self._subscribers.keys()),
            'subscriber_count': {
                event_type: len(handlers)
                for event_type, handlers in self._subscribers.items()
            }
        }
