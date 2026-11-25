"""Jobicy (https://jobicy.com): remote jobs, free API without key.

Its `tag` filter matches single words only ("python", "backend"), not whole job titles.

Terms: credit Jobicy with a link, and send applications to the original offer URL.
"""

from typing import Any

import httpx

from app.services.job_search.criteria import SearchCriteria
from app.services.job_search.errors import SourceError
from app.services.job_search.offer import CollectedOffer
from app.services.job_search.sources.base import (
    get_json,
    parse_datetime,
    salary_range,
    string_list,
    text_or_none,
)
from app.services.job_search.text import html_to_text

API_URL = "https://jobicy.com/api/v2/remote-jobs"
COUNT = 50
MAX_TAGS = 5
MIN_TAG_LENGTH = 3


class JobicySource:
    name = "jobicy"

    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    def fetch(self, criteria: SearchCriteria) -> list[CollectedOffer]:
        offers: list[CollectedOffer] = []
        for tag in search_tags(criteria) or (None,):
            params: dict[str, Any] = {"count": COUNT}
            if tag:
                params["tag"] = tag
            offers.extend(parse_jobs(get_json(self._client, API_URL, params)))
        return offers


def search_tags(criteria: SearchCriteria) -> tuple[str, ...]:
    """The distinct words of the job titles: "Python developer" -> python, developer."""
    words = (word.casefold() for keyword in criteria.keywords for word in keyword.split())
    unique = dict.fromkeys(word for word in words if len(word) >= MIN_TAG_LENGTH)
    return tuple(unique)[:MAX_TAGS]


def parse_jobs(data: Any) -> list[CollectedOffer]:
    if not isinstance(data, dict):
        raise SourceError("jobicy: unexpected answer")
    # No match for a keyword: Jobicy answers without a "jobs" list
    jobs = data.get("jobs") or []
    if not isinstance(jobs, list):
        raise SourceError("jobicy: unexpected answer")
    return [offer for job in jobs if (offer := parse_job(job)) is not None]


def parse_job(job: Any) -> CollectedOffer | None:
    if not isinstance(job, dict) or not job.get("id") or not job.get("url"):
        return None
    title = text_or_none(job.get("jobTitle"))
    if title is None:
        return None
    return CollectedOffer(
        source=JobicySource.name,
        external_id=str(job["id"]),
        url=job["url"],
        title=title,
        description=html_to_text(job.get("jobDescription") or job.get("jobExcerpt") or ""),
        company=text_or_none(job.get("companyName")),
        location=text_or_none(job.get("jobGeo")),
        work_mode="remote",
        tags=string_list(job.get("jobIndustry")),
        salary=salary_range(
            job.get("salaryMin"), job.get("salaryMax"), job.get("salaryCurrency") or ""
        ),
        published_at=parse_datetime(job.get("pubDate")),
    )
