from app.services.job_search.text import (
    detect_language,
    guess_work_mode,
    html_to_text,
    truncate,
)


def test_html_to_text_keeps_the_text_and_line_breaks() -> None:
    html = "<p>Hello <b>world</b></p><ul><li>Python</li><li>SQL &amp; Docker</li></ul>"

    assert html_to_text(html) == "Hello world\nPython\nSQL & Docker"


def test_detect_language_recognizes_french_and_english() -> None:
    french = "Nous cherchons un développeur pour notre équipe. Vous travaillerez avec les données."
    english = "We are looking for a developer to join our team. You will work with the data."

    assert detect_language(french) == "fr"
    assert detect_language(english) == "en"


def test_detect_language_gives_up_on_a_short_text() -> None:
    assert detect_language("Python developer") is None


def test_guess_work_mode_reads_the_offer_words() -> None:
    assert guess_work_mode("Poste hybride à Bruxelles") == "hybrid"
    assert guess_work_mode("Full remote, télétravail possible") == "remote"
    assert guess_work_mode("Bureau à Liège") == "onsite"


def test_truncate_cuts_long_texts_only() -> None:
    assert truncate("abcdef", 4) == "abc…"
    assert truncate("abc", 4) == "abc"
    assert truncate(None, 4) is None
