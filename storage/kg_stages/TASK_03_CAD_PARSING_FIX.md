# Task 03: Stage 3 CAD 解析修复 + 零件检测

## 问题
Stage 3 从两个 STEP 文件（合计 101MB）仅提取了 56 条匿名 `matesWith` 关系：
- `assembly_nodes: 0` — 装配树完全没有提取
- `adjacency: 0` — 空间邻接没有计算
- 零件名全是 `Part_283904` 格式的匿名 ID
- 与 BOM/Manual 零件 0% 对齐

## 前置检查
首先确认 pythonocc-core 是否安装：
```bash
conda activate rag_demo
conda list | grep -i occ
python -c "from OCC.Core.STEPControl import STEPControl_Reader; print('OCC OK')"
```
如果没装，这是最大原因。安装方法：
```bash
conda install -c conda-forge pythonocc-core
```

## 涉及文件
- `backend/pipelines/nodes_cad.py` — CAD 解析核心逻辑

## 改动要点

### 1. 确保 OCC 路径被正确使用
检查代码中 `HAS_OCC` 的判断逻辑，确保在 OCC 可用时走完整解析路径：
- 装配树提取（NAUO → 父子关系）
- 约束提取（GEOMETRIC_TOLERANCE）
- 空间邻接（BoundingBox gap < 2mm）

### 2. 从 STEP PRODUCT 实体提取更多信息
STEP 文件的 PRODUCT 实体格式：
```
#12 = PRODUCT('Part_283904', 'Compressor Blade Stage 1', '', (#context));
```
- 第一个参数是 `name`（可能是匿名 ID）
- **第二个参数是 `description`**（可能包含有意义的名称！）

修改解析逻辑，优先使用 description，fallback 到 name：
```python
def _extract_product_info(step_reader):
    """提取 PRODUCT 的 name 和 description"""
    # 如果 description 非空且不是通用占位符，优先使用
    product_name = description if description and description != '' else name
```

### 3. 利用 OCC 提取几何特征
即使名称是匿名的，几何特征仍有辨识价值：
```python
from OCC.Core.GProp import GProp_GProps
from OCC.Core.BRepGProp import brepgprop_VolumeProperties, brepgprop_SurfaceProperties
from OCC.Core.Bnd import Bnd_Box
from OCC.Core.BRepBndLib import brepbndlib_Add

def _extract_geometry_features(shape):
    """提取零件的几何特征用于匹配"""
    props = GProp_GProps()
    brepgprop_VolumeProperties(shape, props)
    volume = props.Mass()
    
    bbox = Bnd_Box()
    brepbndlib_Add(shape, bbox)
    xmin, ymin, zmin, xmax, ymax, zmax = bbox.Get()
    
    return {
        'volume': volume,
        'bbox_dims': sorted([xmax-xmin, ymax-ymin, zmax-zmin]),  # 排序后尺寸无关方向
        'surface_area': ...,
        'centroid': (props.CentreOfMass().X(), ...),
    }
```

### 4. 零件自动分类（形状启发式）
通过几何特征启发式分类零件类型：
```python
def _classify_part_by_geometry(features):
    dims = features['bbox_dims']  # [最小, 中间, 最大]
    aspect_ratio = dims[2] / max(dims[0], 0.001)
    flatness = dims[0] / max(dims[1], 0.001)
    
    if aspect_ratio > 10:
        return "Bolt/Shaft"  # 细长件
    elif flatness < 0.1 and aspect_ratio < 3:
        return "Disk/Ring"   # 扁平圆形件
    elif volume < threshold_small:
        return "Fastener"    # 小件（螺栓螺母垫圈）
    else:
        return "Housing/Casing"  # 大件
```

### 5. CAD→BOM 拓扑结构对齐
名称对齐失败时，用装配树拓扑做结构对齐：
- 提取 CAD 装配树中每个节点的：子节点数、深度、兄弟节点数
- 提取 BOM 层级中每个节点的同样特征（依赖 Task 01 完成）
- 用匈牙利算法做最优匹配

## 验证标准
- `assembly_nodes > 0`（装配树非空）
- 至少部分零件有非匿名名称（来自 PRODUCT description）
- adjacency 关系数 > 0
- 几何特征成功提取（有 volume/bbox 数据）

## 依赖
- 依赖 Task 01 完成（BOM 有层级后才能做拓扑对齐）
- 需要 pythonocc-core 环境

## 预计工作量
大（约 2-4 小时），其中几何特征提取和分类是探索性工作
