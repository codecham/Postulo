from datetime import date

from app.models import Education, Experience, Profile
from app.schemas.education import EducationCreate
from app.schemas.experience import ExperienceCreate
from app.schemas.profile import ProfileUpdate
from app.services.cv_import.merge import (
    mark_known_educations,
    mark_known_experiences,
    merge_profile,
)


def make_profile(**changes: object) -> Profile:
    """An unsaved profile: merge only reads its attributes."""
    fields: dict[str, object] = {
        "full_name": "Alice",
        "headline": None,
        "summary": "My own summary",
        "city": "Liège",
        "skills": ["Python"],
        "languages": ["fr"],
        "desired_titles": [],
        "work_modes": ["hybrid"],
        "countries": ["BE"],
        "open_to_remote_abroad": True,
    }
    return Profile(**(fields | changes))


def test_values_from_the_cv_win_and_missing_ones_keep_the_current_value() -> None:
    extracted = ProfileUpdate(full_name="Alice Martin", headline="Developer", summary=None)

    merged = merge_profile(make_profile(), extracted)

    assert merged.full_name == "Alice Martin"
    assert merged.headline == "Developer"
    assert merged.summary == "My own summary"
    assert merged.city == "Liège"


def test_lists_are_combined_without_duplicates() -> None:
    extracted = ProfileUpdate(skills=["python", "SQL"], work_modes=["remote"])

    merged = merge_profile(make_profile(), extracted)

    assert merged.skills == ["Python", "SQL"]
    assert merged.work_modes == ["hybrid", "remote"]
    assert merged.countries == ["BE"]


def test_open_to_remote_abroad_is_never_switched_off() -> None:
    merged = merge_profile(make_profile(), ProfileUpdate(open_to_remote_abroad=False))

    assert merged.open_to_remote_abroad is True


def test_experiences_the_user_already_has_are_marked() -> None:
    current = [
        Experience(title="Developer", company="ACME", start_date=date(2022, 1, 15)),
    ]
    extracted = [
        ExperienceCreate(title="developer", company="Acme", start_date=date(2022, 1, 1)),
        ExperienceCreate(title="Intern", company="Acme", start_date=date(2021, 6, 1)),
    ]

    marked = mark_known_experiences(current, extracted)

    assert [item.already_exists for item in marked] == [True, False]


def test_educations_the_user_already_has_are_marked() -> None:
    current = [Education(school="42 PARIS", degree="RNCP level 7")]
    extracted = [
        EducationCreate(school="42 Paris", degree="rncp level 7"),
        EducationCreate(school="42 Paris", degree="Piscine"),
    ]

    marked = mark_known_educations(current, extracted)

    assert [item.already_exists for item in marked] == [True, False]
