"""
Shim for RAGFlow's rag.nlp module.
Provides encoding detection and tokenizer stubs needed by deepdoc parsers.
"""
import chardet


def find_codec(binary: bytes) -> str:
    """Detect the character encoding of a binary blob."""
    result = chardet.detect(binary)
    encoding = result.get("encoding") or "utf-8"
    # Normalize common aliases
    encoding = encoding.lower().replace("-", "_")
    if encoding in ("ascii", "utf_8_sig"):
        encoding = "utf-8"
    return encoding
