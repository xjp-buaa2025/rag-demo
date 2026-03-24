"""
backend/langchain_components/chains.py — Chains 组件

使用 LCEL（LangChain Expression Language）将 Prompt + Retriever + LLM 串联成声明式工作流。
每个 Chain 是一个可 invoke / stream 的 Runnable。

核心 Chain：
  build_rag_chain()         — RAG 问答链：context + history + question → 流式回答
  build_multi_query_chain() — 多查询生成链：question → 多角度查询列表
  build_assembly_chain()    — 装配方案链：BOM + RAG + question → 装配方案
  build_judge_chain()       — 评估打分链：question + context → JSON 打分

与现有代码的关系：
  - build_rag_chain() 替换 chat.py _chat_gen() 的阶段四（Prompt构建 + LLM流式调用）
  - build_multi_query_chain() 替换 chat.py _generate_extra_queries()
  - build_assembly_chain() 替换 assembly.py _assembly_chat_gen() 的 LLM 调用部分
  - build_judge_chain() 替换 eval.py 中的 LLM Judge 打分逻辑
"""

import json
import re
from typing import List

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda

from backend.langchain_components.prompts import (
    ASSEMBLY_PROMPT,
    JUDGE_PROMPT,
    MULTI_QUERY_PROMPT,
    RAG_QA_PROMPT,
)


def build_rag_chain(llm):
    """
    构建 RAG 问答链。

    输入（dict）：
      - context: str（格式化后的参考资料文本）
      - question: str（用户问题）
      - history: List[BaseMessage]（对话历史）

    输出：str（流式时为 token 增量）

    使用方式：
      # 流式（推荐，与现有 SSE 兼容）
      for chunk in rag_chain.stream({"context": ctx, "question": q, "history": msgs}):
          full_answer += chunk
          yield full_answer

      # 同步
      answer = rag_chain.invoke({"context": ctx, "question": q, "history": msgs})
    """
    chain = RAG_QA_PROMPT | llm | StrOutputParser()
    return chain


def build_multi_query_chain(llm):
    """
    构建多查询生成链。

    输入（dict）：
      - question: str（原始用户问题）
      - count: int（生成的额外查询数）

    输出：List[str]（多角度查询列表）
    """

    def parse_queries(text: str) -> List[str]:
        """按行解析，过滤空行和编号前缀。"""
        lines = []
        for line in text.strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            # 去掉可能的编号前缀（如 "1. " 或 "1、"）
            line = re.sub(r"^\d+[.、)\]]\s*", "", line)
            if line:
                lines.append(line)
        return lines

    chain = (
        MULTI_QUERY_PROMPT
        | llm.bind(temperature=0.7)
        | StrOutputParser()
        | RunnableLambda(parse_queries)
    )
    return chain


def build_assembly_chain(llm):
    """
    构建装配方案链。

    输入（dict）：
      - sections: str（格式化后的 BOM + RAG 上下文）
      - question: str（用户问题）
      - history: List[BaseMessage]（对话历史）

    输出：str（流式时为 token 增量）
    """
    chain = ASSEMBLY_PROMPT | llm | StrOutputParser()
    return chain


def build_judge_chain(llm):
    """
    构建 LLM-as-Judge 评估链。

    输入（dict）：
      - question: str（评估问题）
      - context: str（检索到的文档片段）

    输出：dict（JSON 打分结果）
    """

    def parse_judge_response(text: str) -> dict:
        """从 LLM 输出中提取 JSON 打分结果。"""
        s = text.find("{")
        e = text.rfind("}") + 1
        if s >= 0 and e > s:
            try:
                return json.loads(text[s:e])
            except json.JSONDecodeError:
                pass
        return {}

    chain = (
        JUDGE_PROMPT
        | llm.bind(temperature=0.01)
        | StrOutputParser()
        | RunnableLambda(parse_judge_response)
    )
    return chain
