"""
backend/pipelines/sse_bridge.py — LangGraph stream -> SSE 日志适配

将 pipeline.stream() 的节点事件转换为日志型生成器，
与现有 log_gen_to_sse() 完全兼容。

新增 progress_queue 参数：
  若提供 Queue，pipeline 在后台线程运行，主线程消费队列，
  实现单节点内（如 deepdoc_parse_pdf）的实时进度推送。
  若为 None，退化为原始同步模式（向后兼容）。
"""

import queue
import threading
from typing import Iterator

_SENTINEL = object()  # 哨兵：标记流结束


def pipeline_to_log_generator(
    pipeline, initial_state: dict, progress_queue=None
) -> Iterator[str]:
    """
    将 LangGraph pipeline.stream() 转换为日志型生成器。

    progress_queue（可选）：由 ingest_pipeline 路由创建并挂到 app_state，
    deepdoc 节点内的 _progress 回调通过 app_state._ingest_progress_q 写入。
    主线程消费此队列，每收到一条消息立即 yield 完整日志快照。
    """
    if progress_queue is None:
        yield from _sync_pipeline_gen(pipeline, initial_state)
        return

    # ── 带进度队列的异步模式 ──────────────────────────────────────
    all_logs: list[str] = []
    error_holder: list[Exception] = []

    def _run_pipeline():
        """后台线程：运行 pipeline，节点完成时把 log_messages 放入队列。"""
        try:
            for event in pipeline.stream(initial_state):
                for _node_name, update in event.items():
                    if not isinstance(update, dict):
                        continue
                    for msg in update.get("log_messages", []):
                        progress_queue.put(("log", msg))
        except Exception as e:
            error_holder.append(e)
        finally:
            progress_queue.put((_SENTINEL, None))  # 通知主线程流结束

    thread = threading.Thread(target=_run_pipeline, daemon=True)
    thread.start()

    while True:
        try:
            kind, msg = progress_queue.get(timeout=900)  # 15min 超时（心跳每60s发一次，留足裕量）
        except queue.Empty:
            all_logs.append("[sse_bridge] ⚠ 等待超时（15min），管道可能已卡死，请检查后端日志")
            yield "\n".join(all_logs)
            break

        if kind is _SENTINEL:
            break

        all_logs.append(msg)
        yield "\n".join(all_logs)

    thread.join(timeout=5)

    if error_holder:
        all_logs.append(f"[pipeline] ❌ 异常: {error_holder[0]}")
        yield "\n".join(all_logs)

    if not all_logs:
        yield "管道执行完成（无日志输出）"


def _sync_pipeline_gen(pipeline, initial_state: dict) -> Iterator[str]:
    """原始同步版本，向后兼容（不传 progress_queue 时使用）。"""
    all_logs: list[str] = []

    for event in pipeline.stream(initial_state):
        for _node_name, update in event.items():
            if not isinstance(update, dict):
                continue
            new_logs = update.get("log_messages", [])
            if new_logs:
                all_logs.extend(new_logs)
                yield "\n".join(all_logs)

    if not all_logs:
        yield "管道执行完成（无日志输出）"
