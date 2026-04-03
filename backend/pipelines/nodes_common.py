"""
backend/pipelines/nodes_common.py — 共用节点

detect_input: 检测文件类型，设置 file_ext。
error_handler: 记录错误并终止。
"""

import os


def detect_input(state: dict) -> dict:
    """检测文件扩展名，设置 file_ext 字段。"""
    file_path = state["file_path"]
    ext = os.path.splitext(file_path)[1].lower().lstrip(".")
    result = {
        "file_ext": ext,
        "current_node": "detect_input",
        "log_messages": [
            f"[detect_input] 文件类型: .{ext} | 管道: {state.get('pipeline_mode', '?')}"
            f" | stage: {state.get('kg_task_stage', '-')}"
        ],
    }
    # 明确透传 KG 路由字段，防止 LangGraph 版本差异导致字段丢失
    if "kg_task_stage" in state:
        result["kg_task_stage"] = state["kg_task_stage"]
    if "kg_task_id" in state:
        result["kg_task_id"] = state["kg_task_id"]
    return result


def error_handler(state: dict) -> dict:
    """错误终止节点。"""
    err = state.get("error", "未知错误")
    return {
        "current_node": "error_handler",
        "log_messages": [f"[error] {err}"],
    }
