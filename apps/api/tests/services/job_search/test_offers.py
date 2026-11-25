from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import JobOffer
from app.services.job_search.offers import embed_pending_offers, save_offers
from tests.fakes import FakeEmbedder, make_collected_offer


def count_offers(db: Session) -> int:
    return db.scalar(select(func.count()).select_from(JobOffer)) or 0


def test_save_offers_stores_each_offer_once(db: Session) -> None:
    first = make_collected_offer(external_id="1")
    second = make_collected_offer(external_id="2")

    saved = save_offers(db, [first, second, first])
    saved_again = save_offers(db, [first])

    assert (saved.found, saved.new) == (2, 2)
    assert (saved_again.found, saved_again.new) == (1, 0)
    assert count_offers(db) == 2


def test_the_same_id_from_two_sources_is_two_offers(db: Session) -> None:
    save_offers(db, [make_collected_offer(source="a"), make_collected_offer(source="b")])

    assert count_offers(db) == 2


def test_saved_offers_get_their_language(db: Session) -> None:
    description = "Nous cherchons un développeur pour notre équipe, vous travaillerez avec nous."

    save_offers(db, [make_collected_offer(description=description)])

    assert db.scalar(select(JobOffer.language)) == "fr"


def test_embed_pending_offers_fills_the_missing_embeddings(db: Session) -> None:
    save_offers(db, [make_collected_offer(external_id="1"), make_collected_offer(external_id="2")])

    embedded = embed_pending_offers(db, FakeEmbedder())
    embedded_again = embed_pending_offers(db, FakeEmbedder())

    assert (embedded, embedded_again) == (2, 0)
    assert db.scalar(select(func.count()).where(JobOffer.embedding.is_(None))) == 0
