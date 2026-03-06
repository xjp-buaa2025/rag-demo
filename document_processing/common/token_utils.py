"""
document_processing/common/token_utils.py — deepdoc 依赖的 token 计数 shim 模块

背景：
  deepdoc 的原始代码（来自 RAGFlow）通过以下方式导入 token 计数函数：
    from common.token_utils import num_tokens_from_string

  RAGFlow 有自己的 common 包实现。我们把 document_processing/ 加入 sys.path，
  并在这里提供同名函数，让 deepdoc 的 import 语句能正常工作。

实现：
  使用 OpenAI 官方的 tiktoken 库，编码方案 cl100k_base（GPT-3.5/4 使用的 tokenizer）。

精度说明：
  对中文有一定误差（中文 token 化方式与 OpenAI 不同），但 deepdoc 用这个函数
  只做粗粒度的长度判断，不需要精确计数，误差在可接受范围内。

详见 PROJECT_GUIDE.md § 6.5
"""

import tiktoken

# cl100k_base 是 GPT-3.5 / GPT-4 使用的 tokenizer，中英文通用
_encoder = tiktoken.get_encoding("cl100k_base")


def num_tokens_from_string(text: str) -> int:
    """
    计算字符串的 token 数量。

    deepdoc 的解析器用这个函数判断文本块是否超过长度阈值，
    超过则触发进一步切分逻辑。
    """
    if not isinstance(text, str):
        text = str(text)
    return len(_encoder.encode(text))


# 同时暴露 encoder 对象，兼容直接 import encoder 的代码
encoder = _encoder
