"""The tailored CV as a PDF: header, profile, experience, education, skills, languages."""

from reportlab.platypus import Flowable

from app.schemas.application import ApplicationContent, Contact, CvEducation, CvExperience
from app.services.applications.pdf.document import (
    BODY,
    HEADLINE,
    ITEM_TITLE,
    MUTED,
    NAME,
    bold_and_plain,
    build_pdf,
    bullet,
    joined,
    paragraph,
    section_title,
    space,
)
from app.services.applications.pdf.labels import LABELS, Labels, format_period


def render_cv(content: ApplicationContent) -> bytes:
    labels = LABELS[content.language]
    cv = content.cv
    flowables = [
        *_header(content.contact, cv.headline),
        *section_title(labels.summary),
        paragraph(cv.summary, BODY),
        *_experiences(cv.experiences, labels),
        *_educations(cv.education, labels),
        *_list_section(labels.skills, cv.skills),
        *_list_section(labels.languages, cv.languages),
    ]
    name = content.contact.full_name or ""
    return build_pdf(flowables, title=joined(name, cv.headline, separator=" – "), author=name)


def _header(contact: Contact, headline: str) -> list[Flowable]:
    flowables: list[Flowable] = []
    if contact.full_name:
        flowables.append(paragraph(contact.full_name, NAME))
    flowables.append(paragraph(headline, HEADLINE))
    details = joined(contact.city, contact.email, contact.phone, *contact.links)
    if details:
        flowables.append(paragraph(details, MUTED))
    flowables.append(space(2))
    return flowables


def _experiences(experiences: list[CvExperience], labels: Labels) -> list[Flowable]:
    if not experiences:
        return []
    flowables = section_title(labels.experience)
    for experience in experiences:
        flowables.append(bold_and_plain(experience.title, experience.company, ITEM_TITLE))
        period = format_period(experience.start_month, experience.end_month, labels, ongoing=True)
        flowables.append(paragraph(joined(period, experience.location), MUTED))
        flowables.extend(bullet(text) for text in experience.bullets)
    return flowables


def _educations(educations: list[CvEducation], labels: Labels) -> list[Flowable]:
    if not educations:
        return []
    flowables = section_title(labels.education)
    for education in educations:
        flowables.append(_education_title(education))
        period = format_period(education.start_month, education.end_month, labels, ongoing=False)
        flowables.append(paragraph(joined(period, education.location), MUTED))
        if education.details:
            flowables.append(paragraph(education.details, BODY))
    return flowables


def _education_title(education: CvEducation) -> Flowable:
    """'Master, Computer science · ULB', or just the school when there is no degree."""
    degree = joined(education.degree, education.field_of_study, separator=", ")
    if not degree:
        return bold_and_plain(education.school, "", ITEM_TITLE)
    return bold_and_plain(degree, education.school, ITEM_TITLE)


def _list_section(title: str, items: list[str]) -> list[Flowable]:
    if not items:
        return []
    return [*section_title(title), paragraph(" · ".join(items), BODY)]
