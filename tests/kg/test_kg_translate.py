import pytest
from unittest.mock import patch, MagicMock
from backend.pipelines.kg_translate import translate_terms, translate_triples_batch

def make_mock_client(response_text: str):
    client = MagicMock()
    choice = MagicMock()
    choice.message.content = response_text
    client.chat.completions.create.return_value = MagicMock(choices=[choice])
    return client

def test_translate_uses_cache(tmp_path, monkeypatch):
    import backend.kg_storage as ks
    ks.TRANSLATIONS_FILE = str(tmp_path / "translations.json")
    ks.write_translations({"ROTOR": "转子", "isPartOf": "属于"})

    with patch("backend.pipelines.kg_translate._create_llm_client") as mock_c:
        result = translate_terms(["ROTOR", "isPartOf"])
        mock_c.assert_not_called()  # 全部命中缓存，不调用 LLM

    assert result["ROTOR"] == "转子"
    assert result["isPartOf"] == "属于"

def test_translate_calls_llm_for_new_terms(tmp_path, monkeypatch):
    import backend.kg_storage as ks
    ks.TRANSLATIONS_FILE = str(tmp_path / "translations.json")

    llm_response = '{"COMPRESSOR": "压气机", "matesWith": "配合"}'
    with patch("backend.pipelines.kg_translate._create_llm_client") as mock_c:
        mock_c.return_value = make_mock_client(llm_response)
        result = translate_terms(["COMPRESSOR", "matesWith"])

    assert result["COMPRESSOR"] == "压气机"

def test_translate_triples_batch(tmp_path, monkeypatch):
    import backend.kg_storage as ks
    ks.TRANSLATIONS_FILE = str(tmp_path / "translations.json")
    ks.write_translations({"ROTOR": "转子", "isPartOf": "属于", "BOLT": "螺栓"})

    triples = [
        {"head": "BOLT", "relation": "isPartOf", "tail": "ROTOR", "confidence": 1.0}
    ]
    result = translate_triples_batch(triples)
    assert result[0]["head_zh"] == "螺栓"
    assert result[0]["relation_zh"] == "属于"
    assert result[0]["tail_zh"] == "转子"
