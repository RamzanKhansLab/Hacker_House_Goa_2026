import pytest
from pydantic import ValidationError

from app.schemas import QueryRequest


def test_query_request_normalizes_whitespace() -> None:
    assert QueryRequest(query="  What   is RAG?  ").query == "What is RAG?"


def test_query_request_rejects_blank_value() -> None:
    with pytest.raises(ValidationError):
        QueryRequest(query="   ")
