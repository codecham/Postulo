"""Turn profiles and offers into vectors, to compare their meaning with pgvector.

The model runs locally and for free: model2vec static embeddings are small, need no
GPU and understand French, English, Dutch... (potion-multilingual-128M).
"""

from collections.abc import Sequence
from typing import TYPE_CHECKING, Protocol

import numpy as np
import numpy.typing as npt

from app.models import EMBEDDING_DIMENSIONS, Experience, JobOffer, Profile

if TYPE_CHECKING:
    from model2vec import StaticModel

# Long offers are mostly boilerplate (benefits, legal text): the start says the most
OFFER_TEXT_MAX_CHARS = 3000
EXPERIENCES_IN_PROFILE_TEXT = 3


class Embedder(Protocol):
    """Makes one unit-length vector per text. Tests use a fake: no model download."""

    def embed(self, texts: Sequence[str]) -> list[list[float]]: ...


class Model2VecEmbedder:
    """The real embedder. The model is downloaded on first use, then cached on disk."""

    def __init__(self, model_name: str) -> None:
        self._model_name = model_name
        self._model: StaticModel | None = None

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        vectors = np.asarray(self._load().encode(list(texts)), dtype=np.float32)
        if vectors.shape[1] != EMBEDDING_DIMENSIONS:
            raise ValueError(f"{self._model_name} makes {vectors.shape[1]}-dimension vectors")
        return [[float(value) for value in row] for row in normalize(vectors)]

    def _load(self) -> StaticModel:
        if self._model is None:
            # Imported here: loading the library is slow, and only the worker needs it
            from model2vec import StaticModel

            self._model = StaticModel.from_pretrained(self._model_name)
        return self._model


def normalize(vectors: npt.NDArray[np.float32]) -> npt.NDArray[np.float32]:
    """Scale each vector to length 1 (an empty text gives a zero vector, kept as is)."""
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    return np.divide(vectors, norms, out=np.zeros_like(vectors), where=norms > 0)


def profile_text(profile: Profile, experiences: Sequence[Experience]) -> str:
    """What the user is looking for and what they bring, as one text to embed."""
    recent_jobs = [f"{item.title} ({item.company})" for item in experiences]
    parts = [
        profile.headline,
        ", ".join(profile.desired_titles),
        ", ".join(profile.skills),
        ", ".join(recent_jobs[:EXPERIENCES_IN_PROFILE_TEXT]),
        profile.summary,
    ]
    return "\n".join(part for part in parts if part)


def offer_text(offer: JobOffer) -> str:
    parts = [offer.title, ", ".join(offer.tags), offer.description[:OFFER_TEXT_MAX_CHARS]]
    return "\n".join(part for part in parts if part)
