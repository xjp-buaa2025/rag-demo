# S3: 概念 / 架构设计 — 方法论（outline v1）

## 目的
在 S2 指标约束下，给出 3-5 个备选概念架构（模块划分 + 接口 + 装配单元），含装配仿真预检。

## 核心方法（v1 待补完整内容）
1. **功能-结构映射**：S2 engineering_metrics → 功能模块 → 物理组件
2. **装配树推导**：基于 KG isPartOf + matesWith 推导可行模块边界
3. **装配仿真预检**：KG/CAD 静态可达性分析（v2 升级到动态仿真）
4. **基准统一性审查**：工艺基准 / 装配基准 / 检测基准三者关系

## 产物字段
candidate_architectures（每个含 modules / key_interfaces / assembly_simulation / pros / cons / fit_score）/ recommended / rationale_md

## 留待 v2 完善
- 详细的 fit_score 计算
- 装配仿真接入 DELMIA/Process Simulate
