"""
backend/langchain_components/models.py — Models 组件

将现有 FallbackLLMClient 的主备降级逻辑封装为 LangChain BaseChatModel，
提供统一的模型调用接口。切换模型厂商只需修改环境变量，无需改代码。

核心类：
  FallbackChatModel — 自定义 BaseChatModel，先调主 LLM，失败自动切备用
  build_chat_model() — 从环境变量构建 FallbackChatModel 实例

与现有代码的关系：
  - 替代 state.py 中 FallbackLLMClient 在路由中的使用
  - FallbackLLMClient 本身不删除（main_ingest.py CLI 继续使用）
  - Vision 专用的 minimax_client 保持不变（需原始 OpenAI 客户端发 base64 图片）
"""

import os
from typing import Any, Iterator, List, Optional

from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, AIMessageChunk, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatGenerationChunk, ChatResult
from langchain_openai import ChatOpenAI


class FallbackChatModel(BaseChatModel):
    """
    自定义 LangChain ChatModel，封装主备降级逻辑。

    - 同步调用 (_generate)：先调 primary，异常时切 fallback
    - 流式调用 (_stream)：先调 primary，异常时切 fallback
    - 与 LCEL chain.stream() / chain.invoke() 完全兼容
    """

    primary: ChatOpenAI
    fallback: Optional[ChatOpenAI] = None

    @property
    def _llm_type(self) -> str:
        return "fallback-chat-model"

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """同步调用：先 primary，失败则 fallback。"""
        try:
            return self.primary._generate(messages, stop, run_manager, **kwargs)
        except Exception as e:
            if self.fallback is None:
                raise
            print(f"[LangChain] 主 LLM 失败（{e}），切换到备用 LLM...")
            return self.fallback._generate(messages, stop, run_manager, **kwargs)

    def _stream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        """流式调用：先 primary，失败则 fallback。支持 LCEL .stream()。"""
        try:
            yield from self.primary._stream(messages, stop, run_manager, **kwargs)
        except Exception as e:
            if self.fallback is None:
                raise
            print(f"[LangChain] 主 LLM 流式失败（{e}），切换到备用 LLM...")
            yield from self.fallback._stream(messages, stop, run_manager, **kwargs)

    def bind_tools(self, tools, **kwargs):
        """委托给 primary 的 bind_tools（ChatOpenAI 原生支持 OpenAI tool_choice 格式）。
        fallback 在工具调用路径不参与降级，因两者均为 OpenAI 兼容接口。"""
        return self.primary.bind_tools(tools, **kwargs)

    @property
    def _identifying_params(self) -> dict:
        """返回模型标识信息，用于日志和调试。"""
        params = {"primary_model": self.primary.model_name}
        if self.fallback:
            params["fallback_model"] = self.fallback.model_name
        return params


def build_chat_model() -> FallbackChatModel:
    """
    从环境变量构建带降级的 ChatModel。

    环境变量：
      MINIMAX_API_KEY / MINIMAX_BASE_URL / MINIMAX_MODEL — 主 LLM（MiniMax）
      LLM_API_KEY / LLM_BASE_URL / LLM_MODEL — 备用 LLM（SiliconFlow）

    如果未配置 MINIMAX_API_KEY，则只使用备用 LLM（无降级）。
    """
    minimax_key = os.getenv("MINIMAX_API_KEY", "").strip()
    llm_key = os.getenv("LLM_API_KEY", "")
    llm_base = os.getenv("LLM_BASE_URL", "https://api.siliconflow.cn/v1")
    llm_model = os.getenv("LLM_MODEL", "Qwen/Qwen2.5-14B-Instruct")

    if minimax_key:
        primary = ChatOpenAI(
            api_key=minimax_key,
            base_url=os.getenv("MINIMAX_BASE_URL", "https://api.minimaxi.com/v1"),
            model=os.getenv("MINIMAX_MODEL", "MiniMax-M2.5"),
        )
        fallback = ChatOpenAI(
            api_key=llm_key,
            base_url=llm_base,
            model=llm_model,
        )
        return FallbackChatModel(primary=primary, fallback=fallback)
    else:
        # 无 MiniMax 配置，单 LLM 模式（无降级）
        single = ChatOpenAI(
            api_key=llm_key,
            base_url=llm_base,
            model=llm_model,
        )
        return FallbackChatModel(primary=single)
