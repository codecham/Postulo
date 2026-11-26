"""The application folder: the PDFs to upload, and a copy of the offer to keep.

Offers disappear from job boards once filled: the copy is what the user rereads
before an interview.
"""

import re
import uuid
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from sqlalchemy.orm import Session

from app.models import Application, JobOffer
from app.schemas.application import ApplicationContent, ApplicationLanguage
from app.services.applications import applications
from app.services.applications.pdf.cv import render_cv
from app.services.applications.pdf.letter import render_cover_letter

LETTER_LABELS = {
    ApplicationLanguage.FR: "Lettre de motivation",
    ApplicationLanguage.EN: "Cover letter",
}
# Characters that are not safe in a file name on macOS, Windows or Linux
UNSAFE_CHARACTERS = re.compile(r'[\\/:*?"<>|\x00-\x1f]+')
MAX_NAME_LENGTH = 80


@dataclass(frozen=True)
class Dossier:
    folder: Path
    cv: Path
    cover_letter: Path
    offer: Path


def write_dossier(
    db: Session, user_id: uuid.UUID, match_id: uuid.UUID, root: Path, day: date
) -> Dossier:
    """(Re)write the folder of the match's current application, from its reviewed content."""
    application = applications.get_latest_application(db, user_id, match_id)
    offer = applications.match_of(db, application).offer
    content = ApplicationContent.model_validate(application.content)
    folder = root / folder_name(offer, application, day)
    folder.mkdir(parents=True, exist_ok=True)
    dossier = Dossier(
        folder=folder,
        cv=folder / pdf_name("CV", content),
        cover_letter=folder / pdf_name(LETTER_LABELS[content.language], content),
        offer=folder / "offer.md",
    )
    dossier.cv.write_bytes(render_cv(content))
    dossier.cover_letter.write_bytes(render_cover_letter(content, offer.company, day))
    dossier.offer.write_text(offer_markdown(offer))
    return dossier


def folder_name(offer: JobOffer, application: Application, day: date) -> str:
    """'2026-11-26 Acme - Backend developer': sorted by date in a file browser.

    The date is the day the application was written, so a rewrite keeps its folder.
    """
    written_on = application.created_at.date() if application.created_at else day
    return safe_name(f"{written_on.isoformat()} {offer.company or '?'} - {offer.title}")


def pdf_name(label: str, content: ApplicationContent) -> str:
    """'CV Alice Martin.pdf': what the recruiter sees in their downloads."""
    return f"{safe_name(' '.join(filter(None, [label, content.contact.full_name])))}.pdf"


def safe_name(text: str) -> str:
    cleaned = " ".join(UNSAFE_CHARACTERS.sub(" ", text).split())
    return cleaned[:MAX_NAME_LENGTH].rstrip(" .")


def offer_markdown(offer: JobOffer) -> str:
    facts = [
        ("Company", offer.company),
        ("Location", offer.location),
        ("Work mode", offer.work_mode),
        ("Salary", offer.salary),
        ("Job board", offer.source),
        ("Link", offer.url),
        ("Published", offer.published_at.date().isoformat() if offer.published_at else None),
    ]
    lines = [f"# {offer.title}", ""]
    lines += [f"- **{label}**: {value}" for label, value in facts if value]
    return "\n".join([*lines, "", offer.description, ""])
