"""
backend/sse.py — 生成器 → SSE StreamingResponse 适配层

现有 app.py 的生成器有两种 yield 语义：

1. 日志类（run_ingest、run_eval_*）：
   每次 yield 完整的累积文本快照（Gradio 约定）。
   SSE 端直接传 {"log": snapshot}，客户端用此值替换显示内容。

2. Chat 类（chat、assembly_chat）：
   每次 yield 完整的累积回答文本（逐 token 累积）。
   SSE 端需要提取 delta（新增部分）发送 {"delta": new_part}，
   最后一条发送 {"done": true, "sources_md": "..."}。

两个工厂函数返回 FastAPI StreamingResponse（media_type="text/event-stream"）。
路由函数定义为普通 def（非 async def），FastAPI 自动在线程池中执行，
StreamingResponse 接受同步可迭代对象，与此完全兼容。
"""

import json
from typing import Generator, Iterator
from fastapi.responses import StreamingResponse

# SSE 中用于分隔回答正文与参考来源的标志字符串（与 app.py format_sources 一致）
_SOURCES_SEP = "\n\n---\n"


def _sse_data(payload: dict) -> str:
    """格式化单条 SSE 事件（RFC 8895）。"""
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


def log_gen_to_sse(gen: Iterator) -> StreamingResponse:
    """
    将日志型生成器转为 SSE StreamingResponse。
    每条事件格式：data: {"log": "<完整日志快照>"}\n\n
    结束时发送：data: [DONE]\n\n
    """
    def event_stream():
        try:
            for snapshot in gen:
                # run_ingest yield 的是 (log_text, status_text) 元组
                # run_eval_* yield 的是纯字符串
                if isinstance(snapshot, tuple):
                    snapshot = snapshot[0]
                yield _sse_data({"log": str(snapshot)})
        except Exception as e:
            yield _sse_data({"error": str(e)})
        finally:
            yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


def chat_gen_to_sse(gen: Iterator) -> StreamingResponse:
    """
    将 chat / assembly_chat 生成器转为 SSE StreamingResponse。
    - 中间帧：data: {"delta": "<本次新增文本>"}\n\n
    - 最后帧：data: {"done": true, "sources_md": "<参考来源 Markdown 或空字符串>"}\n\n

    原生成器每次 yield 完整累积文本，通过记录 prev_len 提取 delta。
    参考来源部分以 _SOURCES_SEP 为分隔符，从最后一次 snapshot 中提取。
    """
    def event_stream():
        prev_len = 0
        last_snapshot = ""
        try:
            for snapshot in gen:
                if not isinstance(snapshot, str):
                    snapshot = str(snapshot)
                delta = snapshot[prev_len:]
                prev_len = len(snapshot)
                last_snapshot = snapshot
                if delta:
                    yield _sse_data({"delta": delta})
        except Exception as e:
            yield _sse_data({"error": str(e)})
            return

        # 从最后一次 snapshot 提取参考来源 Markdown
        sources_md = ""
        if _SOURCES_SEP in last_snapshot:
            _, sources_md = last_snapshot.split(_SOURCES_SEP, 1)
            sources_md = _SOURCES_SEP + sources_md

        yield _sse_data({"done": True, "sources_md": sources_md})

    return StreamingResponse(event_stream(), media_type="text/event-stream")
