from __future__ import annotations

from app.services.types import SearchHit


class ContextBuilder:
    def __init__(self, max_tokens: int) -> None:
        self.max_tokens = max_tokens

    def build(self, hits: list[SearchHit]) -> tuple[str, list[SearchHit]]:
        selected: list[SearchHit] = []
        fragments: list[str] = []
        seen: set[str] = set()
        used_tokens = 0
        for hit in hits:
            key = hit.chunk.parent_id or hit.chunk.chunk_id
            normalized = " ".join(hit.chunk.text.lower().split())
            if key in seen or normalized in seen:
                continue
            tokens = hit.chunk.text.split()
            remaining = self.max_tokens - used_tokens
            if remaining <= 0:
                break
            excerpt = " ".join(tokens[:remaining])
            if not excerpt:
                continue
            selected.append(hit)
            fragments.append(f"[Source: {hit.chunk.document_id}]\n{excerpt}")
            used_tokens += len(excerpt.split())
            seen.add(key)
            seen.add(normalized)
        return "\n\n".join(fragments), selected
