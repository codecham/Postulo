"""The user's hunt settings: a JSON file on their machine, never in the repository.

It holds personal data (phone, answers to application forms): keep it out of git.
"""

import os
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

DEFAULT_PATH = Path("~/.config/postulo/hunt.json")
# The job boards browsed in Chrome. Remotive, Jobicy and Himalayas are not listed:
# the search already reads them through their public APIs.
DEFAULT_BOARDS = [
    "linkedin",
    "indeed",
    "welcometothejungle",
    "ictjob",
    "jobat",
    "weworkremotely",
]


class Applicant(BaseModel):
    """What application forms ask and the profile does not hold."""

    model_config = ConfigDict(extra="forbid")

    phone: str | None = None
    links: list[str] = Field(default=[], max_length=5)  # LinkedIn, GitHub, portfolio...
    # Answers to the usual form questions, by topic: "work_permit", "notice_period",
    # "salary_expectation", "how_did_you_hear"... Claude asks the user for the others.
    answers: dict[str, str] = {}


class HuntSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str  # the Postulo account the hunt works for
    applications_per_day: int = Field(default=6, ge=1, le=15)
    boards: list[str] = DEFAULT_BOARDS
    dossiers_dir: Path = Path("~/Documents/Postulo/Candidatures")
    # The Chrome to use when several are connected to the Claude account (its deviceId
    # from list_connected_browsers). None: the only one connected.
    browser_device_id: str | None = None
    applicant: Applicant = Applicant()


def settings_path() -> Path:
    return Path(os.environ.get("POSTULO_HUNT_SETTINGS", DEFAULT_PATH)).expanduser()


def load_settings(path: Path) -> HuntSettings:
    settings = HuntSettings.model_validate_json(path.read_text())
    return settings.model_copy(update={"dossiers_dir": settings.dossiers_dir.expanduser()})
