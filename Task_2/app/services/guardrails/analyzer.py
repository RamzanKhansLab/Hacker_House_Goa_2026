from __future__ import annotations

import re

from app.services.types import QueryAnalysis

_UNSAFE = re.compile(r"\b(?:build\s+(?:a\s+)?bomb|make\s+(?:a\s+)?bomb|kill\s+yourself|malware|ransomware)\b", re.I)
_INJECTION = re.compile(r"(?:ignore (?:all |previous |above )?instructions|system prompt|reveal (?:your )?prompt|jailbreak)", re.I)
_DEVANAGARI = re.compile(r"[\u0900-\u097F]")
_BENGALI = re.compile(r"[\u0980-\u09FF]")
_TAMIL = re.compile(r"[\u0B80-\u0BFF]")
_TELUGU = re.compile(r"[\u0C00-\u0C7F]")
_KANNADA = re.compile(r"[\u0C80-\u0CFF]")
_MALAYALAM = re.compile(r"[\u0D00-\u0D7F]")
_GUJARATI = re.compile(r"[\u0A80-\u0AFF]")
_GURMUKHI = re.compile(r"[\u0A00-\u0A7F]")
_ODIA = re.compile(r"[\u0B00-\u0B7F]")
_URDU = re.compile(r"[\u0600-\u06FF]")


class QueryAnalyzer:
    def analyze(self, query: str, declared_language: str | None = None) -> QueryAnalysis:
        normalized = " ".join(query.strip().split())
        language = declared_language or self.detect_language(normalized)
        if _UNSAFE.search(normalized):
            return QueryAnalysis(normalized, language, "UNSAFE", "safety pattern matched")
        if _INJECTION.search(normalized):
            return QueryAnalysis(normalized, language, "INJECTION_BLOCKED", "prompt-injection pattern matched")
        if len(normalized) < 2:
            return QueryAnalysis(normalized, language, "AMBIGUOUS", "query is too short")
        return QueryAnalysis(normalized, language, "IN_DOMAIN", chunk_strategy=self.select_strategy(normalized, language))

    @staticmethod
    def detect_language(text: str) -> str:
        if _TAMIL.search(text):
            return "ta"
        if _TELUGU.search(text):
            return "te"
        if _KANNADA.search(text):
            return "kn"
        if _MALAYALAM.search(text):
            return "ml"
        if _BENGALI.search(text):
            return "bn"
        if _GUJARATI.search(text):
            return "gu"
        if _GURMUKHI.search(text):
            return "pa"
        if _ODIA.search(text):
            return "or"
        if _URDU.search(text):
            return "ur"
        if _DEVANAGARI.search(text):
            # This conservative heuristic lets metadata filters still work;
            # callers may provide hi/mr/ne/sa explicitly when known.
            return "hi"
        return "en"

    @staticmethod
    def select_strategy(query: str, language: str) -> str:
        lower = query.lower()
        if any(term in lower for term in ("language", "हिंदी", "मराठी", "metadata")):
            return "metadata"
        if len(query.split()) > 22 or any(term in lower for term in ("compare", "explain", "difference")):
            return "parent_child"
        if any(term in lower for term in ("exact", "term", "define", "what is", "क्या है")):
            return "sliding"
        return "semantic" if language != "en" else "sentence"
