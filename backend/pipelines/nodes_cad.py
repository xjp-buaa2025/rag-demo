"""
backend/pipelines/nodes_cad.py — CAD 模型解析管道节点

make_cad_nodes(app_state, neo4j_cfg) -> dict

2 个 LangGraph 节点：
  parse_cad_step    — 解析 STEP/STP 文件，提取装配树、配合约束、空间邻接关系
  cad_to_kg_triples — 将 CAD 结构数据规则转换为 KG 三元组并写入 Neo4j

依赖：
  pythonocc-core（Open CASCADE Python 绑定）
  安装方式：conda install -c conda-forge pythonocc-core

对应技术路线.md 第 1.3 节 / 模块2.3 节 / 模块4（isPartOf/matesWith/adjacentTo 三类关系）
"""

from __future__ import annotations

import re
from typing import Any


def make_cad_nodes(app_state: Any, neo4j_cfg: dict) -> dict:
    """工厂函数：创建 CAD 解析管道节点，通过闭包绑定 neo4j_cfg。"""

    def parse_cad_step(state: dict) -> dict:
        """
        节点1：解析 STEP 文件，提取三类数据。

        输出：
          cad_assembly_tree  — 嵌套 dict 装配层级树
          cad_constraints    — 配合约束列表 [{part_a, part_b, constraint_type, interface}]
          cad_adjacency      — 空间邻接列表 [{part_a, part_b, gap_mm}]
        """
        # ── 软检测 OCC 可用性，决定走哪条路径 ──────────────────────────────
        _occ_available = False
        try:
            from OCC.Core.STEPControl import STEPControl_Reader
            from OCC.Core.IFSelect import IFSelect_RetDone
            _occ_available = True
        except ImportError:
            pass

        file_path = state.get("file_path", "")
        if not file_path:
            return {
                "error": "file_path 为空",
                "log_messages": ["[CAD] file_path 为空，跳过解析"],
                "current_node": "parse_cad_step",
            }

        # ── Path B：无 OCC，纯文本 fallback ────────────────────────────────
        if not _occ_available:
            try:
                assembly_tree = _parse_step_tree_from_text(file_path)
                constraints   = _parse_step_constraints(file_path)
                adjacency     = []   # 需要 OCC Reader，无法 fallback
                log_msg = (
                    f"[CAD][FALLBACK] pythonocc-core 不可用，已降级为纯文本解析模式。"
                    f"装配节点 {_count_tree_nodes(assembly_tree)} 个，"
                    f"配合约束 {len(constraints)} 条，邻接关系 0 条（需 OCC）"
                )
                return {
                    "cad_assembly_tree": assembly_tree,
                    "cad_constraints":   constraints,
                    "cad_adjacency":     adjacency,
                    "log_messages":      [log_msg],
                    "current_node":      "parse_cad_step",
                }
            except Exception as e:
                return {
                    "error": str(e),
                    "log_messages": [f"[CAD][FALLBACK] 纯文本解析异常：{e}"],
                    "current_node": "parse_cad_step",
                }

        # ── Path A：有 OCC，完整流程 ────────────────────────────────────────
        try:
            reader = STEPControl_Reader()
            status = reader.ReadFile(file_path)
            if status != IFSelect_RetDone:
                return {
                    "error": f"STEP 文件读取失败，状态码：{status}",
                    "log_messages": [f"[CAD][OCC] STEP 文件读取失败：{file_path}"],
                    "current_node": "parse_cad_step",
                }
            reader.TransferRoots()

            # Step1: 装配树（从 STEP 文本中提取 NAUO 层级关系）
            assembly_tree = _parse_step_tree_from_text(file_path)

            # Step2: 配合约束（从 STEP 文本解析 NAUO + GEOMETRIC_TOLERANCE）
            constraints = _parse_step_constraints(file_path)

            # Step3: 空间邻接（基于包围盒重叠检测，需要 OCC Reader）
            adjacency = _parse_step_adjacency(reader, file_path)

            # Step4: 几何特征提取（体积/面积/包围盒/形心）+ 启发式分类
            cad_geometry: dict = {}
            nb = reader.NbRootsForTransfer()
            if nb > 0:
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as _f:
                        _content = _f.read()
                    _pd_names = list(_build_step_name_chain(_content).values())
                except Exception:
                    _pd_names = []
                for i in range(1, nb + 1):
                    shape   = reader.Shape(i)
                    name    = _pd_names[i - 1] if i - 1 < len(_pd_names) else f"Component_{i}"
                    feats   = _extract_geometry_features(shape)
                    if feats:
                        feats["part_type"] = _classify_part_by_geometry(feats)
                        cad_geometry[name] = feats

            log_msg = (
                f"[CAD][OCC] STEP 解析完成：装配节点 {_count_tree_nodes(assembly_tree)} 个，"
                f"配合约束 {len(constraints)} 条，邻接关系 {len(adjacency)} 条，"
                f"几何特征 {len(cad_geometry)} 个零件"
            )
            return {
                "cad_assembly_tree": assembly_tree,
                "cad_constraints":   constraints,
                "cad_adjacency":     adjacency,
                "cad_geometry":      cad_geometry,
                "log_messages":      [log_msg],
                "current_node":      "parse_cad_step",
            }

        except Exception as e:
            return {
                "error": str(e),
                "log_messages": [f"[CAD][OCC] STEP 解析异常：{e}"],
                "current_node": "parse_cad_step",
            }

    def cad_to_kg_triples(state: dict) -> dict:
        """
        节点2：将 CAD 数据转换为 KG 三元组。

        双路径输出（向后兼容）：
        1. 若管道有 neo4j_cfg 且非联合KG管道（kg_task_stage 未设置），
           保留直写 Neo4j 行为（旧 /bom/pipeline 端点不受影响）。
        2. 无论如何，都将三元组填入 state["cad_kg_triples"] 和 state["cad_entities"]，
           供联合 KG 管道的 merge 阶段消费。

        生成关系：
          isPartOf   — 装配树层级
          matesWith  — 配合约束（含属性：constraint_type, interface）
          adjacentTo — 空间邻接（含属性：gap_mm）
          hasInterface — 零件拥有配合接口
          constrainedBy — 接口受几何约束
        """
        assembly_tree = state.get("cad_assembly_tree") or {}
        constraints   = state.get("cad_constraints")   or []
        adjacency     = state.get("cad_adjacency")     or []

        if not assembly_tree and not constraints and not adjacency:
            return {
                "cad_kg_triples": [],
                "cad_entities":   {},
                "log_messages":   ["[CAD] 无 CAD 数据，跳过 KG 写入"],
                "current_node":   "cad_to_kg_triples",
            }

        # ── 生成标准三元组（供联合KG管道消费）──
        try:
            from backend.pipelines.nodes_kg_unified import make_unified_kg_nodes as _make_unified
            _unified_nodes = _make_unified(app_state, neo4j_cfg)
            _triple_result = _unified_nodes["cad_to_triples"](state)
            cad_kg_triples = _triple_result.get("cad_kg_triples", [])
            cad_entities   = _triple_result.get("cad_entities",   {})
        except Exception as _te:
            cad_kg_triples = []
            cad_entities   = {}

        # ── 旧路径：联合KG管道的 cad/merge 阶段不直写库，其他场景仍直写 ──
        kg_task_stage = state.get("kg_task_stage", "")
        log_msg = ""
        if kg_task_stage not in ("cad", "merge"):
            try:
                from neo4j import GraphDatabase
                driver = GraphDatabase.driver(
                    neo4j_cfg.get("uri",  "bolt://localhost:7687"),
                    auth=(neo4j_cfg.get("user", "neo4j"), neo4j_cfg.get("pass", "neo4j")),
                )
                nodes_written = 0
                rels_written  = 0
                with driver.session() as session:
                    nodes_written, rels_written = _write_cad_to_neo4j(
                        session, assembly_tree, constraints, adjacency
                    )
                driver.close()
                log_msg = f"[CAD] KG 写入完成：节点 {nodes_written} 个，关系 {rels_written} 条"
            except Exception as e:
                log_msg = f"[CAD] KG 写入失败：{e}"
        else:
            log_msg = f"[CAD] 联合KG模式：跳过直写，生成 {len(cad_kg_triples)} 批三元组"

        return {
            "cad_kg_triples": cad_kg_triples,
            "cad_entities":   cad_entities,
            "log_messages":   [log_msg],
            "current_node":   "cad_to_kg_triples",
        }

    return {
        "parse_cad_step":    parse_cad_step,
        "cad_to_kg_triples": cad_to_kg_triples,
    }


# ── CAD 解析辅助函数 ─────────────────────────────────────────────────────────

def _build_step_name_chain(content: str) -> dict:
    """
    建立 PRODUCT_DEFINITION 引用 → 零件名称 的映射链。

    STEP AP203 装配引用链：
      PRODUCT_DEFINITION → PRODUCT_DEFINITION_FORMATION(_WITH_SPECIFIED_SOURCE) → PRODUCT

    NAUO 的第4/5个参数是 PRODUCT_DEFINITION 的引用，所以需要走完整链。
    零件名优先使用 PRODUCT 的 description（第2参数），fallback 到 name（第1参数）。
    """
    # Step1: PRODUCT ref → (name, description)
    prod_re = re.compile(
        r"#(\d+)\s*=\s*PRODUCT\s*\(\s*'([^']*)'\s*,\s*'([^']*)'",
        re.IGNORECASE,
    )
    products: dict = {}  # prod_ref → (name, desc)
    for m in prod_re.finditer(content):
        products[m.group(1)] = (m.group(2).strip(), m.group(3).strip())

    # Step2: PRODUCT_DEFINITION_FORMATION / _WITH_SPECIFIED_SOURCE → PRODUCT
    form_re = re.compile(
        r"#(\d+)\s*=\s*PRODUCT_DEFINITION_FORMATION(?:_WITH_SPECIFIED_SOURCE)?"
        r"\s*\(\s*'[^']*'\s*,\s*'[^']*'\s*,\s*#(\d+)",
        re.IGNORECASE,
    )
    formations: dict = {}  # form_ref → prod_ref
    for m in form_re.finditer(content):
        formations[m.group(1)] = m.group(2)

    # Step3: PRODUCT_DEFINITION → PRODUCT_DEFINITION_FORMATION
    pd_re = re.compile(
        r"#(\d+)\s*=\s*PRODUCT_DEFINITION\s*\(\s*'[^']*'\s*,\s*'[^']*'\s*,\s*#(\d+)",
        re.IGNORECASE,
    )
    pd_name_map: dict = {}  # pd_ref → part_name
    for m in pd_re.finditer(content):
        pd_ref   = m.group(1)
        form_ref = m.group(2)
        prod_ref = formations.get(form_ref)
        if prod_ref and prod_ref in products:
            name, desc = products[prod_ref]
            # description 优先（如 'Compressor Blade'），fallback 到 name
            final = desc if desc and desc not in ("", " ") else name
            pd_name_map[pd_ref] = final or f"Part_{pd_ref}"
        else:
            pd_name_map[pd_ref] = f"Part_{pd_ref}"

    return pd_name_map


def _parse_step_tree_from_text(file_path: str) -> dict:
    """
    从 STEP 文件文本中解析 NEXT_ASSEMBLY_USAGE_OCCURRENCE（NAUO）建立父子树。
    返回格式：{parent_name: {child_name: {}, ...}, ...}

    修复：NAUO 的父子参数是 PRODUCT_DEFINITION 引用，需经三级映射链解析为零件名。
    """
    parent_map: dict = {}   # child_name → parent_name

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        pd_name_map = _build_step_name_chain(content)

        # NAUO 格式：NEXT_ASSEMBLY_USAGE_OCCURRENCE ( 'id', ' ', ' ', #parent_pd, #child_pd, $ )
        nauo_re = re.compile(
            r"NEXT_ASSEMBLY_USAGE_OCCURRENCE\s*\(\s*'[^']*'\s*,\s*'[^']*'\s*,\s*'[^']*'\s*,\s*#(\d+)\s*,\s*#(\d+)",
            re.IGNORECASE,
        )
        for m in nauo_re.finditer(content):
            parent_name = pd_name_map.get(m.group(1), f"Part_{m.group(1)}")
            child_name  = pd_name_map.get(m.group(2), f"Part_{m.group(2)}")
            parent_map[child_name] = parent_name

    except Exception:
        pass

    # ── 数字名前缀补全 ─────────────────────────────────────────────────────
    # C52696C 的子零件 PRODUCT name/description 均为纯数字（'10'、'180-blade'）。
    # 找到根节点（无父节点的节点）作为前缀，将数字名改为 {root}-{name} 格式。
    if parent_map:
        _all = set(parent_map.keys()) | set(parent_map.values())
        _roots = _all - set(parent_map.keys())
        _top = next(iter(_roots), "")
        _NUMERIC_RE = re.compile(r'^\d[\d\-a-zA-Z]*$')
        # 只有当根节点名本身不是数字时才补全（避免误处理）
        if _top and not _NUMERIC_RE.match(_top):
            def _fix(name: str) -> str:
                return f"{_top}-{name}" if _NUMERIC_RE.match(name) else name
            parent_map = {_fix(c): _fix(p) for c, p in parent_map.items()}

    if not parent_map:
        return {"root": {}}

    # 构建嵌套树
    all_names  = set(parent_map.keys()) | set(parent_map.values())
    roots      = all_names - set(parent_map.keys())

    def _build(name: str) -> dict:
        return {child: _build(child) for child, p in parent_map.items() if p == name}

    tree = {root: _build(root) for root in roots}
    return tree if tree else {"root": {}}


def _parse_step_constraints(file_path: str) -> list:
    """
    从 STEP 文本中解析配合约束（NAUO 关系 + GEOMETRIC_TOLERANCE）。
    返回：[{part_a, part_b, constraint_type, interface}, ...]

    修复：使用 _build_step_name_chain 正确解析 PRODUCT_DEFINITION 引用链。
    """
    constraints = []
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        pd_name_map = _build_step_name_chain(content)

        # NAUO → assembly 配合
        nauo_re = re.compile(
            r"NEXT_ASSEMBLY_USAGE_OCCURRENCE\s*\(\s*'[^']*'\s*,\s*'[^']*'\s*,\s*'[^']*'\s*,\s*#(\d+)\s*,\s*#(\d+)",
            re.IGNORECASE,
        )
        seen = set()
        for m in nauo_re.finditer(content):
            pa = pd_name_map.get(m.group(1), f"Part_{m.group(1)}")
            pb = pd_name_map.get(m.group(2), f"Part_{m.group(2)}")
            key = (pa, pb)
            if key not in seen:
                seen.add(key)
                constraints.append({
                    "part_a":          pa,
                    "part_b":          pb,
                    "constraint_type": "assembly",
                    "interface":       "",
                })

        # GEOMETRIC_TOLERANCE → 几何公差约束
        geo_re = re.compile(
            r"GEOMETRIC_TOLERANCE\s*\(\s*'([^']*)'", re.IGNORECASE
        )
        for m in geo_re.finditer(content):
            tol_name = m.group(1).strip()
            if tol_name:
                constraints.append({
                    "part_a":          tol_name,
                    "part_b":          "",
                    "constraint_type": "geometric_tolerance",
                    "interface":       tol_name,
                })

    except Exception:
        pass

    return constraints


def _parse_step_adjacency(reader, file_path: str = "") -> list:
    """
    基于包围盒（Bounding Box）重叠检测物理相邻零件。
    间距 < 2mm 视为邻接。

    修复：STEP AP203 的 OCC Reader 只返回 1 个根 Compound Shape，
    需要遍历顶级子形状（TopoDS_Iterator）才能得到各零件的包围盒。
    子形状命名采用 Comp_{i} 格式，并尝试映射到装配树中的零件名（近似对应）。
    """
    adjacency = []
    try:
        from OCC.Core.BRepBndLib import brepbndlib
        from OCC.Core.Bnd import Bnd_Box
        from OCC.Core.TopoDS import TopoDS_Iterator

        # 遍历根 Shape 的顶级子形状
        root_shape = reader.Shape(1)
        sub_shapes = []
        it = TopoDS_Iterator(root_shape)
        while it.More():
            sub_shapes.append(it.Value())
            it.Next()

        # 若 root 本身无子形状（整体装配体），直接用 NbRoots 逐个读取
        if not sub_shapes:
            nb = reader.NbRootsForTransfer()
            sub_shapes = [reader.Shape(i) for i in range(1, nb + 1)]

        bbox_list = []
        for i, shape in enumerate(sub_shapes, start=1):
            bbox = Bnd_Box()
            brepbndlib.Add(shape, bbox)
            coords = bbox.Get()  # returns list [xmin,ymin,zmin,xmax,ymax,zmax]
            name = f"Comp_{i}"
            bbox_list.append((name, coords[0], coords[1], coords[2], coords[3], coords[4], coords[5]))

        GAP_THRESHOLD = 2.0
        for i, (n1, x1n, y1n, z1n, x1x, y1x, z1x) in enumerate(bbox_list):
            for n2, x2n, y2n, z2n, x2x, y2x, z2x in bbox_list[i + 1:]:
                gap_x = max(0.0, max(x1n, x2n) - min(x1x, x2x))
                gap_y = max(0.0, max(y1n, y2n) - min(y1x, y2x))
                gap_z = max(0.0, max(z1n, z2n) - min(z1x, z2x))
                gap = (gap_x ** 2 + gap_y ** 2 + gap_z ** 2) ** 0.5
                if gap < GAP_THRESHOLD:
                    adjacency.append({
                        "part_a": n1,
                        "part_b": n2,
                        "gap_mm": round(gap, 3),
                    })
    except Exception:
        pass
    return adjacency


def _extract_geometry_features(shape) -> dict:
    """
    从 OCC Shape 提取几何特征，用于零件分类与 BOM 对齐。
    使用兼容 pythonocc-core 7.7.x 的 brepgprop 静态方法。
    """
    try:
        from OCC.Core.BRepGProp import brepgprop
        from OCC.Core.GProp import GProp_GProps
        from OCC.Core.BRepBndLib import brepbndlib
        from OCC.Core.Bnd import Bnd_Box

        props = GProp_GProps()
        brepgprop.VolumeProperties(shape, props)
        volume = props.Mass()

        surf_props = GProp_GProps()
        brepgprop.SurfaceProperties(shape, surf_props)
        surface_area = surf_props.Mass()

        cog = props.CentreOfMass()

        bbox = Bnd_Box()
        brepbndlib.Add(shape, bbox)
        coords = bbox.Get()  # returns list [xmin,ymin,zmin,xmax,ymax,zmax]
        xmin, ymin, zmin, xmax, ymax, zmax = coords[0], coords[1], coords[2], coords[3], coords[4], coords[5]
        dims = sorted([abs(xmax - xmin), abs(ymax - ymin), abs(zmax - zmin)])

        return {
            "volume":       round(volume,       3),
            "surface_area": round(surface_area, 3),
            "bbox_dims":    [round(d, 3) for d in dims],
            "centroid":     (round(cog.X(), 3), round(cog.Y(), 3), round(cog.Z(), 3)),
        }
    except Exception:
        return {}


def _classify_part_by_geometry(features: dict) -> str:
    """
    启发式形状分类：通过包围盒长宽比和体积判断零件类型。
    dims 已排序为 [最小, 中间, 最大]。
    """
    dims   = features.get("bbox_dims", [])
    volume = features.get("volume", 0)
    if not dims or len(dims) < 3:
        return "Unknown"

    aspect_ratio = dims[2] / max(dims[0], 0.001)  # 长轴/短轴
    flatness     = dims[0] / max(dims[1], 0.001)  # 最薄维度比

    if aspect_ratio > 10:
        return "Bolt/Shaft"       # 细长件
    if flatness < 0.1 and aspect_ratio < 3:
        return "Disk/Ring"        # 扁平圆形件
    if volume < 500:
        return "Fastener"         # 小件（螺栓螺母垫圈）
    if volume > 500000:
        return "Housing/Casing"   # 大件
    return "General_Part"


def _count_tree_nodes(tree: dict, count: int = 0) -> int:
    """递归计算装配树节点总数。"""
    for v in tree.values():
        count += 1
        if isinstance(v, dict):
            count = _count_tree_nodes(v, count)
    return count


# ── Neo4j 写入 ────────────────────────────────────────────────────────────────

def _write_cad_to_neo4j(
    session,
    assembly_tree: dict,
    constraints: list,
    adjacency: list,
) -> tuple[int, int]:
    """将 CAD 三类数据写入 Neo4j，返回 (nodes_written, relations_written)。"""
    nodes_written = 0
    rels_written  = 0

    # ── isPartOf（装配树层级）────────────────────────────────
    iso_triples = _tree_to_isPartOf(assembly_tree)
    if iso_triples:
        try:
            session.run("""
                UNWIND $triples AS t
                MERGE (child:Part {part_name: t.child})
                  ON CREATE SET child.part_id = 'CAD_' + t.child,
                                child.source  = 'CAD'
                MERGE (parent:Assembly {part_name: t.parent})
                  ON CREATE SET parent.part_id = 'CAD_' + t.parent,
                                parent.source  = 'CAD'
                MERGE (child)-[:isPartOf]->(parent)
            """, triples=iso_triples)
            nodes_written += len(iso_triples) * 2
            rels_written  += len(iso_triples)
        except Exception:
            pass

    # ── matesWith（配合约束）─────────────────────────────────
    mates = [c for c in constraints if c.get("part_a") and c.get("part_b")]
    if mates:
        try:
            session.run("""
                UNWIND $mates AS m
                MERGE (a:Part {part_name: m.part_a})
                MERGE (b:Part {part_name: m.part_b})
                MERGE (a)-[:matesWith {
                    constraint_type: m.constraint_type,
                    interface:        m.interface
                }]->(b)
            """, mates=mates)
            rels_written += len(mates)
        except Exception:
            pass

    # ── adjacentTo（空间邻接）────────────────────────────────
    if adjacency:
        try:
            session.run("""
                UNWIND $adj AS a
                MERGE (x:Part {part_name: a.part_a})
                MERGE (y:Part {part_name: a.part_b})
                MERGE (x)-[:adjacentTo {gap_mm: a.gap_mm}]->(y)
            """, adj=adjacency)
            rels_written += len(adjacency)
        except Exception:
            pass

    return nodes_written, rels_written


def _tree_to_isPartOf(tree: dict, parent: str | None = None) -> list:
    """将装配树递归转换为 [{child, parent}, ...] 三元组列表。"""
    triples = []
    for name, subtree in tree.items():
        if parent:
            triples.append({"child": name, "parent": parent})
        if isinstance(subtree, dict) and subtree:
            triples.extend(_tree_to_isPartOf(subtree, parent=name))
    return triples
