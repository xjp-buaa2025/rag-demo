"""
backend/langchain_components/memory.py — Memory 组件

管理对话历史和上下文信息，确保多轮对话的连贯性。

核心类：
  ChatMemoryManager — 管理多会话的对话历史

与现有代码的关系：
  - 替换 chat.py:167 的 `for item in history[-12:]` 手写滑窗
  - 替换 assembly.py:84 的 `for item in history[-8:]`
  - 前端不需要改动，仍然发送完整 history 数组
  - 后端通过 history_to_messages() 将前端格式转为 LangChain messages

两种策略：
  策略 A（当前使用）：前端发完整 history，后端转换注入 Prompt
  策略 B（未来扩展）：服务端维护 session_id -> Memory 映射
"""

import threading
from collections import OrderedDict
from typing import Any, List, Optional

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage


class ChatMemoryManager:
    """
    管理多个对话会话的 Memory。

    当前阶段：
      前端仍发送完整 history，后端通过 history_to_messages() 转换，
      注入 LangChain ChatPromptTemplate 的 MessagesPlaceholder。

    未来扩展：
      可启用 session_id -> InMemoryHistory 映射，实现服务端记忆。
    """

    def __init__(self, max_sessions: int = 100, window_k: int = 6):
        """
        Args:
            max_sessions: 最大缓存会话数（LRU 淘汰）
            window_k: 保留最近 k 轮对话（即 2*k 条消息）
        """
        self._sessions: OrderedDict[str, InMemoryHistory] = OrderedDict()
        self._lock = threading.Lock()
        self._max_sessions = max_sessions
        self._window_k = window_k

    @staticmethod
    def history_to_messages(
        history: list, max_messages: int = 12
    ) -> List[BaseMessage]:
        """
        将前端传来的 history 列表转为 LangChain BaseMessage 列表。

        兼容两种格式：
          - Pydantic model: MessageItem(role="user", content="...")
          - dict: {"role": "user", "content": "..."}

        Args:
            history: 前端发来的对话历史
            max_messages: 最多保留的消息数（默认 12，与现有 history[-12:] 对齐）
        """
        messages = []
        for item in history[-max_messages:]:
            role = item.role if hasattr(item, "role") else item.get("role")
            content = (
                item.content if hasattr(item, "content") else item.get("content", "")
            )
            if role == "user":
                messages.append(HumanMessage(content=content))
            elif role == "assistant":
                messages.append(AIMessage(content=content))
        return messages

    def get_history(self, session_id: str) -> "InMemoryHistory":
        """获取或创建指定会话的 History 实例。"""
        with self._lock:
            if session_id not in self._sessions:
                if len(self._sessions) >= self._max_sessions:
                    self._sessions.popitem(last=False)  # LRU 淘汰最旧的
                self._sessions[session_id] = InMemoryHistory(
                    max_messages=self._window_k * 2
                )
            else:
                # 移到末尾（最近使用）
                self._sessions.move_to_end(session_id)
            return self._sessions[session_id]


class InMemoryHistory(BaseChatMessageHistory):
    """
    简单的内存对话历史，支持滑动窗口。
    实现 LangChain BaseChatMessageHistory 接口，可与 RunnableWithMessageHistory 配合使用。
    """

    def __init__(self, max_messages: int = 12):
        self._messages: List[BaseMessage] = []
        self._max_messages = max_messages

    @property
    def messages(self) -> List[BaseMessage]:
        return self._messages[-self._max_messages:]

    def add_message(self, message: BaseMessage) -> None:
        self._messages.append(message)
        # 超出窗口时截断
        if len(self._messages) > self._max_messages * 2:
            self._messages = self._messages[-self._max_messages:]

    def clear(self) -> None:
        self._messages = []
