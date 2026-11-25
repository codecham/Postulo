from typing import Any

import httpx
import pytest

from app.services.job_search.errors import SourceError
from app.services.job_search.sources import adzuna, himalayas, jobicy, remotive
from app.services.job_search.sources.adzuna import AdzunaSource
from app.services.job_search.sources.base import parse_timestamp, salary_range
from app.services.job_search.sources.himalayas import HimalayasSource
from app.services.job_search.sources.jobicy import search_tags
from app.services.job_search.sources.remotive import RemotiveSource
from tests.services.job_search.helpers import make_criteria

REMOTIVE_JOB = {
    "id": 2091179,
    "url": "https://remotive.com/remote-jobs/software-development/python-dev",
    "title": "Python Developer ",
    "company_name": "Acme",
    "tags": ["python", "django"],
    "publication_date": "2026-11-24T10:31:32",
    "candidate_required_location": "Europe",
    "salary": "$57K - $67K",
    "description": "<p>Build <b>APIs</b></p>",
}
JOBICY_JOB = {
    "id": 164244,
    "url": "https://jobicy.com/jobs/164244-python",
    "jobTitle": "Python Engineer",
    "companyName": "Ashby",
    "jobIndustry": ["Engineering"],
    "jobGeo": "Anywhere",
    "jobDescription": "<p>Hello</p>",
    "pubDate": "2026-11-25T11:36:48+00:00",
    "salaryMin": "100000",
    "salaryMax": "130000",
    "salaryCurrency": "EUR",
}
HIMALAYAS_JOB = {
    "guid": "https://himalayas.app/companies/acme/jobs/python-developer",
    "applicationLink": "https://himalayas.app/companies/acme/jobs/python-developer",
    "title": "Python developer",
    "companyName": "Acme",
    "categories": ["Software-Engineer"],
    "locationRestrictions": [],
    "description": "<p>Remote job</p>",
    "pubDate": "1795644209",
    "minSalary": None,
    "maxSalary": None,
    "currency": None,
}
ADZUNA_JOB = {
    "id": "5012345",
    "redirect_url": "https://www.adzuna.be/details/5012345",
    "title": "<strong>Python</strong> developer",
    "description": "Poste hybride à Bruxelles",
    "company": {"display_name": "Belgian Co"},
    "location": {"display_name": "Bruxelles"},
    "created": "2026-11-20T08:00:00Z",
    "salary_min": 45000,
    "salary_max": 0,
}


def test_remotive_jobs_become_remote_offers() -> None:
    [offer] = remotive.parse_jobs({"jobs": [REMOTIVE_JOB]})

    assert offer.external_id == "2091179"
    assert offer.title == "Python Developer"
    assert offer.description == "Build APIs"
    assert offer.work_mode == "remote"
    assert offer.location == "Europe"
    assert offer.tags == ("python", "django")
    assert offer.published_at is not None and offer.published_at.tzinfo is not None


def test_jobicy_jobs_become_remote_offers_with_a_salary() -> None:
    [offer] = jobicy.parse_jobs({"jobs": [JOBICY_JOB]})

    assert offer.title == "Python Engineer"
    assert offer.salary == "100000-130000 EUR"
    assert offer.location == "Anywhere"


def test_jobicy_without_results_gives_no_offer() -> None:
    assert jobicy.parse_jobs({"success": True, "jobCount": 0}) == []


def test_adzuna_jobs_get_their_country_and_a_guessed_work_mode() -> None:
    [offer] = adzuna.parse_jobs({"results": [ADZUNA_JOB]}, "BE")

    assert offer.title == "Python developer"
    assert offer.country == "BE"
    assert offer.work_mode == "hybrid"
    assert offer.company == "Belgian Co"
    assert offer.salary == "45000"


def test_himalayas_jobs_without_restriction_are_worldwide() -> None:
    [offer] = himalayas.parse_jobs({"jobs": [HIMALAYAS_JOB]}, "Belgium")

    assert offer.location == "Worldwide"
    assert offer.work_mode == "remote"
    assert offer.published_at is not None
    assert offer.salary is None


def test_himalayas_long_country_lists_are_summarized_around_the_users_country() -> None:
    countries = ["Austria", "Belgium", "Croatia", "Denmark", "France", "Germany"]

    assert himalayas.describe_region(tuple(countries[:2]), "Belgium") == "Austria, Belgium"
    assert himalayas.describe_region(tuple(countries), "Belgium") == (
        "Belgium and 5 other countries"
    )


def test_jobs_missing_an_essential_field_are_skipped() -> None:
    incomplete = {key: value for key, value in REMOTIVE_JOB.items() if key != "url"}

    assert remotive.parse_jobs({"jobs": [incomplete, REMOTIVE_JOB]})[0].external_id == "2091179"
    assert len(remotive.parse_jobs({"jobs": [incomplete]})) == 0


def test_an_unexpected_answer_raises_source_error() -> None:
    with pytest.raises(SourceError):
        remotive.parse_jobs({"error": "nope"})


def test_salary_range_ignores_missing_bounds() -> None:
    assert salary_range(None, "0") is None
    assert salary_range("50000.4", 60000, "EUR") == "50000-60000 EUR"


def test_parse_timestamp_reads_unix_seconds() -> None:
    assert parse_timestamp("0") is None
    assert parse_timestamp(None) is None
    parsed = parse_timestamp("1795644209")
    assert parsed is not None and parsed.year == 2026


def client_answering(status: int, body: Any, requests: list[httpx.Request]) -> httpx.Client:
    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(status, json=body)

    return httpx.Client(transport=httpx.MockTransport(handler))


def test_remotive_makes_a_single_request() -> None:
    requests: list[httpx.Request] = []
    source = RemotiveSource(client_answering(200, {"jobs": [REMOTIVE_JOB]}, requests))

    offers = source.fetch(make_criteria(keywords=("Python developer", "Data engineer")))

    assert len(offers) == 1
    assert len(requests) == 1


def test_jobicy_searches_the_distinct_words_of_the_titles() -> None:
    criteria = make_criteria(keywords=("Python developer", "Backend developer", "QA"))

    assert search_tags(criteria) == ("python", "developer", "backend")


def test_himalayas_searches_each_title_among_jobs_open_to_the_users_country() -> None:
    requests: list[httpx.Request] = []
    source = HimalayasSource(client_answering(200, {"jobs": [HIMALAYAS_JOB]}, requests))

    source.fetch(make_criteria(keywords=("Python developer",), countries=("BE",)))

    assert [(r.url.params["q"], r.url.params["country"]) for r in requests] == [
        ("Python developer", "Belgium"),
        ("Python developer", "Belgium"),
    ]
    assert [r.url.params["page"] for r in requests] == ["1", "2"]


def test_adzuna_only_searches_the_countries_it_covers() -> None:
    requests: list[httpx.Request] = []
    client = client_answering(200, {"results": []}, requests)
    source = AdzunaSource(client, "my-id", "my-key")

    source.fetch(make_criteria(countries=("BE", "LU"), keywords=("Python",)))

    assert [request.url.path for request in requests] == ["/v1/api/jobs/be/search/1"]
    assert requests[0].url.params["app_key"] == "my-key"


def test_an_http_error_raises_source_error_without_the_api_key() -> None:
    client = client_answering(500, {}, [])
    source = AdzunaSource(client, "my-id", "my-key")

    with pytest.raises(SourceError) as error:
        source.fetch(make_criteria())

    assert "my-key" not in str(error.value)
