"""
document_processing/rag/nlp/__init__.py — deepdoc rag.nlp shim

提供 deepdoc 依赖的两个接口：
  - find_codec(binary) → 检测字节流的字符编码
  - rag_tokenizer       → 分词器对象（jieba 实现，满足 deepdoc TableStructureRecognizer 需求）
"""

import chardet


def find_codec(binary: bytes) -> str:
    """
    检测二进制数据的字符编码。

    deepdoc 在解析文本文件时调用此函数，确定文件应该用什么编码解码。
    常见场景：老旧中文 TXT 文件可能是 GBK 编码，而不是 UTF-8。
    """
    result = chardet.detect(binary)
    encoding = result.get("encoding") or "utf-8"
    encoding = encoding.lower().replace("-", "_")
    if encoding in ("ascii", "utf_8_sig"):
        encoding = "utf-8"
    return encoding


class _RagTokenizer:
    """
    deepdoc 依赖的分词器 shim（jieba 实现）。

    RAGFlow 原版 rag_tokenizer 是基于自定义词典的复杂分词器，
    deepdoc 的 TableStructureRecognizer 仅用其 tokenize() 做简单文本分割，
    用 jieba 代替即可满足需求。
    """

    def __init__(self):
        self._jieba = None

    def _get_jieba(self):
        if self._jieba is None:
            import jieba
            jieba.initialize()
            self._jieba = jieba
        return self._jieba

    def tokenize(self, text: str) -> str:
        """
        中文分词，返回空格分隔的词语字符串。
        deepdoc TSR 用此结果做表格文字的词频统计。
        """
        if not text or not text.strip():
            return ""
        jieba = self._get_jieba()
        words = jieba.cut(text, cut_all=False)
        return " ".join(w for w in words if w.strip())

    def tag(self, word: str) -> str:
        """词性标注（简化实现，返回通用名词标签）。"""
        try:
            import jieba.posseg as pseg
            pairs = list(pseg.cut(word))
            if pairs:
                return pairs[0].flag
        except Exception:
            pass
        return "n"

    def fine_grained_tokenize(self, text: str) -> list:
        """细粒度分词，返回词语列表。"""
        if not text:
            return []
        jieba = self._get_jieba()
        return list(jieba.cut(text, cut_all=True))


rag_tokenizer = _RagTokenizer()


def surname(name: str) -> str:
    """判断姓名中的姓氏（resume 解析用）。简化实现返回首字。"""
    return name[0] if name else ""
