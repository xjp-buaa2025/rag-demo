"""
backend/sse.py — 生成器 → SSE StreamingResponse 适配层

现有生成器有两种 yield 语义：

1. 日志类（run_ingest、run_eval_*）：
   每次 yield 完整的累积文本快照。
   SSE 端直接传 {"log": snapshot}，客户端用此值替换显示内容。

2. Chat 类（chat、assembly_chat）：
   每次 yield 完整的累积回答文本（逐 token 累积）。
   最后一条包含 [__IMAGES__] 标记（可选），用于携带检索到的图片 URL。
   SSE 端：
     中间帧：{"delta": new_part}
     最后帧：{"done": true, "sources_md": "...", "image_urls": [...]}
"""

import json
from typing import Iterator
from fastapi.responses import StreamingResponse

# Chat 生成器中用于分隔回答正文与参考来源的标志字符串
_SOURCES_SEP = "\n\n---\n"
# 用于分隔参考来源与图片 URL 列表的标志字符串
_IMAGES_SEP = "\n\n[__IMAGES__]"


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
    - 最后帧：data: {"done": true, "sources_md": "<参考来源 Markdown>",
                      "image_urls": ["<url1>", ...]}\n\n

    生成器约定：
      最后一次 yield 的字符串可选地在末尾追加：
        \n\n[__IMAGES__]["<url1>","<url2>"]
      sse.py 识别并解析该标记，提取 image_urls 放入 done 帧。
      sources_md 以 _SOURCES_SEP 为分隔符从回答体中提取。
    """
    def event_stream():
        prev_len = 0
        last_snapshot = ""
        try:
            for snapshot in gen:
                if not isinstance(snapshot, str):
                    snapshot = str(snapshot)

                # 计算 delta（去掉 [__IMAGES__] 尾缀后的部分）
                visible = snapshot.split(_IMAGES_SEP, 1)[0] if _IMAGES_SEP in snapshot else snapshot
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

        # 解析 image_urls
        image_urls = []
        if _IMAGES_SEP in last_snapshot:
            body_part, img_json = last_snapshot.split(_IMAGES_SEP, 1)
            try:
                image_urls = json.loads(img_json)
            except Exception:
                image_urls = []
            last_snapshot = body_part

        # 提取 sources_md
        sources_md = ""
        if _SOURCES_SEP in last_snapshot:
            _, sources_md = last_snapshot.split(_SOURCES_SEP, 1)
            sources_md = _SOURCES_SEP + sources_md

        yield _sse_data({"done": True, "sources_md": sources_md, "image_urls": image_urls})

    return StreamingResponse(event_stream(), media_type="text/event-stream")
