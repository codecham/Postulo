"""Himalayas (https://himalayas.app): remote jobs, free API without key.

The search can keep only the jobs open to people living in a given country.
"""

from typing import Any

import httpx

from app.services.job_search.criteria import SearchCriteria
from app.services.job_search.errors import SourceError
from app.services.job_search.offer import CollectedOffer
from app.services.job_search.regions import COUNTRY_NAMES
from app.services.job_search.sources.base import (
    get_json,
    keywords_or_none,
    parse_timestamp,
    salary_range,
    string_list,
    text_or_none,
)
from app.services.job_search.text import html_to_text

API_URL = "https://himalayas.app/jobs/api/search"
# The search returns 20 jobs per page
PAGES = 2
# Longer lists of allowed countries are summarized ("Belgium and 40 other countries")
MAX_LISTED_COUNTRIES = 5


class HimalayasSource:
    name = "himalayas"

    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    def fetch(self, criteria: SearchCriteria) -> list[CollectedOffer]:
        country = home_country_name(criteria)
        offers: list[CollectedOffer] = []
        for keyword in keywords_or_none(criteria):
            for page in range(1, PAGES + 1):
                params: dict[str, Any] = {"page": page}
                if keyword:
                    params["q"] = keyword
                if country:
                    params["country"] = country
                offers.extend(parse_jobs(get_json(self._client, API_URL, params), country))
        return offers


def home_country_name(criteria: SearchCriteria) -> str | None:
    """The English name of the user's first country, as Himalayas expects it."""
    for country in criteria.countries:
        if names := COUNTRY_NAMES.get(country):
            return names[0].title()
    return None


def parse_jobs(data: Any, home_country: str | None) -> list[CollectedOffer]:
    if not isinstance(data, dict) or not isinstance(data.get("jobs"), list):
        raise SourceError("himalayas: unexpected answer")
    return [offer for job in data["jobs"] if (offer := parse_job(job, home_country)) is not None]


def parse_job(job: Any, home_country: str | None) -> CollectedOffer | None:
    if not isinstance(job, dict):
        return None
    url = text_or_none(job.get("applicationLink")) or text_or_none(job.get("guid"))
    title = text_or_none(job.get("title"))
    if url is None or title is None:
        return None
    return CollectedOffer(
        source=HimalayasSource.name,
        external_id=text_or_none(job.get("guid")) or url,
        url=url,
        title=title,
        description=html_to_text(job.get("description") or job.get("excerpt") or ""),
        company=text_or_none(job.get("companyName")),
        location=describe_region(string_list(job.get("locationRestrictions")), home_country),
        work_mode="remote",
        tags=string_list(job.get("categories")),
        salary=salary_range(
            job.get("minSalary"), job.get("maxSalary"), text_or_none(job.get("currency")) or ""
        ),
        published_at=parse_timestamp(job.get("pubDate")),
    )


def describe_region(countries: tuple[str, ...], home_country: str | None) -> str:
    """Where the job can be done from, short enough to store and to read."""
    if not countries:
        return "Worldwide"
    if len(countries) <= MAX_LISTED_COUNTRIES:
        return ", ".join(countries)
    first = home_country if home_country in countries else countries[0]
    return f"{first} and {len(countries) - 1} other countries"
