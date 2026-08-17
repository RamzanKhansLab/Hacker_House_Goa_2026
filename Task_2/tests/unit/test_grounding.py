from app.services.grounding import GroundingValidator


def test_grounding_accepts_supported_claim() -> None:
    result = GroundingValidator().validate(
        "Hybrid retrieval combines dense vector search with BM25.",
        "Hybrid retrieval combines dense vector search with lexical BM25 search.",
    )
    assert result.grounded


def test_grounding_rejects_unsupported_claim() -> None:
    result = GroundingValidator().validate(
        "The system is deployed on Mars with a trillion documents.",
        "Hybrid retrieval combines dense vector search with lexical BM25 search.",
    )
    assert not result.grounded
