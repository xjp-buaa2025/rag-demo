"""
document_processing/rag/nlp/__init__.py — deepdoc 依赖的编码检测 shim 模块

背景：
  deepdoc 的 txt_parser 通过以下方式导入编码检测函数：
    from rag.nlp import find_codec

  RAGFlow 的 rag.nlp 模块有大量其他功能（NLP 处理、分词等），我们只需要
  find_codec 这一个函数，所以单独实现这个 shim，避免引入 RAGFlow 全量依赖。

实现：
  使用 chardet 库检测二进制内容的字符编码（支持 GBK、UTF-8、Big5 等）。

详见 PROJECT_GUIDE.md § 6.6
"""

import chardet


def find_codec(binary: bytes) -> str:
    """
    检测二进制数据的字符编码。

    deepdoc 在解析文本文件时调用此函数，确定文件应该用什么编码解码。
    常见场景：老旧中文 TXT 文件可能是 GBK 编码，而不是 UTF-8。

    标准化处理：
      - ascii → utf-8（ASCII 是 UTF-8 的子集，统一用 utf-8 解码更安全）
      - utf_8_sig → utf-8（带 BOM 的 UTF-8，去掉 BOM 标记）
    """
    result = chardet.detect(binary)
    encoding = result.get("encoding") or "utf-8"
    # 统一编码名称格式（chardet 返回的名称可能含 - 或大写）
    encoding = encoding.lower().replace("-", "_")
    if encoding in ("ascii", "utf_8_sig"):
        encoding = "utf-8"
    return encoding
