import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from backend.pipelines.nodes_kg import _build_prompt_with_bom


def test_bom_table_includes_name_column():
    """速查表应同时包含零件号和名称两列。"""
    bom_entities = [
        {"part_number": "3034521", "name": "CENTER FIRESEAL MOUNT RING"},
        {"part_number": "3034344", "name": "COMPRESSOR ROTOR INSTALLATION"},
    ]
    result = _build_prompt_with_bom("BASE_PROMPT", bom_entities)
    assert "CENTER FIRESEAL MOUNT RING" in result
    assert "3034521" in result
    assert "COMPRESSOR ROTOR INSTALLATION" in result
    assert "3034344" in result


def test_bom_table_includes_bom_id_annotation_instruction():
    """速查表说明中应包含 [BOM:{零件号}] 注释指令。"""
    bom_entities = [{"part_number": "3034521", "name": "MOUNT RING"}]
    result = _build_prompt_with_bom("BASE_PROMPT", bom_entities)
    assert "[BOM:" in result


def test_empty_bom_entities_returns_base_prompt():
    """空列表时返回原始 prompt 不变。"""
    result = _build_prompt_with_bom("MY_PROMPT", [])
    assert result == "MY_PROMPT"


def test_entities_without_part_number_still_show_name():
    """只有名称没有零件号的实体也应出现在速查表中。"""
    bom_entities = [{"part_number": "", "name": "THRUST BEARING"}]
    result = _build_prompt_with_bom("BASE_PROMPT", bom_entities)
    assert "THRUST BEARING" in result


from unittest.mock import patch, MagicMock


def test_stage2_prompt_includes_bom_when_bom_exists():
    """Stage 2 提取时 prompt 应包含 BOM 速查表内容。"""
    captured_prompts = []

    # 模拟 LLM 客户端
    mock_resp = MagicMock()
    mock_resp.choices[0].message.content = '{"entities":[],"relations":[]}'
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_resp

    # 模拟 BOM 数据已存在
    mock_bom = {
        "entities": [
            {"part_number": "3034521", "name": "CENTER FIRESEAL MOUNT RING"},
        ]
    }

    def fake_create(messages, temperature):
        captured_prompts.append(messages[0]["content"])
        return mock_resp

    mock_client.chat.completions.create.side_effect = fake_create

    from backend.routers.kg_stages import _stage2_manual_gen
    from backend.state import AppState

    state = MagicMock(spec=AppState)
    state.llm_client = mock_client

    with patch("backend.routers.kg_stages.stage_exists", return_value=True), \
         patch("backend.routers.kg_stages.read_stage", return_value=mock_bom), \
         patch("backend.routers.kg_stages._extract_pdf_chunks",
               return_value=([{"text": "Remove nuts and bolts. Apply torque.",
                               "chunk_id": "c1", "ata_section": "72-30-01"}], "pdfplumber")), \
         patch("backend.routers.kg_stages.write_stage"), \
         patch("backend.routers.kg_stages._write_manual_to_neo4j", return_value=(False, "test")):
        try:
            for evt in _stage2_manual_gen("fake.pdf", "test.pdf", state, {}):
                pass  # 消费生成器
        except Exception as e:
            pass  # 我们只关心 captured_prompts

    assert len(captured_prompts) > 0
    assert "CENTER FIRESEAL MOUNT RING" in captured_prompts[0], \
        "BOM 名称未注入 prompt，说明 _build_prompt_with_bom 未被调用"


from backend.routers.kg_stages import _post_process_triples


def test_garbled_head_entity_is_filtered():
    """head 含乱码字符（Unicode 替换字符）的三元组应被过滤。"""
    triples = [
        {"head": "\ufffd\ufffd\ufffd\ufffd", "tail": "Gas generator case",
         "relation": "matesWith", "confidence": 0.8,
         "head_type": "Assembly", "tail_type": "Assembly"},
    ]
    result = _post_process_triples(triples)
    assert result == [], f"Expected empty list, got {result}"


def test_garbled_tail_entity_is_filtered():
    """tail 含乱码字符的三元组也应被过滤。"""
    triples = [
        {"head": "Compressor Rotor", "tail": "\ufffd\ufffdȥ\ufffd\ufffd",
         "relation": "matesWith", "confidence": 0.9,
         "head_type": "Assembly", "tail_type": "Assembly"},
    ]
    result = _post_process_triples(triples)
    assert result == []


def test_normal_english_entity_passes_through():
    """正常英文实体不应被误过滤。"""
    triples = [
        {"head": "Center Fireseal Mount Ring", "tail": "Gas Generator Case",
         "relation": "matesWith", "confidence": 0.85,
         "head_type": "Assembly", "tail_type": "Assembly"},
    ]
    result = _post_process_triples(triples)
    assert len(result) == 1
