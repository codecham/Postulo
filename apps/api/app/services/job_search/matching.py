"""Find the offers that fit a user, with pgvector, and save them as matches."""

import uuid
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import delete, func, or_, select, text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.models import JobMatch, JobOffer, MatchStatus
from app.services.job_search.criteria import SearchCriteria
from app.services.job_search.filters import fits_criteria
from app.services.job_search.scoring import find_skills, score_offer

# Offers older than this are probably filled already
MAX_OFFER_AGE = timedelta(days=30)
# How many of the closest offers (by meaning) are checked against the criteria
CANDIDATES = 300


@dataclass(frozen=True)
class ScoredOffer:
    offer: JobOffer
    similarity: float
    score: int
    matched_skills: list[str]


def match_offers(
    db: Session,
    user_id: uuid.UUID,
    criteria: SearchCriteria,
    profile_vector: Sequence[float],
    min_score: int,
) -> int:
    """Save (or refresh) the user's matches and return how many fit."""
    candidates = nearest_offers(db, profile_vector, CANDIDATES)
    scored = [score(offer, similarity, criteria) for offer, similarity in candidates]
    matches = [item for item in scored if item.score >= min_score]
    matches = [item for item in matches if fits_criteria(item.offer, criteria)]
    save_matches(db, user_id, matches)
    return len(matches)


def nearest_offers(
    db: Session, vector: Sequence[float], limit: int
) -> list[tuple[JobOffer, float]]:
    """The recent offers closest in meaning to the vector, with their cosine similarity."""
    # The HNSW index returns at most `ef_search` rows (40 by default): ask for enough
    db.execute(text(f"SET LOCAL hnsw.ef_search = {int(limit)}"))
    distance = JobOffer.embedding.cosine_distance(vector)
    since = datetime.now(UTC) - MAX_OFFER_AGE
    rows = db.execute(
        select(JobOffer, distance)
        .where(JobOffer.embedding.is_not(None))
        .where(or_(JobOffer.published_at >= since, JobOffer.published_at.is_(None)))
        .order_by(distance)
        .limit(limit)
    ).all()
    return [(offer, 1 - float(offer_distance)) for offer, offer_distance in rows]


def score(offer: JobOffer, similarity: float, criteria: SearchCriteria) -> ScoredOffer:
    skills = find_skills(
        f"{offer.title}\n{' '.join(offer.tags)}\n{offer.description}", criteria.skills
    )
    return ScoredOffer(
        offer=offer,
        similarity=similarity,
        score=score_offer(similarity, len(skills), len(criteria.skills)),
        matched_skills=skills,
    )


def save_matches(db: Session, user_id: uuid.UUID, matches: Sequence[ScoredOffer]) -> None:
    """Make these the user's matches: the profile or the criteria may have changed.

    Known matches are updated in place, so they keep their creation date and status.
    Only new matches that no longer fit are removed: the saved ones stay on the
    shortlist, and the dismissed ones stay hidden even if they fit again later.
    """
    offer_ids = [item.offer.id for item in matches]
    db.execute(
        delete(JobMatch).where(
            JobMatch.user_id == user_id,
            JobMatch.status == MatchStatus.NEW,
            JobMatch.offer_id.not_in(offer_ids),
        )
    )
    if not matches:
        db.commit()
        return
    statement = insert(JobMatch).values(
        [
            {
                "id": uuid.uuid4(),
                "user_id": user_id,
                "offer_id": item.offer.id,
                "score": item.score,
                "similarity": item.similarity,
                "matched_skills": item.matched_skills,
            }
            for item in matches
        ]
    )
    db.execute(
        statement.on_conflict_do_update(
            constraint="uq_job_matches_user_offer",
            set_={
                "score": statement.excluded.score,
                "similarity": statement.excluded.similarity,
                "matched_skills": statement.excluded.matched_skills,
                "updated_at": func.now(),
            },
        )
    )
    db.commit()
