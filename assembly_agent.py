"""
assembly_agent.py — LangChain Agent：BOM 图谱 + RAG 知识库 → 装配方案

职责：
  提供交互式对话入口，用户输入装配相关问题，Agent 自主决定：
    - 何时查询 Neo4j BOM 图谱（零件层级、材料、数量）
    - 何时查询 ChromaDB RAG 知识库（工艺规范、设计要求）
  综合两路信息，生成结构化航空发动机装配方案。

运行方式：
  PYTHONUTF8=1 python assembly_agent.py
  PYTHONUTF8=1 python assembly_agent.py --query "生成高压涡轮模块的装配方案"

工具列表：
  bom_query       : 查询 Neo4j，获取零件清单、层级、材料、数量等 BOM 信息
  knowledge_query : 查询 ChromaDB，获取航空发动机工艺规范、装配要求等知识

依赖（.env 配置）：
  NEO4J_URI / NEO4J_USER / NEO4J_PASS
  LLM_API_KEY / LLM_BASE_URL / LLM_MODEL

详见 PROJECT_GUIDE.md § BOM-GraphRAG
"""

import os
import sys
import argparse
import json

from dotenv import load_dotenv
from neo4j import GraphDatabase
import chromadb
from sentence_transformers import SentenceTransformer
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.agents import create_react_agent, AgentExecutor
from langchain import hub

load_dotenv()

# ── 配置 ──────────────────────────────────────────────────────────────────────
NEO4J_URI  = os.getenv("NEO4J_URI",  "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASS = os.getenv("NEO4J_PASS", "password")

LLM_API_KEY  = os.getenv("LLM_API_KEY")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.siliconflow.cn/v1")
LLM_MODEL    = os.getenv("LLM_MODEL",    "Qwen/Qwen2.5-72B-Instruct")

CHROMA_DB_DIR   = os.path.join(os.path.dirname(__file__), "storage", "chroma_db")
COLLECTION_NAME = "local_rag_knowledge"
EMBED_MODEL     = "BAAI/bge-m3"
TOP_K           = 4

SYSTEM_PROMPT = """你是一名资深航空发动机装配工程师，熟悉涡扇发动机的结构设计和装配工艺。
你拥有两个工具：
  1. bom_query       — 查询发动机 BOM（零件层级、材料、数量、规格）
  2. knowledge_query — 查询技术知识库（装配工艺、设计规范、注意事项）

回答装配相关问题时，请务必先查询 BOM 获取零件清单，再查询知识库获取工艺要求，
最后综合生成详细的装配方案。方案需包含：零件清单、装配顺序、工艺要点、注意事项。"""


# ── 全局客户端（懒加载，仅初始化一次）───────────────────────────────────────

_neo4j_driver   = None
_chroma_client  = None
_chroma_col     = None
_embed_model    = None


def get_neo4j():
    global _neo4j_driver
    if _neo4j_driver is None:
        try:
            _neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
            _neo4j_driver.verify_connectivity()
            print("[Neo4j] 连接成功")
        except Exception as e:
            print(f"[警告] Neo4j 不可用：{e}（bom_query 工具将返回提示）")
            _neo4j_driver = None
    return _neo4j_driver


def get_chroma():
    global _chroma_client, _chroma_col, _embed_model
    if _chroma_col is None:
        if not os.path.exists(CHROMA_DB_DIR):
            print("[警告] ChromaDB 不存在，knowledge_query 工具将返回提示")
            return None, None

        print(f"[ChromaDB] 加载 Embedding 模型 {EMBED_MODEL}（首次约 30 秒）…")
        _embed_model = SentenceTransformer(EMBED_MODEL)

        class _EmbedFn:
            def __call__(self, texts):
                return _embed_model.encode(texts).tolist()
            def name(self):
                return EMBED_MODEL

        _chroma_client = chromadb.PersistentClient(path=CHROMA_DB_DIR)
        try:
            _chroma_col = _chroma_client.get_collection(
                name=COLLECTION_NAME, embedding_function=_EmbedFn()
            )
            print(f"[ChromaDB] 集合 '{COLLECTION_NAME}' 已加载，共 {_chroma_col.count()} 块")
        except Exception as e:
            print(f"[警告] ChromaDB 集合加载失败：{e}")
            _chroma_col = None
    return _chroma_col, _embed_model


# ── Tool 1：BOM 查询 ──────────────────────────────────────────────────────────

@tool
def bom_query(question: str) -> str:
    """
    查询 Neo4j BOM 图谱，获取航空发动机零件的层级关系、材料、数量、规格等信息。
    输入：自然语言问题，如"高压涡轮模块包含哪些零件？"
    输出：结构化的零件信息文本。
    """
    driver = get_neo4j()
    if driver is None:
        return "[BOM 查询不可用] Neo4j 未连接，请先启动 Docker：docker start neo4j"

    # 根据问题关键词，选择合适的 Cypher 查询策略
    with driver.session() as session:
        # 策略1：查找特定模块的子零件（2跳以内）
        keywords = _extract_part_keywords(question)
        if keywords:
            results = []
            for kw in keywords:
                rows = session.run("""
                    MATCH (parent) WHERE parent.part_name CONTAINS $kw
                       OR parent.part_name_en CONTAINS $kw
                       OR parent.part_id = $kw
                    OPTIONAL MATCH (child)-[:CHILD_OF*1..2]->(parent)
                    WITH parent, collect(child) AS children
                    RETURN parent.part_name    AS module,
                           parent.part_id      AS module_id,
                           parent.spec         AS module_spec,
                           [c IN children | {
                             name    : c.part_name,
                             id      : c.part_id,
                             qty     : c.qty,
                             unit    : c.unit,
                             material: c.material,
                             weight  : c.weight_kg,
                             spec    : c.spec,
                             note    : c.note
                           }] AS parts
                """, kw=kw).data()
                results.extend(rows)

            if results:
                return _format_bom_results(results)

        # 策略2：全局概览（查询顶层模块）
        overview = session.run("""
            MATCH (root)<-[:CHILD_OF*]-(top_module)
            WHERE root.level_code = '1'
            WITH top_module
            WHERE NOT ()-[:CHILD_OF]->(top_module) OR top_module.level_code IN ['1.1','1.2','1.3','1.4','1.5','1.6','1.7']
            MATCH (top_module)
            WHERE top_module.level_code =~ '1\\.\\d+'
            RETURN top_module.part_name AS name,
                   top_module.part_id   AS id,
                   top_module.weight_kg AS weight,
                   top_module.spec      AS spec
            ORDER BY top_module.level_code
        """).data()

        if overview:
            lines = ["发动机主要模块："]
            for r in overview:
                lines.append(f"  - {r['name']} ({r['id']})  重量:{r['weight']} kg  {r['spec'] or ''}")
            return "\n".join(lines)

        return "[BOM 查询] 未找到匹配信息，请尝试更具体的零件名称或模块名称。"


def _extract_part_keywords(question: str) -> list[str]:
    """从问题中提取可能的零件/模块关键词。"""
    # 常见模块名关键词
    KNOWN_MODULES = [
        "风扇", "压气机", "高压压气机", "低压压气机", "燃烧室",
        "高压涡轮", "低压涡轮", "涡轮", "附件", "尾喷管",
        "涡扇发动机", "Fan", "HPC", "LPC", "HPT", "LPT",
        "叶片", "涡轮盘", "压气机盘", "火焰筒", "喷嘴",
    ]
    found = [kw for kw in KNOWN_MODULES if kw in question]
    return found or [question[:20]]  # fallback：取问题前20字


def _format_bom_results(results: list) -> str:
    """将查询结果格式化为可读文本。"""
    lines = []
    seen = set()
    for r in results:
        module = r.get("module", "未知模块")
        if module in seen:
            continue
        seen.add(module)
        lines.append(f"\n【{module}】 ({r.get('module_id','')})")
        if r.get("module_spec"):
            lines.append(f"  规格：{r['module_spec']}")
        parts = r.get("parts") or []
        if parts:
            lines.append(f"  包含零件（共 {len(parts)} 项）：")
            for p in parts:
                mat  = f"  材料:{p['material']}" if p.get("material") else ""
                wt   = f"  重量:{p['weight']}kg" if p.get("weight") else ""
                spec = f"  规格:{p['spec']}" if p.get("spec") else ""
                note = f"  备注:{p['note']}" if p.get("note") else ""
                lines.append(
                    f"    - {p['name']} ({p['id']})  数量:{p['qty']}{p['unit']}"
                    f"{mat}{wt}{spec}{note}"
                )
    return "\n".join(lines) if lines else "[BOM 查询] 无结果"


# ── Tool 2：知识库查询 ─────────────────────────────────────────────────────────

@tool
def knowledge_query(question: str) -> str:
    """
    查询航空发动机技术知识库，获取装配工艺规范、设计要求、注意事项等专业知识。
    输入：技术问题，如"涡轮叶片装配有哪些工艺要求？"
    输出：来自教材的相关原文片段。
    """
    collection, embed_model = get_chroma()
    if collection is None:
        return "[知识库查询不可用] ChromaDB 未初始化，请先运行 main_ingest.py 入库"

    n = min(TOP_K, collection.count())
    if n == 0:
        return "[知识库查询] 知识库为空，请先运行 main_ingest.py 入库"

    query_vec = embed_model.encode([question]).tolist()
    results = collection.query(
        query_embeddings=query_vec,
        n_results=n,
        include=["documents", "metadatas", "distances"],
    )

    docs      = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    lines = [f"【知识库检索结果 — 问题：{question}】\n"]
    for i, (doc, meta, dist) in enumerate(zip(docs, metadatas, distances), 1):
        source = meta.get("source", "未知来源")
        page   = meta.get("page", "?")
        rel    = "高" if dist < 0.3 else "中" if dist < 0.6 else "低"
        lines.append(f"[{i}] 来源：{source} 第{page}页  相关度：{rel}（距离{dist:.3f}）")
        lines.append(f"{doc[:600]}{'…' if len(doc)>600 else ''}\n")

    return "\n".join(lines)


# ── Agent 构建 ────────────────────────────────────────────────────────────────

def build_agent():
    """构建 ReAct Agent，加载工具和 LLM。"""
    llm = ChatOpenAI(
        api_key=LLM_API_KEY,
        base_url=LLM_BASE_URL,
        model=LLM_MODEL,
        temperature=0.3,
        streaming=False,
    )

    tools = [bom_query, knowledge_query]

    # 使用 LangChain Hub 的标准 ReAct prompt
    # 若网络不通，使用内置备用 prompt
    try:
        prompt = hub.pull("hwchase17/react")
    except Exception:
        from langchain_core.prompts import PromptTemplate
        prompt = PromptTemplate.from_template(
            "Answer the following questions as best you can. You have access to the following tools:\n\n"
            "{tools}\n\n"
            "Use the following format:\n\n"
            "Question: the input question you must answer\n"
            "Thought: you should always think about what to do\n"
            "Action: the action to take, should be one of [{tool_names}]\n"
            "Action Input: the input to the action\n"
            "Observation: the result of the action\n"
            "... (this Thought/Action/Action Input/Observation can repeat N times)\n"
            "Thought: I now know the final answer\n"
            "Final Answer: the final answer to the original input question\n\n"
            "Begin!\n\n"
            "Question: {input}\n"
            "Thought:{agent_scratchpad}"
        )

    agent = create_react_agent(llm, tools, prompt)
    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=8,
        handle_parsing_errors=True,
    )
    return executor


# ── 主流程 ────────────────────────────────────────────────────────────────────

def run_query(executor, question: str) -> str:
    """执行单次查询，返回装配方案文本。"""
    full_question = (
        f"{SYSTEM_PROMPT}\n\n"
        f"用户问题：{question}\n\n"
        "请先使用 bom_query 查询相关模块的零件清单，"
        "再使用 knowledge_query 查询工艺规范，"
        "最后综合生成详细装配方案。"
    )
    result = executor.invoke({"input": full_question})
    return result.get("output", "未获得有效答案")


def interactive_mode(executor):
    """交互式对话模式。"""
    print("\n" + "="*55)
    print("  航空发动机装配方案生成器")
    print("  （输入 quit 或 exit 退出）")
    print("="*55)
    print("示例问题：")
    print("  - 生成高压涡轮模块的完整装配方案")
    print("  - 涡轮叶片装配时有哪些注意事项？")
    print("  - 燃烧室模块包含哪些零件？装配顺序是什么？\n")

    while True:
        try:
            question = input("请输入问题 > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n已退出。")
            break

        if not question:
            continue
        if question.lower() in ("quit", "exit", "退出"):
            print("已退出。")
            break

        print("\n[Agent 思考中…]\n")
        try:
            answer = run_query(executor, question)
            print("\n" + "─"*55)
            print("【装配方案】")
            print(answer)
            print("─"*55 + "\n")
        except Exception as e:
            print(f"[错误] {e}\n")


def main():
    parser = argparse.ArgumentParser(description="航空发动机装配方案生成 Agent")
    parser.add_argument("--query", "-q", type=str, help="单次查询（不进入交互模式）")
    args = parser.parse_args()

    print("[初始化] 加载 LLM 和知识库…")
    executor = build_agent()

    if args.query:
        answer = run_query(executor, args.query)
        print("\n【装配方案】")
        print(answer)
    else:
        interactive_mode(executor)


if __name__ == "__main__":
    main()
