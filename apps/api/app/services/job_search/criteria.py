"""What a job search looks for, read from the user's profile."""

from dataclasses import dataclass

from app.models import Profile

# Each keyword costs one request per job board: keep the searches polite and fast
MAX_KEYWORDS = 5


@dataclass(frozen=True)
class SearchCriteria:
    keywords: tuple[str, ...]
    skills: tuple[str, ...]
    countries: tuple[str, ...]
    work_modes: tuple[str, ...]  # empty: any work mode
    open_to_remote_abroad: bool
    offer_languages: tuple[str, ...]  # empty: any language

    @classmethod
    def from_profile(cls, profile: Profile) -> SearchCriteria:
        return cls(
            keywords=search_keywords(profile),
            skills=tuple(profile.skills),
            countries=tuple(profile.countries),
            work_modes=tuple(profile.work_modes),
            open_to_remote_abroad=profile.open_to_remote_abroad,
            offer_languages=tuple(profile.offer_languages),
        )

    @property
    def is_searchable(self) -> bool:
        """False when the profile gives nothing to look for."""
        return bool(self.keywords or self.skills)

    def accepts_work_mode(self, work_mode: str) -> bool:
        return not self.work_modes or work_mode in self.work_modes


def search_keywords(profile: Profile) -> tuple[str, ...]:
    """The job titles the user wants, or their headline when they listed none."""
    if profile.desired_titles:
        return tuple(profile.desired_titles[:MAX_KEYWORDS])
    if profile.headline:
        return (profile.headline,)
    return ()
