"""
Tier-2 跨章节粗评 QA 生成（20 题）

输入：storage/kg_stages/stage2_manual_triples.json（PT6A 整机 6022 三元组）
输出：tests/kg/fixtures/assembly_qa_tier2.jsonl（20 条 QA）

分布（v4 plan §1.0.1）：
  72-50 涡轮装配     → 6 题（关键词：Turbine, Stator, Blade）
  73-10/20 燃油系统  → 5 题（关键词：Fuel, FCU, Nozzle, Pump fuel）
  76-77 控制与指示   → 4 题（关键词：Control, Indication, Sensor, Bleed valve）
  79 滑油系统        → 5 题（关键词：Oil, Lubric, Scavenge, Reduction gear）

特点：
  - 无 gold_chunk_ids（评测用 LLM-Judge）
  - gold_subgraph 来自 KG 关联三元组
  - 全部聚焦装配场景（避免诊断/维修类问题）
"""
import json
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

random.seed(42)
STAGE2 = Path("storage/kg_stages/stage2_manual_triples.json")
OUTPUT = Path("tests/kg/fixtures/assembly_qa_tier2.jsonl")

# 章节关键词（部分零件名匹配则归入该章节）
CHAPTER_KEYWORDS = {
    "72-50_turbine": [
        "Turbine", "turbine", "Stator", "stator", "Blade", "blade",
        "Vane", "vane", "Disk", "disk", "Shroud", "shroud",
    ],
    "73_fuel": [
        "Fuel", "fuel", "FCU", "Nozzle", "nozzle", "Manifold", "manifold",
        "Drain", "Pump fuel",
    ],
    "76_77_control": [
        "Control", "control", "Bleed", "bleed", "Sensor", "sensor",
        "Indication", "indication", "Governor", "governor", "P3", "PT6A control",
    ],
    "79_oil": [
        "Oil", " oil", "Lubric", "lubric", "Scavenge", "scavenge",
        "Reduction gear", "reduction gear", "Tank", "Filter oil",
    ],
}

CHAPTER_QUOTAS = {
    "72-50_turbine": 6,
    "73_fuel": 5,
    "76_77_control": 4,
    "79_oil": 5,
}


def classify_entity(name: str) -> str | None:
    """根据零件/工序名分类章节，返回章节 key 或 None"""
    if not name:
        return None
    matches = []
    for ch, kws in CHAPTER_KEYWORDS.items():
        for kw in kws:
            if kw in name:
                matches.append(ch)
                break
    if not matches:
        return None
    # 如果多匹配，按优先级 turbine > fuel > oil > control（更具体的优先）
    priority = ["72-50_turbine", "73_fuel", "79_oil", "76_77_control"]
    for p in priority:
        if p in matches:
            return p
    return matches[0]


def load_triples():
    d = json.load(open(STAGE2, encoding="utf-8"))
    triples = d.get("triples", [])
    return triples


def index_triples(triples):
    """构建按 head/tail 索引的字典"""
    out_edges = defaultdict(list)  # head_name → [(rel, tail, t)]
    in_edges = defaultdict(list)   # tail_name → [(rel, head, t)]
    entity_meta = {}  # name → {description, type, ...} 取首次出现
    for t in triples:
        h, tl = t.get("head", ""), t.get("tail", "")
        rel = t.get("relation", "")
        if not h or not tl:
            continue
        out_edges[h].append((rel, tl, t))
        in_edges[tl].append((rel, h, t))
        if h not in entity_meta:
            entity_meta[h] = {
                "type": t.get("head_type", ""),
                "description": t.get("head_description", ""),
            }
        if tl not in entity_meta:
            entity_meta[tl] = {
                "type": t.get("tail_type", ""),
                "description": t.get("tail_description", ""),
            }
    return out_edges, in_edges, entity_meta


def collect_chapter_entities(entity_meta: dict):
    """{chapter_key: [name, ...]}"""
    by_chapter = defaultdict(list)
    for name, meta in entity_meta.items():
        ch = classify_entity(name)
        if ch:
            by_chapter[ch].append(name)
    return by_chapter


def build_qa_for_entity(name: str, ch: str, out_edges: dict, in_edges: dict, entity_meta: dict, qa_id: str) -> dict | None:
    """
    根据实体的 KG 关联生成一题。优先选择具有信息量的关系（procedure/specification/tools）。
    返回 None 表示该实体信息不足，跳过。
    """
    out = out_edges.get(name, [])
    inn = in_edges.get(name, [])
    meta = entity_meta.get(name, {})
    etype = meta.get("type", "")
    desc = meta.get("description", "")

    # 收集相关关系
    requires = [(r, t, tr) for r, t, tr in out if r == "requires"]
    specs = [(r, t, tr) for r, t, tr in out if r == "specifiedBy"]
    mates = [(r, t, tr) for r, t, tr in out if r == "matesWith"] + [(r, h, tr) for r, h, tr in inn if r == "matesWith"]
    parts = [(r, h, tr) for r, h, tr in inn if r == "isPartOf"]   # name 作为 parent，children 是 h
    procs = [(r, h, tr) for r, h, tr in inn if r == "participatesIn"]   # name 是 procedure，h 是 part

    short_name = name[:60] + ("…" if len(name) > 60 else "")

    # ── 模板 1：Procedure → 工具 + 规范 ──
    if etype == "Procedure" or " of " in name or "Removal" in name or "Installation" in name:
        if requires or specs:
            tools = [t[1] for t in requires[:5]]
            spec_lines = []
            for _, sid, tr in specs[:5]:
                sm = entity_meta.get(sid, {})
                sd = sm.get("description", "")
                spec_lines.append(f"{sid}（{sd[:30]}）" if sd else sid)
            ans_parts = []
            if tools:
                ans_parts.append(f"所需工具：{ '、'.join(tools[:3]) }")
            if spec_lines:
                ans_parts.append(f"涉及规范：{ '；'.join(spec_lines[:3]) }")
            return {
                "qa_id": qa_id,
                "category": ch,
                "subtype": "procedure_anchor",
                "question": f"PT6A 装配中，执行「{short_name}」需要哪些工具或遵循哪些规范？",
                "gold_answer": "；".join(ans_parts) + "。",
                "gold_answer_kw": tools + [s for s in spec_lines[:3]],
                "anchor_entity": name,
                "anchor_type": etype,
                "related_triples_count": len(requires) + len(specs),
                "need_human_check": True,
            }

    # ── 模板 2：Part 是装配体的组成 → 列出包含的子件 ──
    if parts and len(parts) >= 2:
        children = [c[1] for c in parts[:6]]
        return {
            "qa_id": qa_id,
            "category": ch,
            "subtype": "assembly_components",
            "question": f"PT6A 的「{short_name}」组件由哪些主要零件构成？",
            "gold_answer": f"主要零件包括：{ '、'.join(c[:50] for c in children) }。" + (f" 整体功能：{desc}" if desc else ""),
            "gold_answer_kw": children,
            "anchor_entity": name,
            "anchor_type": etype,
            "related_triples_count": len(parts),
            "need_human_check": True,
        }

    # ── 模板 3：Part 与其他 Part 的配合关系 ──
    if mates and len(mates) >= 1:
        partners = [m[1] for m in mates[:5]]
        return {
            "qa_id": qa_id,
            "category": ch,
            "subtype": "mating_partners",
            "question": f"PT6A 装配中，「{short_name}」与哪些零件存在配合或连接关系？",
            "gold_answer": f"配合零件：{ '、'.join(p[:50] for p in partners) }。" + (f" {short_name} 的作用：{desc}" if desc else ""),
            "gold_answer_kw": partners,
            "anchor_entity": name,
            "anchor_type": etype,
            "related_triples_count": len(mates),
            "need_human_check": True,
        }

    # ── 模板 4：Part 参与的工序 ──
    if procs and len(procs) >= 1:
        proc_names = [p[1] for p in procs[:5]]
        return {
            "qa_id": qa_id,
            "category": ch,
            "subtype": "involved_procedures",
            "question": f"PT6A 装配中，「{short_name}」涉及哪些主要装配/检查工序？",
            "gold_answer": f"涉及工序：{ '；'.join(p[:60] for p in proc_names) }。",
            "gold_answer_kw": proc_names,
            "anchor_entity": name,
            "anchor_type": etype,
            "related_triples_count": len(procs),
            "need_human_check": True,
        }

    return None  # 信息量不足


def main():
    triples = load_triples()
    print(f"Loaded {len(triples)} triples from stage2")

    out_edges, in_edges, entity_meta = index_triples(triples)
    print(f"Entities: {len(entity_meta)}")

    by_chapter = collect_chapter_entities(entity_meta)
    print(f"\nChapter entity distribution:")
    for ch, names in by_chapter.items():
        print(f"  {ch}: {len(names)}")

    # 按章节配额抽题
    all_qa = []
    qa_counter = 1
    for ch, quota in CHAPTER_QUOTAS.items():
        names = by_chapter.get(ch, [])
        # 按"实体的相关三元组数量"排序，多关联的优先
        scored = []
        for n in names:
            score = len(out_edges.get(n, [])) + len(in_edges.get(n, []))
            scored.append((score, n))
        scored.sort(reverse=True)
        # 优先选 score 高的，跳过信息量不足
        ch_qa = []
        for _, name in scored:
            if len(ch_qa) >= quota:
                break
            qid = f"T2_{ch.split('_')[0]}_{len(ch_qa)+1:02d}"
            qa = build_qa_for_entity(name, ch, out_edges, in_edges, entity_meta, qid)
            if qa:
                ch_qa.append(qa)
        # 全局重编号
        for q in ch_qa:
            q["qa_id_global"] = f"T2_{qa_counter:03d}"
            qa_counter += 1
        all_qa.extend(ch_qa)
        print(f"  → {ch}: {len(ch_qa)}/{quota} 题")

    # 分布统计
    print(f"\nGenerated {len(all_qa)} Tier-2 QA items")
    cat_dist = Counter(q["category"] for q in all_qa)
    sub_dist = Counter(q["subtype"] for q in all_qa)
    print("Category distribution:")
    for k, v in sorted(cat_dist.items()):
        print(f"  {k}: {v}")
    print("Subtype distribution:")
    for k, v in sorted(sub_dist.items()):
        print(f"  {k}: {v}")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        for q in all_qa:
            f.write(json.dumps(q, ensure_ascii=False) + "\n")
    print(f"\n[OK] Saved: {OUTPUT}")
    print(f"File size: {OUTPUT.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
