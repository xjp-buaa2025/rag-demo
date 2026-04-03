"""
backend/sse.py — 生成器 → SSE StreamingResponse 适配层

现有生成器有两种 yield 语义：

1. 日志类（run_ingest、run_eval_*）：
   每次 yield 完整的累积文本快照。
   SSE 端直接传 {"log": snapshot}，客户端用此值替换显示内容。

2. Chat 类（chat、assembly_chat）：
   每次 yield 完整的累积回答文本（逐 token 累积）。
   最后一条追加 _SOURCES_JSON_SEP + JSON 格式的结构化来源列表。
   SSE 端：
     中间帧：{"delta": new_part}
     最后帧：{"done": true, "sources": [...Citation...], "image_urls": [...]}
"""

import json
from typing import Iterator
from fastapi.responses import StreamingResponse

# Chat 生成器中用于分隔回答正文与结构化来源 JSON 的标志字符串
_SOURCES_JSON_SEP = "\n\n[__SOURCES_JSON__]"
# 兼容旧版：图片 URL 分隔符（已废弃，图片信息现在内嵌在 sources JSON 中）
_IMAGES_SEP = "\n\n[__IMAGES__]"
# 阶段状态标记前缀（生成器 yield 此前缀的字符串，SSE 层转为 stage 帧）
_STAGE_PREFIX = "__STAGE__:"


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
                if isinstance(snapshot, tuple):
                    snapshot = snapshot[0]
                yield _sse_data({"log": str(snapshot)})
        except GeneratorExit:
            gen.close()
            return
        except Exception as e:
            yield _sse_data({"error": str(e)})
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


def chat_gen_to_sse(gen: Iterator) -> StreamingResponse:
    """
    将 chat / assembly_chat 生成器转为 SSE StreamingResponse。
    - 中间帧：data: {"delta": "<本次新增文本>"}\n\n
    - 最后帧：data: {"done": true, "sources": [...Citation...], "image_urls": [...]}\n\n

    生成器约定：
      最后一次 yield 的字符串在末尾追加：
        \n\n[__SOURCES_JSON__][{...}, ...]
      sse.py 识别并解析该标记，提取结构化 Citation 列表放入 done 帧。
      image_urls 从 sources 中自动提取（chunk_type=="image" 且有 image_url）。
    """
    def event_stream():
        prev_len = 0
        last_snapshot = ""
        try:
            for snapshot in gen:
                if not isinstance(snapshot, str):
                    snapshot = str(snapshot)

                # 阶段标记检测：emit stage 帧，不更新 prev_len
                if snapshot.startswith(_STAGE_PREFIX):
                    yield _sse_data({"stage": snapshot[len(_STAGE_PREFIX):]})
                    continue

                # 计算 delta（去掉 _SOURCES_JSON_SEP 及其后内容，只发送回答正文增量）
                visible = snapshot.split(_SOURCES_JSON_SEP, 1)[0]
                delta = visible[prev_len:]
                prev_len = len(visible)
                last_snapshot = snapshot

                if delta:
                    yield _sse_data({"delta": delta})

        except GeneratorExit:
            gen.close()
            return
        except Exception as e:
            yield _sse_data({"error": str(e)})
            return

        # 解析结构化来源 JSON
        sources = []
        if _SOURCES_JSON_SEP in last_snapshot:
            _, sources_raw = last_snapshot.split(_SOURCES_JSON_SEP, 1)
            try:
                sources = json.loads(sources_raw)
            except Exception:
                sources = []

        # 从 sources 中提取图片 URL（chunk_type=="image" 且有 image_url）
        image_urls = [
            s["image_url"] for s in sources
            if s.get("chunk_type") == "image" and s.get("image_url")
        ]

        yield _sse_data({"done": True, "sources": sources, "image_urls": image_urls})

    return StreamingResponse(event_stream(), media_type="text/event-stream")
