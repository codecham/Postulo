"""One function per command. Each prints JSON for Claude and returns the exit status."""

import json
import time
import uuid
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app.models import JobMatch, MatchStatus, User
from app.schemas.application import GeneratedApplication
from app.schemas.hunt import BrowserFindings
from app.services import profiles
from app.services.hunt import applying, dossier, search, selection
from app.services.job_search import dashboard
from app.services.job_search.criteria import SearchCriteria
from scripts.hunt.settings import HuntSettings

# Enough of the offer to judge it; the full text is in the dossier and on the page
DESCRIPTION_EXCERPT = 1500


@dataclass(frozen=True)
class Context:
    db: Session
    user: User
    settings: HuntSettings


def print_json(data: Any) -> None:
    print(json.dumps(data, indent=2, ensure_ascii=False, default=str))


def brief(ctx: Context) -> int:
    """What to look for and where: the profile's criteria and the hunt settings."""
    profile = profiles.get_or_create_profile(ctx.db, ctx.user.id)
    criteria = SearchCriteria.from_profile(profile)
    print_json(
        {
            "headline": profile.headline,
            "city": profile.city,
            "keywords": criteria.keywords,
            "skills": criteria.skills,
            "countries": criteria.countries,
            "work_modes": criteria.work_modes or "any",
            "open_to_remote_abroad": criteria.open_to_remote_abroad,
            "offer_languages": criteria.offer_languages or "any",
            "boards": ctx.settings.boards,
            "applications_per_day": ctx.settings.applications_per_day,
        }
    )
    return 0


def run_search(ctx: Context, findings_file: Path | None, timeout_minutes: int) -> int:
    """Save the offers found in the browser, then run the search and wait for it."""
    findings = (
        BrowserFindings.model_validate_json(findings_file.read_text())
        if findings_file
        else BrowserFindings(offers=[])
    )
    saved, run = search.run_search(
        ctx.db, ctx.user.id, findings, timedelta(minutes=timeout_minutes), time.sleep
    )
    print_json(
        {
            "browser_offers": {"found": saved.found, "new": saved.new},
            "search": {
                "status": run.status,
                "offers_found": run.offers_found,
                "offers_new": run.offers_new,
                "matches_found": run.matches_found,
                "failed_sources": run.failed_sources,
                "error": run.error,
            },
        }
    )
    return 0 if run.error is None else 1


def candidates(ctx: Context, limit: int) -> int:
    """The best new matches with no application yet, to choose today's ones from."""
    matches = selection.list_candidates(ctx.db, ctx.user.id, limit)
    print_json([match_summary(match, DESCRIPTION_EXCERPT) for match in matches])
    return 0


def save_application(ctx: Context, match_id: uuid.UUID, application_file: Path) -> int:
    """Save a validated application and write its dossier."""
    generated = GeneratedApplication.model_validate_json(application_file.read_text())
    details = applying.ContactDetails(
        phone=ctx.settings.applicant.phone, links=ctx.settings.applicant.links
    )
    applying.save_application(ctx.db, ctx.user, match_id, generated, details)
    return write_dossier(ctx, match_id)


def ready(ctx: Context, count_only: bool) -> int:
    """The applications waiting for the user's go, numbered for "go 1 3"."""
    matches = selection.list_ready(ctx.db, ctx.user.id)
    if count_only:
        print(len(matches))
        return 0
    items = [
        {"number": number, **match_summary(match, description_length=0)}
        for number, match in enumerate(matches, start=1)
    ]
    print_json(items)
    return 0


def write_dossier(ctx: Context, match_id: uuid.UUID) -> int:
    """(Re)write the PDFs from the application as the user last reviewed it."""
    written = dossier.write_dossier(
        ctx.db, ctx.user.id, match_id, ctx.settings.dossiers_dir, date.today()
    )
    print_json(
        {
            "folder": written.folder,
            "cv": written.cv,
            "cover_letter": written.cover_letter,
            "offer": written.offer,
        }
    )
    return 0


def mark_sent(ctx: Context, match_id: uuid.UUID, notes: str | None) -> int:
    tracking = applying.mark_sent(ctx.db, ctx.user.id, match_id, notes, date.today())
    print_json({"status": tracking.status, "follow_up_on": tracking.follow_up_on})
    return 0


def dismiss(ctx: Context, match_id: uuid.UUID) -> int:
    """Hide a match the user does not want (it can be restored in the app)."""
    dashboard.set_status(ctx.db, ctx.user.id, match_id, MatchStatus.DISMISSED)
    print_json({"dismissed": match_id})
    return 0


def match_summary(match: JobMatch, description_length: int) -> dict[str, Any]:
    offer = match.offer
    summary: dict[str, Any] = {
        "match_id": match.id,
        "score": match.score,
        "title": offer.title,
        "company": offer.company,
        "location": offer.location,
        "work_mode": offer.work_mode,
        "language": offer.language,
        "board": offer.source,
        "url": offer.url,
        "published_at": offer.published_at,
        "matched_skills": match.matched_skills,
    }
    if description_length:
        summary["description"] = offer.description[:description_length]
    return summary
