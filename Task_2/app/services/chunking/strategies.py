from __future__ import annotations

import hashlib
import re
from abc import ABC, abstractmethod
from collections.abc import Iterable, Mapping
from typing import Any, cast

from app.services.types import Chunk

_SENTENCE_RE = re.compile(r"(?<=[.!?।])\s+", re.UNICODE)


def _tokens(text: str) -> list[str]:
    return text.split()


def _chunk_id(document_id: str, strategy: str, start: int, text: str) -> str:
    digest = hashlib.sha256(f"{document_id}|{strategy}|{start}|{text}".encode("utf-8")).hexdigest()[:16]
    return f"{document_id}:{strategy}:{digest}"


def _make_chunk(record: dict[str, object], strategy: str, text: str, start: int, parent_id: str | None = None) -> Chunk:
    return Chunk(
        chunk_id=_chunk_id(str(record["id"]), strategy, start, text),
        document_id=str(record["id"]),
        parent_id=parent_id,
        text=text,
        language=str(record.get("language", "unknown")),
        source_language=str(record.get("source_language") or "") or None,
        target_language=str(record.get("target_language") or "") or None,
        title=str(record.get("title") or "") or None,
        strategy=strategy,
        start_offset=start,
        end_offset=start + len(text),
        token_count=len(_tokens(text)),
        metadata=dict(cast(Mapping[str, Any], record.get("metadata", {}) or {})),
    )


class ChunkingStrategy(ABC):
    name: str

    @abstractmethod
    def chunk(self, record: dict[str, object]) -> list[Chunk]: ...


class FixedChunker(ChunkingStrategy):
    name = "fixed"

    def __init__(self, size: int = 120) -> None:
        self.size = size

    def chunk(self, record: dict[str, object]) -> list[Chunk]:
        text = str(record["text"])
        tokens = _tokens(text)
        chunks: list[Chunk] = []
        offset = 0
        for position in range(0, len(tokens), self.size):
            body = " ".join(tokens[position : position + self.size])
            start = text.find(body, offset)
            chunks.append(_make_chunk(record, self.name, body, max(start, offset)))
            offset = max(start, offset) + len(body)
        return chunks


class SentenceChunker(ChunkingStrategy):
    name = "sentence"

    def __init__(self, sentences_per_chunk: int = 3) -> None:
        self.sentences_per_chunk = sentences_per_chunk

    def chunk(self, record: dict[str, object]) -> list[Chunk]:
        text = str(record["text"])
        sentences = [sentence.strip() for sentence in _SENTENCE_RE.split(text) if sentence.strip()]
        chunks: list[Chunk] = []
        offset = 0
        for position in range(0, len(sentences), self.sentences_per_chunk):
            body = " ".join(sentences[position : position + self.sentences_per_chunk])
            start = text.find(body, offset)
            chunks.append(_make_chunk(record, self.name, body, max(start, offset)))
            offset = max(start, offset) + len(body)
        return chunks


class SlidingWindowChunker(ChunkingStrategy):
    name = "sliding"

    def __init__(self, size: int = 120, overlap: int = 30) -> None:
        self.size = size
        self.overlap = overlap

    def chunk(self, record: dict[str, object]) -> list[Chunk]:
        text = str(record["text"])
        tokens = _tokens(text)
        step = max(1, self.size - self.overlap)
        output: list[Chunk] = []
        offset = 0
        for position in range(0, len(tokens), step):
            body = " ".join(tokens[position : position + self.size])
            if not body:
                break
            start = text.find(body, offset)
            output.append(_make_chunk(record, self.name, body, max(start, offset)))
            offset = max(start, offset)
            if position + self.size >= len(tokens):
                break
        return output


class SemanticChunker(SentenceChunker):
    name = "semantic"

    def __init__(self, max_tokens: int = 150) -> None:
        self.max_tokens = max_tokens

    def chunk(self, record: dict[str, object]) -> list[Chunk]:
        text = str(record["text"])
        sentences = [sentence.strip() for sentence in _SENTENCE_RE.split(text) if sentence.strip()]
        groups: list[str] = []
        current: list[str] = []
        current_tokens = 0
        for sentence in sentences:
            sentence_tokens = len(_tokens(sentence))
            if current and current_tokens + sentence_tokens > self.max_tokens:
                groups.append(" ".join(current))
                current, current_tokens = [], 0
            current.append(sentence)
            current_tokens += sentence_tokens
        if current:
            groups.append(" ".join(current))
        offset = 0
        output: list[Chunk] = []
        for body in groups:
            start = text.find(body, offset)
            output.append(_make_chunk(record, self.name, body, max(start, offset)))
            offset = max(start, offset) + len(body)
        return output


class MetadataAwareChunker(SemanticChunker):
    name = "metadata"

    def chunk(self, record: dict[str, object]) -> list[Chunk]:
        output = super().chunk(record)
        language = str(record.get("language", "unknown"))
        return [
            Chunk(**{**chunk.as_dict(), "strategy": self.name, "metadata": {**chunk.metadata, "language_bucket": language}})
            for chunk in output
        ]


class ParentChildChunker(ChunkingStrategy):
    name = "parent_child"

    def __init__(self, parent_size: int = 240, child_size: int = 80) -> None:
        self.parent_size = parent_size
        self.child_size = child_size

    def chunk(self, record: dict[str, object]) -> list[Chunk]:
        text = str(record["text"])
        words = _tokens(text)
        output: list[Chunk] = []
        offset = 0
        for parent_start in range(0, len(words), self.parent_size):
            parent_text = " ".join(words[parent_start : parent_start + self.parent_size])
            if not parent_text:
                continue
            start = text.find(parent_text, offset)
            start = max(start, offset)
            parent = _make_chunk(record, self.name, parent_text, start)
            output.append(parent)
            for child_start in range(0, len(_tokens(parent_text)), self.child_size):
                child_text = " ".join(_tokens(parent_text)[child_start : child_start + self.child_size])
                if child_text:
                    child_offset = parent_text.find(child_text)
                    output.append(_make_chunk(record, self.name, child_text, start + child_offset, parent.chunk_id))
            offset = start + len(parent_text)
        return output


def build_chunker(name: str) -> ChunkingStrategy:
    choices: dict[str, ChunkingStrategy] = {
        "fixed": FixedChunker(),
        "sentence": SentenceChunker(),
        "sliding": SlidingWindowChunker(),
        "semantic": SemanticChunker(),
        "metadata": MetadataAwareChunker(),
        "parent_child": ParentChildChunker(),
    }
    if name not in choices:
        raise ValueError(f"Unknown chunking strategy: {name}")
    return choices[name]


def chunk_records(records: Iterable[dict[str, object]], strategy: str) -> list[Chunk]:
    chunker = build_chunker(strategy)
    return [chunk for record in records for chunk in chunker.chunk(record)]
