"""Save collected offers once, and give each one its embedding."""

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from urllib.parse import urlsplit

from sqlalchemy import select, tuple_
from sqlalchemy.orm import Session

from app.models import JobOffer
from app.services.job_search.embeddings import Embedder, offer_text
from app.services.job_search.offer import CollectedOffer
from app.services.job_search.text import detect_language, truncate

EMBEDDING_BATCH_SIZE = 256


@dataclass(frozen=True)
class SavedOffers:
    found: int  # distinct offers the job boards returned
    new: int  # among them, offers seen for the first time


def save_offers(db: Session, collected: Iterable[CollectedOffer]) -> SavedOffers:
    """Insert the offers not stored yet. Known offers are left as they are."""
    unique = {offer.key: offer for offer in collected if is_web_url(offer.url)}
    known = _known_keys(db, list(unique))
    new_offers = [build_offer(offer) for key, offer in unique.items() if key not in known]
    db.add_all(new_offers)
    db.commit()
    return SavedOffers(found=len(unique), new=len(new_offers))


def is_web_url(url: str) -> bool:
    """True for an http(s) link: a job board must never put a `javascript:` URL in a page."""
    parts = urlsplit(url.strip())
    return parts.scheme in {"http", "https"} and bool(parts.netloc)


def build_offer(offer: CollectedOffer) -> JobOffer:
    """The database row of a collected offer, cut to the column sizes."""
    return JobOffer(
        source=offer.source,
        external_id=offer.external_id[:200],
        url=offer.url[:2000],
        title=truncate(offer.title, 300) or "",
        company=truncate(offer.company, 200),
        location=truncate(offer.location, 300),
        country=offer.country,
        work_mode=offer.work_mode,
        language=detect_language(f"{offer.title}\n{offer.description}"),
        description=offer.description,
        tags=[tag[:100] for tag in offer.tags],
        salary=truncate(offer.salary, 100),
        published_at=offer.published_at,
    )


def embed_pending_offers(db: Session, embedder: Embedder) -> int:
    """Compute the embedding of every offer that has none yet. Returns how many."""
    count = 0
    while batch := _offers_without_embedding(db, EMBEDDING_BATCH_SIZE):
        _embed(batch, embedder)
        db.commit()
        count += len(batch)
    return count


def _embed(offers: Sequence[JobOffer], embedder: Embedder) -> None:
    vectors = embedder.embed([offer_text(offer) for offer in offers])
    for offer, vector in zip(offers, vectors, strict=True):
        offer.embedding = vector


def _offers_without_embedding(db: Session, limit: int) -> Sequence[JobOffer]:
    return db.scalars(select(JobOffer).where(JobOffer.embedding.is_(None)).limit(limit)).all()


def _known_keys(db: Session, keys: list[tuple[str, str]]) -> set[tuple[str, str]]:
    if not keys:
        return set()
    rows = db.execute(
        select(JobOffer.source, JobOffer.external_id).where(
            tuple_(JobOffer.source, JobOffer.external_id).in_(keys)
        )
    )
    return {(source, external_id) for source, external_id in rows}
