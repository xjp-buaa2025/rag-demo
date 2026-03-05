"""
Shim for RAGFlow's common.token_utils.
Provides token counting using tiktoken.
"""
import tiktoken

_encoder = tiktoken.get_encoding("cl100k_base")


def num_tokens_from_string(text: str) -> int:
    """Count the number of tokens in a text string."""
    if not isinstance(text, str):
        text = str(text)
    return len(_encoder.encode(text))


# Also expose the encoder object for code that imports it directly
encoder = _encoder
