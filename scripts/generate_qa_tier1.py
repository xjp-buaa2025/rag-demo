"""
Tier-1 精评 QA 生成 v2（改进版）

输入：storage/kg_stages/golden_triples.json（108 实体 / 99 三元组 / 72-30 压气机）
输出：tests/kg/fixtures/assembly_qa_tier1.jsonl（60 条 QA）

v2 相对 v1 的改进：
  - A 类补到 20 题：A1(10)+A2(5)+A3(5)，新增"跨级祖父装配"查询
  - B1 工序-工具合并：同一工序的多工具合并为一题（Q018-20 → Q018）
  - C1 工序-规范合并：同一工序的多规范合并答案
  - D1 mates_with 增强：关联 hasInterface 拿 interface_type 写入答案

QA 分布（v4 plan §1.1）：
  A 零件结构          → 20 题（10 child→parent / 5 parent→children / 5 grandparent）
  B 工序工具          → 12 题（3 合并工具 / 6 工序零件 / 3 工序先后）
  C 技术规范          → 9 题（6 工序规范 / 3 反向问规范用途）
  D 几何配合          → 19 题（8 mates_with 增强 / 5 hasInterface / 3 adjacentTo / 3 constrainedBy）

需 Day 3 陛下勾选 ✓/✗。
"""
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

random.seed(42)

GOLDEN = Path("storage/kg_stages/golden_triples.json")
OUTPUT = Path("tests/kg/fixtures/assembly_qa_tier1.jsonl")


def load_golden():
    d = json.load(open(GOLDEN, encoding="utf-8"))
    id2ent = {}
    for items in d["entities"].values():
        for e in items:
            id2ent[e["id"]] = e
    return d, id2ent


def name_of(ent: dict, prefer: str = "zh") -> str:
    if prefer == "zh":
        return (ent.get("name_zh") or ent.get("name_en") or ent.get("id", "")).strip()
    return (ent.get("name_en") or ent.get("name_zh") or ent.get("id", "")).strip()


def ata_of(*sources: str) -> str:
    """从多个 source 字符串取第一个 ATA 章节号"""
    import re
    for s in sources:
        m = re.search(r"(\d{2}-\d{2}-\d{2})", s or "")
        if m:
            return m.group(1)
    return ""


def build_indices(triples: list):
    """
    返回字典：
      child2parent: {child_id: [(parent_id, triple_id), ...]}
      parent2children: {parent_id: [(child_id, triple_id), ...]}
      proc_tools: {proc_id: [(tool_id, t)]}      requires
      proc_parts: {proc_id: [(part_id, t)]}      participatesIn (Part→Procedure 头尾翻转)
      proc_specs: {proc_id: [(spec_id, t)]}      specifiedBy
      part_iface: {part_id: [(iface_id, t)]}      hasInterface
      iface_gc:   {iface_id: [(gc_id, t)]}        constrainedBy
      mates:      list of triples                  matesWith
      adjacents:  list of triples                  adjacentTo
      precedes:   list of triples                  precedes
    """
    idx = {
        "child2parent": defaultdict(list),
        "parent2children": defaultdict(list),
        "proc_tools": defaultdict(list),
        "proc_parts": defaultdict(list),
        "proc_specs": defaultdict(list),
        "iface_specs": defaultdict(list),
        "part_iface": defaultdict(list),
        "iface_gc": defaultdict(list),
        "mates": [],
        "adjacents": [],
        "precedes": [],
    }
    for t in triples:
        rel = t["relation"]
        h, tl = t["head"], t["tail"]
        if rel == "isPartOf":
            idx["child2parent"][h].append((tl, t))
            idx["parent2children"][tl].append((h, t))
        elif rel == "requires":
            idx["proc_tools"][h].append((tl, t))
        elif rel == "participatesIn":
            idx["proc_parts"][tl].append((h, t))  # Part→Procedure
        elif rel == "specifiedBy":
            # head 可能是 Procedure 或 Interface
            idx["proc_specs"][h].append((tl, t))
            idx["iface_specs"][h].append((tl, t))
        elif rel == "hasInterface":
            idx["part_iface"][h].append((tl, t))
        elif rel == "constrainedBy":
            idx["iface_gc"][h].append((tl, t))
        elif rel == "matesWith":
            idx["mates"].append(t)
        elif rel == "adjacentTo":
            idx["adjacents"].append(t)
        elif rel == "precedes":
            idx["precedes"].append(t)
    return idx


# ═════════════════════════════════════════════════════════════════════════════
# A 零件结构（20 题）
# ═════════════════════════════════════════════════════════════════════════════
def gen_A(id2ent, idx):
    items = []

    # A1: child→parent，10 题
    isPartOf = []
    for child_id, parents in idx["child2parent"].items():
        for parent_id, t in parents:
            isPartOf.append((child_id, parent_id, t))
    sampled = random.sample(isPartOf, min(10, len(isPartOf)))
    for i, (c, p, t) in enumerate(sampled):
        ce, pe = id2ent.get(c, {}), id2ent.get(p, {})
        items.append({
            "category": "A_structure",
            "subtype": "child_to_parent",
            "question": f"在 PT6A 压气机装配中，{name_of(ce)}（{name_of(ce, 'en')}）属于哪个装配体？",
            "gold_answer": f"{name_of(ce)}属于{name_of(pe)}（{name_of(pe, 'en')}）。",
            "gold_answer_kw": [name_of(pe), name_of(pe, "en")],
            "gold_subgraph": {"nodes": [c, p], "triples": [{"head": c, "relation": "isPartOf", "tail": p}]},
            "source_ata": ata_of(t.get("source"), pe.get("ata", "")),
            "source_triple_ids": [t.get("id", "")],
        })

    # A2: parent→children，选子件 ≥2 的 parent，最多 5 题
    big_parents = [(p, ch) for p, ch in idx["parent2children"].items() if len(ch) >= 2]
    random.shuffle(big_parents)
    for parent_id, children_pairs in big_parents[:5]:
        pe = id2ent.get(parent_id, {})
        ch_names = [name_of(id2ent.get(cid, {})) for cid, _ in children_pairs if id2ent.get(cid)]
        triple_ids = [t.get("id", "") for _, t in children_pairs]
        if not ch_names:
            continue
        items.append({
            "category": "A_structure",
            "subtype": "parent_to_children",
            "question": f"PT6A 的 {name_of(pe)}（{name_of(pe, 'en')}）由哪些主要零件/组件构成？",
            "gold_answer": f"{name_of(pe)}主要包含：" + "、".join(ch_names) + "等。",
            "gold_answer_kw": ch_names,
            "gold_subgraph": {
                "nodes": [parent_id] + [cid for cid, _ in children_pairs],
                "triples": [{"head": cid, "relation": "isPartOf", "tail": parent_id} for cid, _ in children_pairs],
            },
            "source_ata": ata_of(pe.get("ata", "")),
            "source_triple_ids": triple_ids,
        })

    # A3: grandparent，跨级 isPartOf*2 链查询，5 题
    chains = []  # (leaf_id, mid_id, top_id, t1, t2)
    for leaf_id, mids in idx["child2parent"].items():
        for mid_id, t1 in mids:
            tops = idx["child2parent"].get(mid_id, [])
            for top_id, t2 in tops:
                chains.append((leaf_id, mid_id, top_id, t1, t2))
    random.shuffle(chains)
    seen_leaves = set()
    a3_count = 0
    for leaf_id, mid_id, top_id, t1, t2 in chains:
        if leaf_id in seen_leaves:
            continue
        seen_leaves.add(leaf_id)
        le, me, te = id2ent.get(leaf_id, {}), id2ent.get(mid_id, {}), id2ent.get(top_id, {})
        items.append({
            "category": "A_structure",
            "subtype": "grandparent",
            "question": f"在 PT6A 装配层级中，{name_of(le)}（{name_of(le, 'en')}）所属的最高级装配体是什么？",
            "gold_answer": f"{name_of(le)}经由{name_of(me)}最终归属于{name_of(te)}（{name_of(te, 'en')}）。",
            "gold_answer_kw": [name_of(te), name_of(te, "en"), name_of(me)],
            "gold_subgraph": {
                "nodes": [leaf_id, mid_id, top_id],
                "triples": [
                    {"head": leaf_id, "relation": "isPartOf", "tail": mid_id},
                    {"head": mid_id, "relation": "isPartOf", "tail": top_id},
                ],
            },
            "source_ata": ata_of(t1.get("source"), t2.get("source"), te.get("ata", "")),
            "source_triple_ids": [t1.get("id", ""), t2.get("id", "")],
        })
        a3_count += 1
        if a3_count >= 5:
            break

    return items


# ═════════════════════════════════════════════════════════════════════════════
# B 工序工具（12 题）
# ═════════════════════════════════════════════════════════════════════════════
def gen_B(id2ent, idx):
    items = []

    # B1: procedure → 所有所需工具（合并版），3 题
    proc_with_tools = [(p, tools) for p, tools in idx["proc_tools"].items() if tools]
    proc_with_tools.sort(key=lambda x: -len(x[1]))  # 多工具的优先
    for proc_id, tool_pairs in proc_with_tools[:3]:
        pe = id2ent.get(proc_id, {})
        tool_names = []
        triple_ids = []
        nodes = [proc_id]
        triples_sg = []
        for tid, t in tool_pairs:
            te = id2ent.get(tid, {})
            disp = name_of(te)
            if te.get("tool_id"):
                disp += f"（{te['tool_id']}）"
            tool_names.append(disp)
            triple_ids.append(t.get("id", ""))
            nodes.append(tid)
            triples_sg.append({"head": proc_id, "relation": "requires", "tail": tid})
        items.append({
            "category": "B_procedure",
            "subtype": "proc_tools_merged",
            "question": f"执行{name_of(pe)}（{name_of(pe, 'en')}）工序时，需要哪些专用工具？",
            "gold_answer": f"{name_of(pe)}需要使用以下工具：" + "、".join(tool_names) + "。",
            "gold_answer_kw": tool_names,
            "gold_subgraph": {"nodes": nodes, "triples": triples_sg},
            "source_ata": ata_of(pe.get("step_id", "")),
            "source_triple_ids": triple_ids,
        })

    # B2: procedure → 参与零件，6 题
    proc_with_parts = [(p, parts) for p, parts in idx["proc_parts"].items() if parts]
    proc_with_parts.sort(key=lambda x: -len(x[1]))
    for proc_id, part_pairs in proc_with_parts[:6]:
        pe = id2ent.get(proc_id, {})
        part_names = [name_of(id2ent.get(pid, {})) for pid, _ in part_pairs if id2ent.get(pid)]
        triple_ids = [t.get("id", "") for _, t in part_pairs]
        if not part_names:
            continue
        items.append({
            "category": "B_procedure",
            "subtype": "proc_to_parts",
            "question": f"PT6A 的{name_of(pe)} 工序涉及到哪些主要零件？",
            "gold_answer": f"{name_of(pe)}涉及零件：" + "、".join(part_names) + "。",
            "gold_answer_kw": part_names,
            "gold_subgraph": {
                "nodes": [proc_id] + [pid for pid, _ in part_pairs],
                "triples": [{"head": pid, "relation": "participatesIn", "tail": proc_id} for pid, _ in part_pairs],
            },
            "source_ata": ata_of(pe.get("step_id", "")),
            "source_triple_ids": triple_ids,
        })

    # B3: 工序先后，3 题
    for t in idx["precedes"][:3]:
        pa, pb = id2ent.get(t["head"], {}), id2ent.get(t["tail"], {})
        items.append({
            "category": "B_procedure",
            "subtype": "proc_sequence",
            "question": f"PT6A 装配中，完成{name_of(pa)}之后，下一步应执行什么工序？",
            "gold_answer": f"下一步执行{name_of(pb)}（{name_of(pb, 'en')}）。",
            "gold_answer_kw": [name_of(pb)],
            "gold_subgraph": {
                "nodes": [t["head"], t["tail"]],
                "triples": [{"head": t["head"], "relation": "precedes", "tail": t["tail"]}],
            },
            "source_ata": ata_of(t.get("source"), pa.get("step_id", "")),
            "source_triple_ids": [t.get("id", "")],
        })

    return items


# ═════════════════════════════════════════════════════════════════════════════
# C 技术规范（9 题）
# ═════════════════════════════════════════════════════════════════════════════
def gen_C(id2ent, idx):
    items = []

    # C1: head（Procedure or Interface）→ 所有规范，按 head 分组合并，最多 6 题
    proc_with_specs = [(p, specs) for p, specs in idx["proc_specs"].items() if specs]
    proc_with_specs.sort(key=lambda x: -len(x[1]))
    for proc_id, spec_pairs in proc_with_specs[:6]:
        pe = id2ent.get(proc_id, {})
        # 按 spec_type 分组
        bytype = defaultdict(list)
        triple_ids = []
        for sid, t in spec_pairs:
            se = id2ent.get(sid, {})
            stype = se.get("type", "spec")
            val = se.get("value", "")
            unit = se.get("unit", "")
            bytype[stype].append(f"{name_of(se)}：{val} {unit}".strip())
            triple_ids.append(t.get("id", ""))
        types_str = "、".join(bytype.keys())
        all_specs = []
        for stype, specs in bytype.items():
            all_specs.extend(specs)
        items.append({
            "category": "C_specification",
            "subtype": "proc_specs_merged",
            "question": f"执行{name_of(pe)}（{name_of(pe, 'en')}）需要遵循哪些技术规范（如{types_str}）？",
            "gold_answer": f"{name_of(pe)}涉及的技术规范包括：" + "；".join(all_specs) + "。",
            "gold_answer_kw": [s.split("：")[-1].strip() for s in all_specs],
            "gold_subgraph": {
                "nodes": [proc_id] + [sid for sid, _ in spec_pairs],
                "triples": [{"head": proc_id, "relation": "specifiedBy", "tail": sid} for sid, _ in spec_pairs],
            },
            "source_ata": ata_of(pe.get("step_id", "")),
            "source_triple_ids": triple_ids,
        })

    # C2: 按 spec_type 聚合问（PT6A 的所有 torque 规范有哪些？等），3 题
    # 收集所有 spec entities 按 type 分组
    spec_by_type = defaultdict(list)
    for ent_id, ent in id2ent.items():
        if ent.get("label") == "Specification":
            stype = ent.get("type", "其他")
            spec_by_type[stype].append(ent_id)

    spec_types_sorted = sorted(spec_by_type.items(), key=lambda x: -len(x[1]))
    for stype, sids in spec_types_sorted[:3]:
        if len(sids) < 2:
            continue
        # 取该 type 下前 4 个 spec
        sids_take = sids[:4]
        spec_lines = []
        for sid in sids_take:
            se = id2ent.get(sid, {})
            spec_lines.append(f"{name_of(se)}：{se.get('value', '')} {se.get('unit', '')}".strip())
        items.append({
            "category": "C_specification",
            "subtype": "spec_by_type",
            "question": f"PT6A 压气机装配涉及的{stype}类技术规范主要有哪些？",
            "gold_answer": f"主要的{stype}规范包括：" + "；".join(spec_lines) + "。",
            "gold_answer_kw": [name_of(id2ent.get(sid, {})) for sid in sids_take]
                              + [id2ent.get(sid, {}).get("value", "") for sid in sids_take],
            "gold_subgraph": {
                "nodes": sids_take,
                "triples": [],
            },
            "source_ata": ata_of(*[id2ent.get(sid, {}).get("source", "") for sid in sids_take]),
            "source_triple_ids": [],
        })

    return items


# ═════════════════════════════════════════════════════════════════════════════
# D 几何配合（19 题）
# ═════════════════════════════════════════════════════════════════════════════
def gen_D(id2ent, idx):
    items = []

    # D1: matesWith 增强（关联 hasInterface 拿 interface_type）
    for t in idx["mates"][:8]:
        pa, pb = id2ent.get(t["head"], {}), id2ent.get(t["tail"], {})
        # 查 head 的 hasInterface
        iface_id = t.get("interface")
        iface_type_str = ""
        if iface_id:
            ie = id2ent.get(iface_id, {})
            itype = ie.get("interface_type", "")
            iname = name_of(ie)
            if itype:
                iface_type_str = f"配合方式：{itype}（{iname}）"
        nodes = [t["head"], t["tail"]]
        triples_sg = [{"head": t["head"], "relation": "matesWith", "tail": t["tail"]}]
        if iface_id:
            nodes.append(iface_id)
            triples_sg.append({"head": t["head"], "relation": "hasInterface", "tail": iface_id})
        ans_main = f"{name_of(pa)} 与 {name_of(pb)} 之间存在配合关系"
        if iface_type_str:
            ans_main += f"，{iface_type_str}"
        else:
            ans_main += "，通过物理接触面对接"
        items.append({
            "category": "D_geometry",
            "subtype": "mates_with",
            "question": f"PT6A 压气机中，{name_of(pa)}（{name_of(pa, 'en')}）与{name_of(pb)}的配合关系是什么？",
            "gold_answer": ans_main + "。",
            "gold_answer_kw": [name_of(pa), name_of(pb)] + ([itype] if iface_id and id2ent.get(iface_id, {}).get("interface_type") else []),
            "gold_subgraph": {"nodes": nodes, "triples": triples_sg},
            "source_ata": ata_of(t.get("source")),
            "source_triple_ids": [t.get("id", "")],
        })

    # D2: hasInterface，5 题（按 part 去重）
    seen_parts = set()
    d2_count = 0
    for part_id, ifaces in idx["part_iface"].items():
        if d2_count >= 5:
            break
        if part_id in seen_parts:
            continue
        seen_parts.add(part_id)
        for iface_id, t in ifaces[:1]:  # 每 part 只取 1 个 interface
            pe, ie = id2ent.get(part_id, {}), id2ent.get(iface_id, {})
            itype = ie.get("interface_type", "装配接口")
            items.append({
                "category": "D_geometry",
                "subtype": "has_interface",
                "question": f"{name_of(pe)}（{name_of(pe, 'en')}）的装配接口属于什么类型？",
                "gold_answer": f"{name_of(pe)}具有{itype}类型的装配接口（{name_of(ie)}）。",
                "gold_answer_kw": [itype, name_of(ie)],
                "gold_subgraph": {
                    "nodes": [part_id, iface_id],
                    "triples": [{"head": part_id, "relation": "hasInterface", "tail": iface_id}],
                },
                "source_ata": ata_of(t.get("source"), pe.get("ata", "")),
                "source_triple_ids": [t.get("id", "")],
            })
            d2_count += 1
            break

    # D3: adjacentTo，3 题（取不同 part_a 的）
    seen = set()
    d3_count = 0
    for t in idx["adjacents"]:
        if d3_count >= 3:
            break
        if t["head"] in seen:
            continue
        seen.add(t["head"])
        pa, pb = id2ent.get(t["head"], {}), id2ent.get(t["tail"], {})
        items.append({
            "category": "D_geometry",
            "subtype": "adjacent_to",
            "question": f"PT6A 压气机装配中，{name_of(pa)}相邻的零件有哪些？",
            "gold_answer": f"{name_of(pa)}与{name_of(pb)}（{name_of(pb, 'en')}）在装配中空间邻接。",
            "gold_answer_kw": [name_of(pb), name_of(pb, "en")],
            "gold_subgraph": {
                "nodes": [t["head"], t["tail"]],
                "triples": [{"head": t["head"], "relation": "adjacentTo", "tail": t["tail"]}],
            },
            "source_ata": ata_of(t.get("source")),
            "source_triple_ids": [t.get("id", "")],
        })
        d3_count += 1

    # D4: constrainedBy + GeoConstraint，3 题
    for iface_id, gc_pairs in list(idx["iface_gc"].items())[:3]:
        for gc_id, t in gc_pairs[:1]:
            ie, ge = id2ent.get(iface_id, {}), id2ent.get(gc_id, {})
            ctype = ge.get("constraint_type", "几何约束")
            items.append({
                "category": "D_geometry",
                "subtype": "constrained_by",
                "question": f"{name_of(ie)}受什么几何约束？该约束在装配中起什么作用？",
                "gold_answer": f"{name_of(ie)}受{ctype}约束（{name_of(ge)}），用于保证装配精度。",
                "gold_answer_kw": [ctype, name_of(ge)],
                "gold_subgraph": {
                    "nodes": [iface_id, gc_id],
                    "triples": [{"head": iface_id, "relation": "constrainedBy", "tail": gc_id}],
                },
                "source_ata": ata_of(t.get("source")),
                "source_triple_ids": [t.get("id", "")],
            })
            break

    return items


def main():
    d, id2ent = load_golden()
    triples = d["triples"]
    print(f"Loaded {len(id2ent)} entities, {len(triples)} triples")

    idx = build_indices(triples)
    print(f"Indices built: child2parent={len(idx['child2parent'])} | "
          f"proc_tools={len(idx['proc_tools'])} | proc_parts={len(idx['proc_parts'])} | "
          f"proc_specs={len(idx['proc_specs'])} | mates={len(idx['mates'])}")

    all_qa = []
    all_qa += gen_A(id2ent, idx)
    all_qa += gen_B(id2ent, idx)
    all_qa += gen_C(id2ent, idx)
    all_qa += gen_D(id2ent, idx)

    # 全局编号 + need_human_check
    for i, q in enumerate(all_qa, 1):
        q["qa_id_global"] = f"Q{i:03d}"
        q["gold_chunk_ids"] = []
        q["need_human_check"] = True
        q["generated_by"] = "tier1-template-v2"

    # 分布统计
    from collections import Counter
    dist_cat = Counter(q["category"] for q in all_qa)
    dist_sub = Counter(f"{q['category']}/{q['subtype']}" for q in all_qa)
    print(f"\nGenerated {len(all_qa)} QA items:")
    for k, v in sorted(dist_cat.items()):
        print(f"  {k}: {v}")
    print("\nSubtype breakdown:")
    for k, v in sorted(dist_sub.items()):
        print(f"  {k}: {v}")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        for q in all_qa:
            f.write(json.dumps(q, ensure_ascii=False) + "\n")
    print(f"\n[OK] Saved: {OUTPUT}")
    print(f"File size: {OUTPUT.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
