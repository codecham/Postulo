"""How well an offer fits a profile, as a score from 0 to 100.

Mostly the meaning (embedding similarity), plus a bonus for the profile's skills that
the offer names explicitly. Simple on purpose: easy to explain to the user.
"""

import re
from collections.abc import Iterable

# Cosine similarities of model2vec embeddings, measured on real offers: unrelated jobs
# score about 0.4 against a developer profile, very close jobs 0.8. Scale that to 0-1.
SIMILARITY_FLOOR = 0.40
SIMILARITY_CEILING = 0.80
SKILLS_WEIGHT = 0.25
# Finding this many of the user's skills gives the full skill bonus
SKILLS_FOR_FULL_BONUS = 5


def score_offer(similarity: float, matched_skills: int, total_skills: int) -> int:
    meaning = _scale(similarity, SIMILARITY_FLOOR, SIMILARITY_CEILING)
    if total_skills == 0:
        return round(100 * meaning)
    skills = min(matched_skills / min(total_skills, SKILLS_FOR_FULL_BONUS), 1.0)
    return round(100 * ((1 - SKILLS_WEIGHT) * meaning + SKILLS_WEIGHT * skills))


def find_skills(text: str, skills: Iterable[str]) -> list[str]:
    """The skills the text names as whole words, ignoring case ("Go" is not in "good")."""
    return [skill for skill in skills if _mentions(text, skill)]


def _mentions(text: str, skill: str) -> bool:
    # \b fails around symbols ("C++", ".NET"): look for non-word neighbours instead
    pattern = rf"(?<!\w){re.escape(skill)}(?!\w)"
    return re.search(pattern, text, re.IGNORECASE) is not None


def _scale(value: float, low: float, high: float) -> float:
    return min(max((value - low) / (high - low), 0.0), 1.0)
