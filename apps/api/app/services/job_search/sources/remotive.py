"""Remotive (https://remotive.com): remote jobs, free API without key.

The public API ignores search filters: it always returns its latest jobs (delayed), so
one request per search is enough. Terms: link back to the offer and name Remotive.
"""

from typing import Any

import httpx

from app.services.job_search.criteria import SearchCriteria
from app.services.job_search.errors import SourceError
from app.services.job_search.offer import CollectedOffer
from app.services.job_search.sources.base import (
    get_json,
    parse_datetime,
    string_list,
    text_or_none,
)
from app.services.job_search.text import html_to_text

API_URL = "https://remotive.com/api/remote-jobs"
LIMIT = 50


class RemotiveSource:
    name = "remotive"

    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    def fetch(self, criteria: SearchCriteria) -> list[CollectedOffer]:
        return parse_jobs(get_json(self._client, API_URL, {"limit": LIMIT}))


def parse_jobs(data: Any) -> list[CollectedOffer]:
    if not isinstance(data, dict) or not isinstance(data.get("jobs"), list):
        raise SourceError("remotive: unexpected answer")
    return [offer for job in data["jobs"] if (offer := parse_job(job)) is not None]


def parse_job(job: Any) -> CollectedOffer | None:
    """One offer, or None when an essential field is missing."""
    if not isinstance(job, dict) or not job.get("id") or not job.get("url") or not job.get("title"):
        return None
    return CollectedOffer(
        source=RemotiveSource.name,
        external_id=str(job["id"]),
        url=job["url"],
        title=job["title"].strip(),
        description=html_to_text(job.get("description") or ""),
        company=text_or_none(job.get("company_name")),
        location=text_or_none(job.get("candidate_required_location")),
        work_mode="remote",
        tags=string_list(job.get("tags")),
        salary=text_or_none(job.get("salary")),
        published_at=parse_datetime(job.get("publication_date")),
    )
