"""The PDFs hold real, extractable text: what applicant tracking systems need."""

from datetime import date
from io import BytesIO

from pypdf import PdfReader

from app.schemas.application import ApplicationContent, ApplicationLanguage, Contact
from app.services.applications.pdf.cv import render_cv
from app.services.applications.pdf.letter import render_cover_letter
from tests.fakes import make_generated_application


def make_content(**changes: object) -> ApplicationContent:
    generated = make_generated_application()
    fields = {
        "language": ApplicationLanguage.EN,
        "contact": Contact(full_name="Alice Martin", email="alice@mail.com", city="Brussels"),
        "cv": generated.cv,
        "cover_letter": generated.cover_letter,
    }
    return ApplicationContent.model_validate(fields | changes)


def text_of(pdf: bytes) -> str:
    return "\n".join(page.extract_text() for page in PdfReader(BytesIO(pdf)).pages)


def test_the_cv_shows_the_header_sections_and_bullets() -> None:
    text = text_of(render_cv(make_content()))

    assert "Alice Martin" in text
    assert "EXPERIENCE" in text
    assert "Built the billing API used by 200 customers." in text
    assert "Jan 2022 – Present" in text


def test_the_cv_uses_the_document_language() -> None:
    text = text_of(render_cv(make_content(language=ApplicationLanguage.FR)))

    assert "EXPÉRIENCE PROFESSIONNELLE" in text
    assert "COMPÉTENCES" in text


def test_markup_characters_are_shown_as_text() -> None:
    cv = make_generated_application().cv.model_copy(update={"summary": "Python <3 & R&D"})

    text = text_of(render_cv(make_content(cv=cv)))

    assert "Python <3 & R&D" in text


def test_the_letter_shows_the_company_date_subject_and_signature() -> None:
    pdf = render_cover_letter(make_content(), company="Acme", day=date(2026, 11, 26))

    text = text_of(pdf)
    assert "Acme" in text
    assert "Brussels, 26 November 2026" in text
    assert "Subject: Application for the Python developer position" in text
    assert text.rstrip().endswith("Alice Martin")
