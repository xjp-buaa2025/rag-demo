# S1: 任务调研与资料采集 — 方法论

## 目的

把用户的"我要为 X 设计装配方案"模糊请求，翻译为结构化任务说明书，并集中拉取一次参考资料（本地 KG 快照 + Web 联网检索）。本阶段是后续 4 阶段的"输入契约"。

## 关键产物

`stage1.json`：含 subject / kg_snapshot / web_search_results / vision_notes / compliance_scope / task_card_md 六字段。

## 核心方法

### 1. 子系统识别与边界圈定
- 从用户输入提取系统名（中文 + 英文，如 "PT6A HPC" 与 "高压压气机"）
- 识别 scope（如"3 级轴流 + 1 级离心"），明确不在范围内的部分（避免任务无界扩张）
- 识别设计意图：新设计 / 工艺优化 / 复刻 / 故障改进
- 识别约束优先级：可靠性 / 维修性 / 成本 / 重量（最多 2 项 primary）

### 2. KG 快照（本地）
查询 Neo4j 已有该子系统的：
- Part / Assembly 实体计数
- 关键 hasInterface / matesWith 关系样本
- 已知 Procedure 与 Tool 关联

### 3. Web 联网检索（三组并发）
针对子系统名构造 3 类查询：
- 中文 + GJB：找国内标准条款
- 英文 + "assembly procedure"：找国际范例
- 具体型号 + "service bulletin"：找型号变更通告

### 4. 适航/质量体系合规性预筛
基于 subject 类型识别适用条款：
- AS9100D §8.1（风险管理）
- GJB 9001C §7.5（生产服务过程控制）
- 民航：ARP4754A、CCAR-33（发动机适航）
- 军用：GJB 1647A（型号研制规范）

### 5. 视觉素材解析（可选）
若用户上传草图/参考图片，调 Vision LLM 提取语义描述。

## 常见陷阱

- ❌ **scope 模糊**：未明确"哪些不在范围内"——后续 S3 概念设计会无限扩张
- ❌ **设计意图与约束冲突未暴露**：例如声称"工艺优化"但又要求"重新设计架构"
- ❌ **Web 搜索结果直接当事实**：必须经用户审核，标记 `selected: null` 等待审核
- ❌ **忽略本地 KG 已有内容**：导致重复劳动 + 与已有数据不一致

## 产物质量自检 Checklist

- [ ] subject.system 中英文都填写
- [ ] subject.scope 至少 2 项（含一项明确"不包含"）
- [ ] constraints.primary 单值字符串（非数组）
- [ ] kg_snapshot.part_count 为整数（即使 KG 不可用也要返回 0 + warning）
- [ ] web_search_results 每项含 id / url / title / excerpt / confidence / selected:null
- [ ] compliance_scope 至少 1 项
- [ ] task_card_md 含五栏：目标 / 范围 / 边界 / 约束 / 已知风险
