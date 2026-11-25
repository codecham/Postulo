from datetime import date

import pytest

from app.models import Experience, Profile
from app.schemas.application import ApplicationLanguage
from app.services.applications.context import (
    MAX_OFFER_DESCRIPTION_LENGTH,
    build_context,
    document_language,
)
from tests.services.job_search.helpers import make_offer


@pytest.mark.parametrize(
    ("offer_language", "expected"),
    [("fr", ApplicationLanguage.FR), ("en", ApplicationLanguage.EN), ("nl", "en"), (None, "en")],
)
def test_document_language_follows_the_offer_or_falls_back_to_english(
    offer_language: str | None, expected: ApplicationLanguage
) -> None:
    offer = make_offer(language=offer_language)

    assert document_language(offer) == expected


def test_build_context_gives_months_and_flags_the_current_job() -> None:
    profile = Profile(full_name="Alice", skills=["Python"], languages=["fr"])
    experience = Experience(
        title="Developer", company="Acme", start_date=date(2022, 1, 1), end_date=None
    )

    context = build_context(profile, [experience], [], make_offer())

    [described] = context.candidate["experiences"]
    assert described["start_month"] == "2022-01"
    assert described["end_month"] is None
    assert described["is_current"] is True


def test_build_context_cuts_a_very_long_offer() -> None:
    offer = make_offer(description="x" * (MAX_OFFER_DESCRIPTION_LENGTH + 100))

    context = build_context(Profile(skills=[], languages=[]), [], [], offer)

    assert len(context.offer["description"]) == MAX_OFFER_DESCRIPTION_LENGTH


def test_the_prompt_names_the_language_and_keeps_accents() -> None:
    profile = Profile(full_name="Zoé", skills=[], languages=[])

    prompt = build_context(profile, [], [], make_offer(language="fr")).as_prompt()

    assert prompt.startswith("Document language: fr")
    assert "Zoé" in prompt
