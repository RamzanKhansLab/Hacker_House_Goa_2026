from ingestion.normalize import normalize_record


def test_normalize_msmarco_xi_schema_preserves_translated_passages_and_language() -> None:
    records = normalize_record(
        {
            "query_id": 7,
            "query": "कृत्रिम बुद्धिमत्ता क्या है?",
            "Answer": "कृत्रिम बुद्धिमत्ता मशीनों की बुद्धिमान कार्य करने की क्षमता है।",
            "source_lang": "eng_Latn",
            "target_lang": "hin_Deva",
            "passages": {
                "English_passages": ["Artificial intelligence is a field of computer science."],
                "Translated_passages": ["कृत्रिम बुद्धिमत्ता कंप्यूटर विज्ञान का क्षेत्र है।"],
            },
        }
    )
    assert len(records) == 1
    assert records[0]["language"] == "hi"
    assert records[0]["source_language"] == "eng_Latn"
    assert records[0]["target_language"] == "hin_Deva"
    assert records[0]["text"] == "कृत्रिम बुद्धिमत्ता कंप्यूटर विज्ञान का क्षेत्र है।"


def test_normalize_msmarco_xi_uses_selected_passages_when_labels_exist() -> None:
    records = normalize_record(
        {
            "query_id": 8,
            "query": "test",
            "target_lang": "hin_Deva",
            "passages": {"is_selected": [0, 1], "Translated_passages": ["wrong passage", "selected passage"]},
        }
    )
    assert [record["text"] for record in records] == ["selected passage"]
