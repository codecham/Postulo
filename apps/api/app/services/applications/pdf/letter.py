"""The cover letter as a PDF: sender, company, date, subject, then the letter itself."""

from datetime import date

from reportlab.platypus import Flowable

from app.schemas.application import ApplicationContent, Contact
from app.services.applications.pdf.document import (
    BODY,
    LETTER_PARAGRAPH,
    MUTED,
    build_pdf,
    joined,
    paragraph,
    space,
)
from app.services.applications.pdf.labels import LABELS, format_day


def render_cover_letter(content: ApplicationContent, company: str | None, day: date) -> bytes:
    labels = LABELS[content.language]
    letter = content.cover_letter
    flowables = [
        *_sender(content.contact),
        space(8),
        *([paragraph(company, BODY)] if company else []),
        paragraph(joined(content.contact.city, format_day(day, labels), separator=", "), MUTED),
        space(8),
        paragraph(f"{labels.subject} {letter.subject}", BODY),
        space(6),
        paragraph(letter.greeting, LETTER_PARAGRAPH),
        *(paragraph(text, LETTER_PARAGRAPH) for text in letter.paragraphs),
        paragraph(letter.closing, LETTER_PARAGRAPH),
        *([paragraph(content.contact.full_name, BODY)] if content.contact.full_name else []),
    ]
    name = content.contact.full_name or ""
    return build_pdf(flowables, title=letter.subject, author=name)


def _sender(contact: Contact) -> list[Flowable]:
    lines = [contact.full_name, contact.email, contact.phone, contact.city, *contact.links]
    return [paragraph(line, BODY) for line in lines if line]
