from __future__ import annotations

from functools import cached_property
from typing import Sequence

MODEL_NAME = "intfloat/multilingual-e5-small"


def prepare_e5_inputs(texts: Sequence[str], query: bool) -> list[str]:
    prefix = "query: " if query else "passage: "
    return [f"{prefix}{text}" for text in texts]


class LocalEmbedder:
    """A local multilingual embedding service. It makes no paid model API calls."""

    @cached_property
    def model(self):
        from sentence_transformers import SentenceTransformer
        return SentenceTransformer(MODEL_NAME, cache_folder="/models")

    def encode(self, texts: Sequence[str], query: bool = False) -> list[list[float]]:
        vectors = self.model.encode(prepare_e5_inputs(texts, query), normalize_embeddings=True)
        return vectors.tolist()
