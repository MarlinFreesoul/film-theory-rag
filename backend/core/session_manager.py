"""
Session Manager - 对话会话管理器

功能：
- 管理多轮对话上下文
- 累积用户意图和关键词
- 跟踪创作状态演化
"""

import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class ConversationTurn:
    """单轮对话"""
    turn_number: int
    user_input: str
    keywords: List[str]
    stage: str
    inspirations_count: int
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ConversationContext:
    """对话上下文"""
    session_id: str
    turns: List[ConversationTurn] = field(default_factory=list)
    accumulated_keywords: set = field(default_factory=set)
    dimension_focus: Optional[str] = None  # 当前聚焦维度
    created_at: datetime = field(default_factory=datetime.now)

    def add_turn(self, user_input: str, keywords: List[str], stage: str, inspirations_count: int):
        """添加一轮对话"""
        turn = ConversationTurn(
            turn_number=len(self.turns) + 1,
            user_input=user_input,
            keywords=keywords,
            stage=stage,
            inspirations_count=inspirations_count
        )
        self.turns.append(turn)

        # 累积关键词
        for kw in keywords:
            self.accumulated_keywords.add(kw)

    def get_context_keywords(self) -> List[str]:
        """获取上下文关键词（带权重的）"""
        # 简单策略：最近的轮次权重更高
        if not self.turns:
            return []

        # 取最近3轮的关键词
        recent_turns = self.turns[-3:]
        keywords = []
        for turn in recent_turns:
            keywords.extend(turn.keywords)

        return keywords

    def is_first_turn(self) -> bool:
        """是否是第一轮"""
        return len(self.turns) == 0

    def get_summary(self) -> Dict[str, Any]:
        """获取会话摘要"""
        return {
            'session_id': self.session_id,
            'turn_count': len(self.turns),
            'accumulated_keywords': list(self.accumulated_keywords),
            'dimension_focus': self.dimension_focus,
            'created_at': self.created_at.isoformat(),
            'latest_stage': self.turns[-1].stage if self.turns else None
        }


class SessionManager:
    """会话管理器（内存版本）"""

    def __init__(self):
        self._sessions: Dict[str, ConversationContext] = {}
        print("[SessionManager] Initialized (in-memory mode)")

    def create_session(self) -> str:
        """创建新会话"""
        session_id = str(uuid.uuid4())
        context = ConversationContext(session_id=session_id)
        self._sessions[session_id] = context
        print(f"[SessionManager] Created session: {session_id}")
        return session_id

    def get_session(self, session_id: str) -> Optional[ConversationContext]:
        """获取会话上下文"""
        return self._sessions.get(session_id)

    def add_turn(self, session_id: str, user_input: str, keywords: List[str],
                 stage: str, inspirations_count: int):
        """添加对话轮次"""
        context = self.get_session(session_id)
        if not context:
            print(f"[SessionManager] Session not found: {session_id}")
            return

        context.add_turn(user_input, keywords, stage, inspirations_count)
        print(f"[SessionManager] Added turn {len(context.turns)} to session {session_id}")

    def get_context_keywords(self, session_id: str) -> List[str]:
        """获取上下文关键词"""
        context = self.get_session(session_id)
        if not context:
            return []
        return context.get_context_keywords()

    def is_first_turn(self, session_id: str) -> bool:
        """判断是否是第一轮"""
        context = self.get_session(session_id)
        if not context:
            return True
        return context.is_first_turn()

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            'total_sessions': len(self._sessions),
            'active_sessions': len([s for s in self._sessions.values() if len(s.turns) > 0])
        }

    def cleanup_old_sessions(self, max_age_hours: int = 24):
        """清理过期会话（简单实现）"""
        now = datetime.now()
        to_delete = []

        for session_id, context in self._sessions.items():
            age = (now - context.created_at).total_seconds() / 3600
            if age > max_age_hours:
                to_delete.append(session_id)

        for session_id in to_delete:
            del self._sessions[session_id]

        if to_delete:
            print(f"[SessionManager] Cleaned up {len(to_delete)} old sessions")
