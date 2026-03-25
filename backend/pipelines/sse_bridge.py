"""
backend/pipelines/sse_bridge.py — LangGraph stream -> SSE 日志适配

将 pipeline.stream() 的节点事件转换为日志型生成器，
与现有 log_gen_to_sse() 完全兼容。
"""

from typing import Iterator


def pipeline_to_log_generator(pipeline, initial_state: dict) -> Iterator[str]:
    """
    将 LangGraph pipeline.stream() 转换为日志型生成器。

    LangGraph stream 每次 yield: {node_name: state_update_dict}
    提取 log_messages 并累积为完整快照，与现有 SSE 协议一致。
    """
    all_logs: list[str] = []

    for event in pipeline.stream(initial_state):
        for _node_name, update in event.items():
            if not isinstance(update, dict):
                continue
            new_logs = update.get("log_messages", [])
            if new_logs:
                all_logs.extend(new_logs)
                yield "\n".join(all_logs)

    # 检查最终状态中的错误
    # （最后一次 yield 已经包含了所有日志）
    if not all_logs:
        yield "管道执行完成（无日志输出）"
