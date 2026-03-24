"""
backend/langchain_components — LangChain 集成层

将 LangChain 7 大核心组件（Models、Prompts、Chains、Memory、Agents、Tools、Retrievers）
统一封装在此模块下，作为现有原生 Python 实现的编排层。

现有 FastAPI 路由通过导入本模块来使用 LangChain 组件，
底层检索函数（retrieve.py）和 SSE 适配层（sse.py）保持不变。
"""
