"""
document_processing/rag/prompts/generator.py — shim

deepdoc pdf_parser 使用 vision_llm_describe_prompt 调用视觉 LLM 描述图片，
我们不使用这条路径（改用 MiniMax Vision API），所以空实现即可。
"""


def vision_llm_describe_prompt(page=1, **kwargs) -> str:
    """返回空字符串，不使用 RAGFlow 内置 Vision LLM 路径。"""
    return ""


def vision_llm_figure_describe_prompt(*args, **kwargs) -> str:
    return ""


def vision_llm_figure_describe_prompt_with_context(*args, **kwargs) -> str:
    return ""
