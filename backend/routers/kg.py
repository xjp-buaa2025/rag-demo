"""
backend/routers/kg.py — 联合 KG 构建 HTTP 端点

四个端点：

  POST /kg/task/create
      创建新任务，返回 task_id。

  POST /kg/task/{task_id}/upload
      上传单文件并处理（stage=bom|cad|manual），返回 SSE 日志流。

  POST /kg/task/{task_id}/merge
      触发三源合并 + 写库（SSE 日志流）。

  GET  /kg/task/{task_id}/status
      查询各阶段完成情况（JSON）。
"""

import os
import tempfile
import queue
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse

from backend.sse import log_gen_to_sse
from backend.routers.ingest import get_state   # 复用现有 Depends
from backend.state import AppState

router = APIRouter()


def _get_neo4j_cfg(request: Request) -> dict:
    return getattr(request.app.state, "neo4j_cfg", {})


# ─────────────────────────────────────────────
# POST /kg/task/create
# ─────────────────────────────────────────────

@router.post("/task/create", summary="创建联合KG构建任务")
def kg_task_create(
    request: Request,
    state: AppState = Depends(get_state),
):
    """
    创建新的联合 KG 构建任务，返回 task_id。
    后续三次 upload 调用（bom/cad/manual）共享同一 task_id，
    最后调用 merge 端点触发三源合并写库。
    """
    manager = state.kg_task_manager
    if manager is None:
        raise HTTPException(status_code=503, detail="KGTaskManager 未初始化，服务不可用")

    try:
        task_id = str(uuid.uuid4())
        manager.create_task(task_id)
        return JSONResponse({"task_id": task_id, "status": "created"})
    except RuntimeError as e:
        raise HTTPException(status_code=429, detail=str(e))


# ─────────────────────────────────────────────
# POST /kg/task/{task_id}/upload
# ─────────────────────────────────────────────

@router.post("/task/{task_id}/upload", summary="上传文件并处理（SSE）")
def kg_task_upload(
    request: Request,
    task_id: str,
    stage: str = Form(..., description="处理阶段：bom | cad | manual"),
    file: Optional[UploadFile] = File(default=None),
    clear_first: bool = Form(default=False),
    state: AppState = Depends(get_state),
):
    """
    上传单个文件，在联合 KG 管道中按 stage 处理，结果存入任务。
    stage: "bom" | "cad" | "manual"
    响应为 SSE 日志流；处理完成后自动调用 store_stage_result。
    """

    manager = state.kg_task_manager
    if manager is None:
        raise HTTPException(status_code=503, detail="KGTaskManager 未初始化")

    task = manager.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"task_id={task_id!r} 不存在或已超时")

    pipeline = state.lg_kg_pipeline
    if pipeline is None:
        raise HTTPException(status_code=503, detail="联合 KG 管道未初始化")

    valid_stages = {"bom", "cad", "manual"}
    if stage not in valid_stages:
        raise HTTPException(
            status_code=400,
            detail=f"stage 参数非法：{stage!r}，合法值为 {sorted(valid_stages)}"
        )

    # 保存上传文件到临时目录
    if file is None:
        raise HTTPException(status_code=400, detail="缺少上传文件")

    suffix = os.path.splitext(file.filename or "")[-1] or ".tmp"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    try:
        content = file.file.read()
        tmp.write(content)
        tmp.flush()
        tmp_path = tmp.name
    finally:
        tmp.close()

    file_ext = suffix.lstrip(".").lower()

    initial_state = {
        "file_path":      tmp_path,
        "file_ext":       file_ext,
        "pipeline_mode":  "kg",
        "kg_task_id":     task_id,
        "kg_task_stage":  stage,
        "clear_first":    clear_first,
        "log_messages":   [f"[KG-Upload] stage={stage}, file={file.filename}"],
    }

    progress_q = queue.Queue()
    state._ingest_progress_q = progress_q
    final_state_holder: list = []   # 通过列表在嵌套函数中共享 final_state

    def _run_pipeline_bg():
        """后台线程：invoke 管道，将日志和 final_state 推入队列。"""
        import threading as _t
        _SENTINEL_BG = object()
        try:
            fs = pipeline.invoke(initial_state)
            final_state_holder.append(fs)
            # 将 final_state 中的日志推入进度队列
            for msg in fs.get("log_messages", []):
                progress_q.put(("log", msg))
        except Exception as e:
            progress_q.put(("log", f"[KG-Upload] ❌ 管道异常: {e}"))
        finally:
            progress_q.put((_SENTINEL_BG, None))
            # 存储阶段产物
            try:
                if final_state_holder:
                    manager.store_stage_result(task_id, stage, final_state_holder[0])
            except Exception:
                pass
            try:
                os.unlink(tmp_path)
            except Exception:
                pass
            state._ingest_progress_q = None

    import threading as _threading
    _SENTINEL_MAIN = object()

    def _run_and_store():
        all_logs: list[str] = []
        t = _threading.Thread(target=_run_pipeline_bg, daemon=True)
        t.start()
        while True:
            try:
                kind, msg = progress_q.get(timeout=900)
            except queue.Empty:
                all_logs.append("[KG-Upload] ⚠ 等待超时（15min）")
                yield "\n".join(all_logs)
                break
            # 检查是否遇到哨兵（任意 kind 为非字符串对象）
            if not isinstance(kind, str):
                break
            all_logs.append(msg)
            yield "\n".join(all_logs)
        t.join(timeout=5)
        if not all_logs:
            yield f"[KG-Upload] stage={stage} 处理完成（无日志输出）"

    return log_gen_to_sse(_run_and_store())


# ─────────────────────────────────────────────
# POST /kg/task/{task_id}/merge
# ─────────────────────────────────────────────

@router.post("/task/{task_id}/merge", summary="触发三源合并写库（SSE）")
def kg_task_merge(
    request: Request,
    task_id: str,
    state: AppState = Depends(get_state),
):
    """
    使用任务中已存储的 BOM/CAD/手册三源中间产物，触发合并+对齐+写库。
    响应为 SSE 日志流。
    """

    manager = state.kg_task_manager
    if manager is None:
        raise HTTPException(status_code=503, detail="KGTaskManager 未初始化")

    task = manager.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"task_id={task_id!r} 不存在或已超时")

    pipeline = state.lg_kg_pipeline
    if pipeline is None:
        raise HTTPException(status_code=503, detail="联合 KG 管道未初始化")

    try:
        initial_state = manager.build_merge_state(task_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

    # 补充 pipeline_mode 使 detect_input 节点可正常运行
    initial_state.setdefault("pipeline_mode", "kg")

    progress_q = queue.Queue()
    state._ingest_progress_q = progress_q

    def _run_merge():
        import threading as _threading

        def _bg():
            try:
                for event in pipeline.stream(initial_state):
                    for _node, update in event.items():
                        if isinstance(update, dict):
                            for msg in update.get("log_messages", []):
                                progress_q.put(("log", msg))
            except Exception as e:
                progress_q.put(("log", f"[KG-Merge] ❌ 异常: {e}"))
            finally:
                progress_q.put((None, None))
                state._ingest_progress_q = None

        all_logs: list[str] = []
        t = _threading.Thread(target=_bg, daemon=True)
        t.start()
        while True:
            try:
                kind, msg = progress_q.get(timeout=900)
            except queue.Empty:
                all_logs.append("[KG-Merge] ⚠ 等待超时")
                yield "\n".join(all_logs)
                break
            if kind is None:
                break
            all_logs.append(msg)
            yield "\n".join(all_logs)
        t.join(timeout=5)
        if not all_logs:
            yield "[KG-Merge] 合并写库完成（无日志输出）"

    return log_gen_to_sse(_run_merge())


# ─────────────────────────────────────────────
# GET /kg/task/{task_id}/status
# ─────────────────────────────────────────────

@router.get("/task/{task_id}/status", summary="查询任务各阶段完成情况")
def kg_task_status(
    task_id: str,
    state: AppState = Depends(get_state),
):
    """
    查询联合 KG 构建任务状态。

    返回格式：
    {
        "task_id":     str,
        "stages_done": ["bom", "cad", ...],
        "created_at":  "2026-04-03T10:00:00Z",
        "expires_at":  "2026-04-03T12:00:00Z",
    }
    """
    manager = state.kg_task_manager
    if manager is None:
        raise HTTPException(status_code=503, detail="KGTaskManager 未初始化")

    status = manager.get_status(task_id)
    if status is None:
        raise HTTPException(status_code=404, detail=f"task_id={task_id!r} 不存在或已超时")

    return JSONResponse(status)
