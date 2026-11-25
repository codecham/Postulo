"""The job boards the search uses, given the server settings."""

from dataclasses import dataclass

import httpx

from app.core.config import Settings
from app.services.job_search.sources.adzuna import AdzunaSource
from app.services.job_search.sources.base import JobSource
from app.services.job_search.sources.himalayas import HimalayasSource
from app.services.job_search.sources.jobicy import JobicySource
from app.services.job_search.sources.remotive import RemotiveSource


@dataclass(frozen=True)
class SourceInfo:
    name: str
    url: str
    enabled: bool


def adzuna_configured(settings: Settings) -> bool:
    return settings.adzuna_app_id is not None and settings.adzuna_app_key is not None


def source_infos(settings: Settings) -> list[SourceInfo]:
    """Every supported job board and whether this server uses it."""
    return [
        SourceInfo("remotive", "https://remotive.com", enabled=True),
        SourceInfo("jobicy", "https://jobicy.com", enabled=True),
        SourceInfo("himalayas", "https://himalayas.app", enabled=True),
        SourceInfo("adzuna", "https://www.adzuna.be", enabled=adzuna_configured(settings)),
    ]


def build_sources(settings: Settings, client: httpx.Client) -> list[JobSource]:
    sources: list[JobSource] = [
        RemotiveSource(client),
        JobicySource(client),
        HimalayasSource(client),
    ]
    if settings.adzuna_app_id is not None and settings.adzuna_app_key is not None:
        api_key = settings.adzuna_app_key.get_secret_value()
        sources.append(AdzunaSource(client, settings.adzuna_app_id, api_key))
    return sources
