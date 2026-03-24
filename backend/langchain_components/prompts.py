"""
backend/langchain_components/prompts.py — Prompts 组件

将散落在各路由文件中的硬编码 prompt 统一管理为 LangChain ChatPromptTemplate。
好处：集中维护、支持变量注入、可复用、可版本管理。

各模板替换来源：
  RAG_QA_PROMPT           ← chat.py SYSTEM_PROMPT
  MULTI_QUERY_PROMPT      ← chat.py _generate_extra_queries() 内的硬编码
  JUDGE_PROMPT            ← eval.py JUDGE_PROMPT_TMPL
  ASSEMBLY_PROMPT         ← assembly.py ASSEMBLY_SYSTEM_PROMPT
  VISION_CAPTION_PROMPT   ← image_captioner.py _CAPTION_PROMPT
  AGENT_SYSTEM_PROMPT     ← 已迁移至 agents.py（create_agent 用 str 而非 ChatPromptTemplate）

  RAGAS 系列              ← eval.py 中的 RAGAS_* 常量
"""

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


# ===== 1. RAG 问答 Prompt =====
# 替换 chat.py:32-36 的 SYSTEM_PROMPT
RAG_QA_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "你是一个专业的知识库问答助手。请严格根据提供的参考资料回答用户问题。\n"
     "如果参考资料中没有相关信息，请如实说明\"知识库中没有找到相关内容\"，不要凭空捏造。\n"
     "回答要详细、准确、有条理，尽量引用原文中的具体数据和技术细节，不要省略重要信息。\n"
     "如果参考资料中包含图片（标记为\"图片描述\"的条目会附带图片URL），"
     "请在回答中使用 Markdown 图片语法 ![描述](URL) 展示相关图片。"
     "只使用参考资料中提供的图片URL，不要编造URL。"),
    MessagesPlaceholder(variable_name="history"),
    ("human", "参考资料：\n{context}\n\n用户问题：{question}"),
])


# ===== 2. 多查询生成 Prompt =====
# 替换 chat.py:53-58 _generate_extra_queries() 中的硬编码 prompt
MULTI_QUERY_PROMPT = ChatPromptTemplate.from_messages([
    ("human",
     "请为以下问题从{count}个不同角度生成{count}个补充检索查询。\n"
     "要求：\n"
     "1. 每个查询独占一行，无需编号或其他符号\n"
     "2. 与原问题表达不同，侧重不同方面或使用不同关键词\n"
     "3. 保持简洁，不超过50字\n\n"
     "原问题：{question}\n\n"
     "仅输出{count}个查询，每行一个："),
])


# ===== 3. LLM-as-Judge 评估 Prompt =====
# 替换 eval.py:43-64 的 JUDGE_PROMPT_TMPL
JUDGE_PROMPT = ChatPromptTemplate.from_messages([
    ("human",
     "你是一名 RAG 系统评估专家。请根据以下检索到的文档片段，对其质量进行评分。\n\n"
     "【问题】\n{question}\n\n"
     "【检索到的文档片段】\n{context}\n\n"
     "请从以下三个维度各打 0-5 分（整数），并给出简短理由（各一句话）：\n"
     "1. 相关性（0-5）：片段内容与问题的相关程度\n"
     "2. 完整性（0-5）：片段是否包含足以回答该问题的信息\n"
     "3. 可回答性（0-5）：仅凭这些片段，是否能给出令用户满意的答案\n\n"
     "请严格按以下 JSON 格式输出，不要有其他内容：\n"
     '{{"relevance": <0-5>, "completeness": <0-5>, "answerability": <0-5>,\n'
     '  "reason_relevance": "<一句话>", "reason_completeness": "<一句话>",\n'
     '  "reason_answerability": "<一句话>"}}'),
])


# ===== 4. 装配方案 Prompt =====
# 替换 assembly.py:25-28 的 ASSEMBLY_SYSTEM_PROMPT
ASSEMBLY_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "你是一名资深航空发动机装配工程师，熟悉涡扇发动机的结构设计和装配工艺。\n"
     "根据提供的 BOM 零件清单和技术知识库内容，生成详细的装配方案。\n"
     "方案须包含：零件清单确认、装配顺序（步骤编号）、工艺要点（力矩/公差/工装）、注意事项。\n"
     "若 BOM 或知识库无相关数据，请说明并基于通用工程知识回答。"),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{sections}\n\n【用户问题】\n{question}"),
])


# ===== 5. Vision 图片描述 Prompt =====
# 替换 image_captioner.py:17-21 的 _CAPTION_PROMPT（仅用于 prompt 管理，实际调用仍走原始 client）
VISION_CAPTION_PROMPT = ChatPromptTemplate.from_messages([
    ("human",
     "请用中文详细描述这张图片的内容，包括：图中的主要元素、结构关系、标注文字（如有）。\n"
     "如果这是技术图纸或示意图，请重点描述其结构和功能。\n"
     "描述要准确、详尽，以便用于文档检索。{context_hint}"),
])


# ===== 6. Agent 路由决策 Prompt =====
# 已迁移至 agents.py（create_agent 使用 system_prompt 字符串，非 ChatPromptTemplate）


# ===== 7. RAGAS 评估系列 Prompt =====
# 替换 eval.py:66-94 的 RAGAS_* 常量

RAGAS_CONTEXT_RELEVANCE_PROMPT = ChatPromptTemplate.from_messages([
    ("human",
     "你是一名 RAG 评估专家。给定以下问题和检索到的上下文，"
     "请提取上下文中与问题直接相关的句子。\n"
     "每行输出一个相关句子，不要输出任何编号或解释。如果没有相关句子，仅输出 NONE。\n\n"
     "【问题】\n{question}\n\n【上下文】\n{context}"),
])

RAGAS_FAITHFULNESS_DECOMPOSE_PROMPT = ChatPromptTemplate.from_messages([
    ("human",
     "将以下答案拆解为原子化的事实声明（每个声明是一个简短、独立可验证的陈述句）。\n"
     "每行输出一条声明，不要编号，不要解释。\n\n【答案】\n{answer}"),
])

RAGAS_FAITHFULNESS_VERIFY_PROMPT = ChatPromptTemplate.from_messages([
    ("human",
     "给定以下上下文和一条声明，判断该声明是否完全由上下文内容支撑。\n"
     "只回答 YES 或 NO，不要有任何其他内容。\n\n"
     "【上下文】\n{context}\n\n【声明】\n{claim}"),
])

RAGAS_ANSWER_RELEVANCE_PROMPT = ChatPromptTemplate.from_messages([
    ("human",
     "给定以下答案，生成 3 个可能引发该答案的不同问题。\n"
     "每行输出一个问题，不要编号，不要解释。\n\n【答案】\n{answer}"),
])
