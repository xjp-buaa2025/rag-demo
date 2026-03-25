"""
backend/pipelines/nodes_bom.py — BOM 管道节点

阶段一（PDF/DOCX 入口）：
  extract_tables — 提取表格为 Markdown 格式
  llm_to_csv     — LLM 将非标准表格转为标准 BOM JSON/CSV

阶段二（CSV/Excel 入口，转换后或直接表格文件）：
  load_table     — 读取 CSV/Excel -> DataFrame JSON
  validate_bom_df — pandas 清洗、字段校验
  write_neo4j    — 写入 Neo4j 节点 + CHILD_OF 关系

所有节点通过 make_bom_nodes() 工厂函数创建，闭包绑定 AppState + neo4j_cfg。
"""

import os
from typing import Any


def make_bom_nodes(app_state: Any, neo4j_cfg: dict):
    """
    工厂函数：通过闭包绑定 AppState 和 Neo4j 配置，返回所有 BOM 节点函数的字典。
    """

    # ------------------------------------------------------------------
    # 阶段一：文档转表格（PDF/DOCX 入口）
    # ------------------------------------------------------------------

    def extract_tables(state: dict) -> dict:
        """从 PDF/DOCX 提取表格 -> Markdown 格式。
        复用 bom.py 的 _extract_from_pdf() 和 _extract_from_docx()。"""
        from backend.routers.bom import _extract_from_pdf, _extract_from_docx, _DOCX_AVAILABLE

        file_path = state["file_path"]
        ext = state.get("file_ext", "")
        logs = [f"[extract_tables] 提取 {ext.upper()} 中的表格…"]

        try:
            if ext == "pdf":
                raw = _extract_from_pdf(file_path)
            elif ext == "docx":
                if not _DOCX_AVAILABLE:
                    return {"error": "缺少 python-docx，请运行：pip install python-docx",
                            "log_messages": logs}
                raw = _extract_from_docx(file_path)
            else:
                return {"error": f"不支持的格式：{ext}，BOM 管道支持 pdf/docx/xlsx/csv",
                        "log_messages": logs}

            if not raw.strip():
                return {"error": f"{ext.upper()} 中未找到可识别的表格或文本",
                        "log_messages": logs}

            logs.append(f"[extract_tables] 提取完成（{len(raw)} 字符）")
            return {
                "tables_markdown": raw,
                "current_node": "extract_tables",
                "log_messages": logs,
            }
        except Exception as e:
            return {"error": f"表格提取失败: {e}", "log_messages": logs}

    def llm_to_csv(state: dict) -> dict:
        """LLM 将非标准表格 Markdown 转为标准 BOM JSON 记录。
        复用 bom.py 的 _LlmBomConverter / _split_for_llm / _parse_llm_json。"""
        from backend.routers.bom import _split_for_llm, _parse_llm_json, BOM_CONVERSION_PROMPT

        raw_text = state.get("tables_markdown", "")
        if not raw_text.strip():
            return {"error": "无表格内容可转换", "log_messages": ["[llm_to_csv] 无内容"]}

        chunks = _split_for_llm(raw_text)
        logs = [f"[llm_to_csv] 文档分为 {len(chunks)} 段，开始 LLM 转换…"]
        all_records = []

        for i, chunk in enumerate(chunks):
            logs.append(f"  LLM 转换第 {i + 1}/{len(chunks)} 段…")
            prompt = BOM_CONVERSION_PROMPT.format(content=chunk)
            try:
                resp = app_state.llm_client.chat.completions.create(
                    model=None,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                )
                raw_json = resp.choices[0].message.content
                records = _parse_llm_json(raw_json)
                logs.append(f"  第 {i + 1} 段提取到 {len(records)} 条记录")
                all_records.extend(records)
            except Exception as e:
                logs.append(f"  第 {i + 1} 段 LLM 调用失败：{e}")

        if not all_records:
            return {"error": "LLM 未能提取有效 BOM 记录", "log_messages": logs}

        logs.append(f"[llm_to_csv] LLM 转换完成：共 {len(all_records)} 条原始记录")
        return {
            "bom_records": all_records,
            "current_node": "llm_to_csv",
            "log_messages": logs,
        }

    # ------------------------------------------------------------------
    # 阶段二：数据处理（CSV/Excel 入口）
    # ------------------------------------------------------------------

    def load_table(state: dict) -> dict:
        """读取 CSV/Excel -> DataFrame JSON 序列化。"""
        import pandas as pd

        file_path = state["file_path"]
        ext = state.get("file_ext", "")
        logs = [f"[load_table] 读取 {ext.upper()} 文件…"]

        try:
            if ext in ("xlsx", "xls"):
                df = pd.read_excel(file_path, dtype=str)
            elif ext == "csv":
                df = pd.read_csv(file_path, dtype=str)
            else:
                return {"error": f"不支持的格式：{ext}", "log_messages": logs}

            df.columns = [c.strip().lower() for c in df.columns]
            logs.append(f"[load_table] 读取成功：{len(df)} 行 × {len(df.columns)} 列")
            return {
                "bom_dataframe_json": df.to_json(orient="records", force_ascii=False),
                "current_node": "load_table",
                "log_messages": logs,
            }
        except Exception as e:
            return {"error": f"读取文件失败: {e}", "log_messages": logs}

    def validate_bom_df(state: dict) -> dict:
        """pandas 清洗、字段校验、填默认值。
        输入来自 llm_to_csv（bom_records）或 load_table（bom_dataframe_json）。"""
        import pandas as pd

        logs = ["[validate] 开始数据清洗…"]

        # 确定数据来源
        if state.get("bom_records"):
            df = pd.DataFrame(state["bom_records"])
            logs.append(f"  来源：LLM 解析结果（{len(df)} 条）")
        elif state.get("bom_dataframe_json"):
            df = pd.read_json(state["bom_dataframe_json"], orient="records")
            df.columns = [c.strip().lower() for c in df.columns]
            logs.append(f"  来源：CSV/Excel 文件（{len(df)} 行）")
        else:
            return {"error": "无 BOM 数据可处理", "log_messages": logs}

        # 确保必填列存在
        required = ["level_code", "part_id", "part_name", "part_name_en",
                    "category", "qty", "unit"]
        optional = ["material", "weight_kg", "spec", "note"]
        for col in required + optional:
            if col not in df.columns:
                df[col] = ""

        # 数据清洗
        df = df.dropna(subset=["level_code", "part_id"])
        for col in df.columns:
            df[col] = df[col].fillna("").astype(str).str.strip()
        df = df[df["level_code"].str.strip() != ""]
        df = df[df["part_id"].str.strip() != ""]
        df["qty"] = pd.to_numeric(df["qty"], errors="coerce").fillna(1).astype(int)
        df["unit"] = df["unit"].replace("", "件")
        df["category"] = df["category"].replace("", "Part")

        if df.empty:
            return {"error": "清洗后无有效 BOM 记录", "log_messages": logs}

        categories = df["category"].value_counts().to_dict()
        logs.append(f"[validate] 清洗完成：{len(df)} 条记录 | {categories}")

        return {
            "bom_dataframe_json": df.to_json(orient="records", force_ascii=False),
            "current_node": "validate_bom_df",
            "log_messages": logs,
        }

    def write_neo4j(state: dict) -> dict:
        """写入 Neo4j 节点（Assembly/Part/Standard）+ CHILD_OF 关系。
        复用 bom.py 的 _run_bom_ingest() 中的 Neo4j 写入逻辑。"""
        import pandas as pd
        from backend.routers.bom import _get_neo4j_driver

        df_json = state.get("bom_dataframe_json", "")
        if not df_json:
            return {"error": "无 BOM 数据可写入", "log_messages": ["[neo4j] 无数据"]}

        df = pd.read_json(df_json, orient="records")
        clear_first = state.get("clear_first", False)
        logs = ["[neo4j] 连接 Neo4j…"]

        driver = _get_neo4j_driver(app_state, neo4j_cfg)
        if driver is None:
            return {"error": "Neo4j 不可用，请先启动：docker start neo4j",
                    "log_messages": logs}
        logs.append("[neo4j] 连接成功")

        try:
            with driver.session() as session:
                for label in ("Assembly", "Part", "Standard"):
                    session.run(
                        f"CREATE CONSTRAINT IF NOT EXISTS FOR (n:{label}) REQUIRE n.part_id IS UNIQUE"
                    )
                logs.append("[neo4j] Schema 约束已就绪")

                if clear_first:
                    r = session.run("""
                        MATCH (n) WHERE n:Assembly OR n:Part OR n:Standard
                        DETACH DELETE n RETURN count(n) AS cnt
                    """).single()
                    logs.append(f"[neo4j] 已清空旧数据（{r['cnt']} 个节点）")

                records = df.to_dict(orient="records")
                for category in ("Assembly", "Part", "Standard"):
                    batch = [r for r in records if r.get("category") == category]
                    if not batch:
                        continue
                    session.run(f"""
                        UNWIND $rows AS row
                        MERGE (n:{category} {{part_id: row.part_id}})
                        SET n.level_code   = row.level_code,
                            n.part_name    = row.part_name,
                            n.part_name_en = row.part_name_en,
                            n.qty          = toInteger(row.qty),
                            n.unit         = row.unit,
                            n.material     = row.material,
                            n.weight_kg    = CASE row.weight_kg WHEN '' THEN null
                                             ELSE toFloat(row.weight_kg) END,
                            n.spec         = row.spec,
                            n.note         = row.note
                    """, rows=batch)
                    logs.append(f"  {category}：写入 {len(batch)} 个节点")

                # 建立 CHILD_OF 关系
                level_map = dict(zip(df["level_code"].astype(str),
                                     df["part_id"].astype(str)))
                edges = []
                for _, row in df.iterrows():
                    code = str(row["level_code"])
                    if "." not in code:
                        continue
                    parent_code = ".".join(code.split(".")[:-1])
                    parent_id = level_map.get(parent_code)
                    if parent_id:
                        edges.append({"child_id": row["part_id"], "parent_id": parent_id})

                if edges:
                    session.run("""
                        UNWIND $edges AS e
                        MATCH (child  {part_id: e.child_id})
                        MATCH (parent {part_id: e.parent_id})
                        MERGE (child)-[:CHILD_OF]->(parent)
                    """, edges=edges)

                r2 = session.run("""
                    MATCH (n) WHERE n:Assembly OR n:Part OR n:Standard
                    RETURN count(CASE WHEN n:Assembly THEN 1 END) AS a,
                           count(CASE WHEN n:Part     THEN 1 END) AS p,
                           count(CASE WHEN n:Standard THEN 1 END) AS s
                """).single()

                summary = (
                    f"[neo4j] 入库完成！"
                    f"Assembly:{r2['a']}  Part:{r2['p']}  Standard:{r2['s']}  "
                    f"关系:{len(edges)} 条"
                )
                logs.append(summary)

            return {
                "stats": {"assembly": r2["a"], "part": r2["p"],
                           "standard": r2["s"], "edges": len(edges)},
                "current_node": "write_neo4j",
                "log_messages": logs,
            }
        except Exception as e:
            return {"error": f"Neo4j 写入失败: {e}", "log_messages": logs}

    # ------------------------------------------------------------------
    # 返回节点字典
    # ------------------------------------------------------------------
    return {
        "extract_tables": extract_tables,
        "llm_to_csv": llm_to_csv,
        "load_table": load_table,
        "validate_bom_df": validate_bom_df,
        "write_neo4j": write_neo4j,
    }
