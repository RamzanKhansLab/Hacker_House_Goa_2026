from __future__ import annotations

from app.services.grounding import GroundingValidator


def evaluate_examples(examples: list[tuple[str, str, bool]]) -> float:
    """Return deterministic grounding accuracy for labelled local test examples."""
    validator = GroundingValidator()
    correct = sum(validator.validate(answer, context).grounded == expected for answer, context, expected in examples)
    return correct / len(examples) if examples else 0.0
