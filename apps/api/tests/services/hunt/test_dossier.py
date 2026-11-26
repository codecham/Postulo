from datetime import date
from pathlib import Path

import pytest
from sqlalchemy.orm import Session

from app.services.applications.errors import ApplicationNotFoundError
from app.services.hunt import dossier
from tests.services.hunt.helpers import write_application
from tests.services.job_search.helpers import add_match, create_user

TODAY = date(2026, 11, 26)


def test_the_dossier_holds_both_pdfs_and_the_offer(db: Session, tmp_path: Path) -> None:
    user = create_user(db, full_name="Alice Martin")
    match = add_match(db, user, company="Acme", title="Python developer", url="https://a.io/1")
    application = write_application(db, user, match)

    written = dossier.write_dossier(db, user.id, match.id, tmp_path, TODAY)

    written_on = application.created_at.date().isoformat()
    assert written.folder == tmp_path / f"{written_on} Acme - Python developer"
    assert written.cv.name == "CV Alice Martin.pdf"
    assert written.cover_letter.name in {
        "Cover letter Alice Martin.pdf",
        "Lettre de motivation Alice Martin.pdf",
    }
    assert written.cv.read_bytes().startswith(b"%PDF")
    assert written.cover_letter.read_bytes().startswith(b"%PDF")
    assert "https://a.io/1" in written.offer.read_text()


def test_rewriting_the_dossier_keeps_its_folder(db: Session, tmp_path: Path) -> None:
    user = create_user(db)
    match = add_match(db, user)
    write_application(db, user, match)
    first = dossier.write_dossier(db, user.id, match.id, tmp_path, TODAY)

    second = dossier.write_dossier(db, user.id, match.id, tmp_path, date(2026, 12, 1))

    assert second.folder == first.folder
    assert len(list(tmp_path.iterdir())) == 1


def test_a_match_without_application_has_no_dossier(db: Session, tmp_path: Path) -> None:
    user = create_user(db)
    match = add_match(db, user)

    with pytest.raises(ApplicationNotFoundError):
        dossier.write_dossier(db, user.id, match.id, tmp_path, TODAY)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Acme/Inc: Backend? dev", "Acme Inc Backend dev"),
        ("  spaced   out.  ", "spaced out"),
        ("x" * 200, "x" * dossier.MAX_NAME_LENGTH),
    ],
)
def test_names_are_safe_for_every_file_system(text: str, expected: str) -> None:
    assert dossier.safe_name(text) == expected
