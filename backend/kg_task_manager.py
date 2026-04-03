"""
backend/kg_task_manager.py — 联合 KG 构建任务管理器

KGTaskManager 是单例式的内存任务协调器，用于在三次独立文件上传
（BOM → CAD → 手册）之间保持中间产物，最终触发三源合并写库。

设计约束：
- 最多同时持有 10 个活跃任务
- TTL 7200 秒（2小时），到期后自动驱逐
- 内存存储（不持久化），服务重启后任务丢失属预期行为
"""

from __future__ import annotations

import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional


@dataclass
class KGTask:
    """单次联合 KG 构建任务的中间状态容器。"""

    task_id: str
    created_at: datetime = field(default_factory=datetime.utcnow)

    # 各阶段产出的中间三元组与实体字典
    bom_kg_triples: list[dict] = field(default_factory=list)
    bom_entities: dict = field(default_factory=dict)          # normalize(name) -> {gid, part_id, ...}

    cad_kg_triples: list[dict] = field(default_factory=list)
    cad_entities: dict = field(default_factory=dict)          # normalize(name) -> {gid, cad_part_name, ...}

    kg_triples: list[dict] = field(default_factory=list)      # 手册阶段产出的 kg_triples

    # 已完成的阶段名称集合（"bom" | "cad" | "manual"）
    stages_done: set = field(default_factory=set)


class KGTaskManager:
    """
    联合 KG 构建任务管理器（进程内单例，线程安全）。

    使用方式：
        manager = KGTaskManager(ttl_seconds=7200)
        task_id = manager.create_task()
        manager.store_stage_result(task_id, "bom", pipeline_state)
        initial_state = manager.build_merge_state(task_id)
    """

    MAX_TASKS = 10

    def __init__(self, ttl_seconds: int = 7200) -> None:
        self._tasks: dict[str, KGTask] = {}
        self._lock = threading.Lock()
        self._ttl = timedelta(seconds=ttl_seconds)
        # 启动定期清理（每 15 分钟）
        self._schedule_eviction()

    # ------------------------------------------------------------------
    # 公开 API
    # ------------------------------------------------------------------

    def create_task(self, task_id: Optional[str] = None) -> KGTask:
        """
        创建新任务，返回 KGTask 对象。

        若 task_id 为 None，则自动生成 UUID。
        超过 MAX_TASKS 上限时抛出 RuntimeError。
        """
        with self._lock:
            self._evict_expired_locked()
            if len(self._tasks) >= self.MAX_TASKS:
                raise RuntimeError(
                    f"任务数量已达上限 {self.MAX_TASKS}，请等待现有任务完成或超时后重试。"
                )
            tid = task_id or str(uuid.uuid4())
            if tid in self._tasks:
                raise ValueError(f"task_id={tid!r} 已存在。")
            task = KGTask(task_id=tid)
            self._tasks[tid] = task
            return task

    def get_task(self, task_id: str) -> Optional[KGTask]:
        """查询任务，不存在或已过期则返回 None。"""
        with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                return None
            if self._is_expired(task):
                del self._tasks[task_id]
                return None
            return task

    def store_stage_result(
        self, task_id: str, stage: str, pipeline_state: dict
    ) -> None:
        """
        将某阶段管道运行完毕后的 state 存入任务。

        stage: "bom" | "cad" | "manual"
        pipeline_state: LangGraph 最终 state 字典（直接传入，无需序列化）
        """
        with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                raise KeyError(f"task_id={task_id!r} 不存在或已超时。")
            if self._is_expired(task):
                del self._tasks[task_id]
                raise KeyError(f"task_id={task_id!r} 已超时，结果无法保存。")

            if stage == "bom":
                task.bom_kg_triples = pipeline_state.get("bom_kg_triples") or []
                task.bom_entities   = pipeline_state.get("bom_entities")   or {}
            elif stage == "cad":
                task.cad_kg_triples = pipeline_state.get("cad_kg_triples") or []
                task.cad_entities   = pipeline_state.get("cad_entities")   or {}
            elif stage == "manual":
                task.kg_triples = pipeline_state.get("kg_triples") or []
            else:
                raise ValueError(f"未知 stage={stage!r}，合法值为 bom/cad/manual。")

            task.stages_done.add(stage)

    def build_merge_state(self, task_id: str) -> dict:
        """
        根据已存储的各阶段产物，构造可直接传入联合管道 merge 阶段的 initial_state。

        返回的 dict 包含 kg_task_stage="merge" 以及三源中间数据。
        调用方负责将此 dict 作为 unified pipeline 的 initial_state 传入。
        """
        with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                raise KeyError(f"task_id={task_id!r} 不存在或已超时。")
            if self._is_expired(task):
                del self._tasks[task_id]
                raise KeyError(f"task_id={task_id!r} 已超时。")

            return {
                "kg_task_id":     task.task_id,
                "kg_task_stage":  "merge",
                "bom_kg_triples": list(task.bom_kg_triples),
                "bom_entities":   dict(task.bom_entities),
                "cad_kg_triples": list(task.cad_kg_triples),
                "cad_entities":   dict(task.cad_entities),
                "kg_triples":     list(task.kg_triples),
                # merge 阶段需要知道哪些源已就绪
                "stages_done":    set(task.stages_done),
                "log_messages":   [],
            }

    def get_status(self, task_id: str) -> Optional[dict]:
        """
        返回任务状态摘要，用于 GET /kg/task/{id}/status 端点。

        返回格式：
        {
            "task_id": str,
            "stages_done": list[str],
            "created_at": str (ISO),
            "expires_at": str (ISO),
        }
        """
        task = self.get_task(task_id)
        if task is None:
            return None
        expires_at = task.created_at + self._ttl
        return {
            "task_id":     task.task_id,
            "stages_done": sorted(task.stages_done),
            "created_at":  task.created_at.isoformat() + "Z",
            "expires_at":  expires_at.isoformat() + "Z",
        }

    # ------------------------------------------------------------------
    # 内部工具
    # ------------------------------------------------------------------

    def _is_expired(self, task: KGTask) -> bool:
        return datetime.utcnow() - task.created_at > self._ttl

    def _evict_expired_locked(self) -> None:
        """调用前必须已持有 self._lock。"""
        expired = [tid for tid, t in self._tasks.items() if self._is_expired(t)]
        for tid in expired:
            del self._tasks[tid]

    def _evict_expired(self) -> None:
        """定时清理入口（由 Timer 触发，自动续期）。"""
        with self._lock:
            self._evict_expired_locked()
        self._schedule_eviction()

    def _schedule_eviction(self) -> None:
        """每 15 分钟触发一次过期任务清理。"""
        t = threading.Timer(900, self._evict_expired)
        t.daemon = True   # 不阻止进程退出
        t.start()
