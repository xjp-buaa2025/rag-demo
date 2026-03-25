"""
backend/pipelines/ — LangGraph 多步骤数据处理管道

两条管道：
  - RAG 管道：PDF -> Markdown + 图片提取 -> 文本切块 -> 向量编码 -> Qdrant
  - BOM 管道：PDF/DOCX -> 表格提取 -> LLM 转 CSV -> pandas 清洗 -> Neo4j

灵活入口：每条管道可从任意中间节点开始（如直接从 MD 或 Excel 切入）。
"""
