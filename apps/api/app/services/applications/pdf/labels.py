"""The fixed words of the documents, and how dates are written, in each language."""

from dataclasses import dataclass
from datetime import date

from app.schemas.application import ApplicationLanguage


@dataclass(frozen=True)
class Labels:
    summary: str
    experience: str
    education: str
    skills: str
    languages: str
    present: str
    subject: str
    months: tuple[str, ...]  # short month names, January first
    long_months: tuple[str, ...]


LABELS: dict[ApplicationLanguage, Labels] = {
    ApplicationLanguage.EN: Labels(
        summary="Profile",
        experience="Experience",
        education="Education",
        skills="Skills",
        languages="Languages",
        present="Present",
        subject="Subject:",
        months=("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"),
        long_months=(
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ),
    ),
    ApplicationLanguage.FR: Labels(
        summary="Profil",
        experience="Expérience professionnelle",
        education="Formation",
        skills="Compétences",
        languages="Langues",
        present="Aujourd'hui",
        subject="Objet :",
        months=(
            "janv.",
            "févr.",
            "mars",
            "avr.",
            "mai",
            "juin",
            "juil.",
            "août",
            "sept.",
            "oct.",
            "nov.",
            "déc.",
        ),
        long_months=(
            "janvier",
            "février",
            "mars",
            "avril",
            "mai",
            "juin",
            "juillet",
            "août",
            "septembre",
            "octobre",
            "novembre",
            "décembre",
        ),
    ),
}


def format_month(month: str | None, labels: Labels) -> str:
    """'2024-06' -> 'Jun 2024' (or 'juin 2024'). Empty when unknown."""
    if not month:
        return ""
    year, number = month.split("-")
    return f"{labels.months[int(number) - 1]} {year}"


def format_period(
    start_month: str | None, end_month: str | None, labels: Labels, *, ongoing: bool
) -> str:
    """'Jan 2022 – Jun 2024', 'Jan 2022 – Present', or just one end when the other is unknown."""
    start = format_month(start_month, labels)
    end = format_month(end_month, labels) or (labels.present if ongoing and start else "")
    return " – ".join(part for part in (start, end) if part)


def format_day(day: date, labels: Labels) -> str:
    """The date of a letter: '26 November 2026' or '26 novembre 2026'."""
    return f"{day.day} {labels.long_months[day.month - 1]} {day.year}"
