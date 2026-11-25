"""Adzuna (https://developer.adzuna.com): jobs of many countries, Belgium included.

The API is free but needs an app id and key. Without them, this source is skipped.
"""

from typing import Any

import httpx

from app.services.job_search.criteria import SearchCriteria
from app.services.job_search.errors import SourceError
from app.services.job_search.offer import CollectedOffer
from app.services.job_search.sources.base import (
    get_json,
    keywords_or_none,
    parse_datetime,
    salary_range,
    text_or_none,
)
from app.services.job_search.text import guess_work_mode, html_to_text

API_URL = "https://api.adzuna.com/v1/api/jobs/{country}/search/1"
RESULTS_PER_PAGE = 50
MAX_DAYS_OLD = 30
# Countries Adzuna covers (ISO 3166-1 alpha-2)
COUNTRIES = frozenset(
    {"AT", "AU", "BE", "BR", "CA", "CH", "DE", "ES", "FR", "GB", "IN"}
    | {"IT", "MX", "NL", "NZ", "PL", "SG", "US", "ZA"}
)


class AdzunaSource:
    name = "adzuna"

    def __init__(self, client: httpx.Client, app_id: str, app_key: str) -> None:
        self._client = client
        self._credentials = {"app_id": app_id, "app_key": app_key}

    def fetch(self, criteria: SearchCriteria) -> list[CollectedOffer]:
        offers: list[CollectedOffer] = []
        for country in (c for c in criteria.countries if c in COUNTRIES):
            for keyword in keywords_or_none(criteria):
                offers.extend(self._search(country, keyword))
        return offers

    def _search(self, country: str, keyword: str | None) -> list[CollectedOffer]:
        params: dict[str, Any] = {
            **self._credentials,
            "results_per_page": RESULTS_PER_PAGE,
            "max_days_old": MAX_DAYS_OLD,
        }
        if keyword:
            params["what"] = keyword
        url = API_URL.format(country=country.lower())
        return parse_jobs(get_json(self._client, url, params), country)


def parse_jobs(data: Any, country: str) -> list[CollectedOffer]:
    if not isinstance(data, dict) or not isinstance(data.get("results"), list):
        raise SourceError("adzuna: unexpected answer")
    return [offer for job in data["results"] if (offer := parse_job(job, country)) is not None]


def parse_job(job: Any, country: str) -> CollectedOffer | None:
    if not isinstance(job, dict) or not job.get("id") or not job.get("redirect_url"):
        return None
    # Adzuna highlights the search words with <strong> tags
    title = html_to_text(job.get("title") or "")
    if not title:
        return None
    description = html_to_text(job.get("description") or "")
    return CollectedOffer(
        source=AdzunaSource.name,
        external_id=str(job["id"]),
        url=job["redirect_url"],
        title=title,
        description=description,
        company=text_or_none(_display_name(job.get("company"))),
        location=text_or_none(_display_name(job.get("location"))),
        country=country,
        work_mode=guess_work_mode(f"{title}\n{description}"),
        salary=salary_range(job.get("salary_min"), job.get("salary_max")),
        published_at=parse_datetime(job.get("created")),
    )


def _display_name(value: object) -> object:
    return value.get("display_name") if isinstance(value, dict) else None
