"""Shared building blocks of the PDFs: page setup, text styles and safe paragraphs.

Plain, single-column documents with real text and standard fonts: what applicant
tracking systems read best.
"""

from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Flowable, HRFlowable, Paragraph, SimpleDocTemplate, Spacer

MARGIN = 18 * mm
TEXT_COLOR = HexColor("#1f2937")
MUTED_COLOR = HexColor("#4b5563")

BODY = ParagraphStyle("body", fontName="Helvetica", fontSize=10, leading=14, textColor=TEXT_COLOR)
MUTED = ParagraphStyle("muted", parent=BODY, textColor=MUTED_COLOR)
NAME = ParagraphStyle("name", parent=BODY, fontName="Helvetica-Bold", fontSize=20, leading=24)
HEADLINE = ParagraphStyle("headline", parent=BODY, fontSize=12, leading=16)
SECTION = ParagraphStyle(
    "section", parent=BODY, fontName="Helvetica-Bold", fontSize=11, leading=14, spaceBefore=10
)
ITEM_TITLE = ParagraphStyle("item_title", parent=BODY, spaceBefore=6)
BULLET = ParagraphStyle("bullet", parent=BODY, leftIndent=12, bulletIndent=2)
LETTER_PARAGRAPH = ParagraphStyle("letter_paragraph", parent=BODY, leading=15, spaceAfter=9)


def paragraph(text: str, style: ParagraphStyle) -> Paragraph:
    """A paragraph of plain text: reportlab reads markup, so the text is escaped."""
    return Paragraph(escape(text), style)


def bold_and_plain(bold: str, plain: str, style: ParagraphStyle) -> Paragraph:
    """A bold start, then plain text: '**Developer** · Acme' (no plain part: all bold)."""
    rest = f" · {escape(plain)}" if plain else ""
    return Paragraph(f"<b>{escape(bold)}</b>{rest}", style)


def bullet(text: str) -> Paragraph:
    return Paragraph(escape(text), BULLET, bulletText="•")


def section_title(text: str) -> list[Flowable]:
    return [
        paragraph(text.upper(), SECTION),
        HRFlowable(width="100%", thickness=0.6, color=MUTED_COLOR, spaceBefore=1, spaceAfter=3),
    ]


def joined(*parts: str | None, separator: str = " · ") -> str:
    """The non-empty parts, joined: 'Brussels · alice@mail.com'."""
    return separator.join(part for part in parts if part)


def space(height_mm: float) -> Spacer:
    return Spacer(1, height_mm * mm)


def build_pdf(flowables: list[Flowable], *, title: str, author: str) -> bytes:
    """Lay the content out on A4 pages and return the PDF file."""
    output = BytesIO()
    document = SimpleDocTemplate(
        output,
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=MARGIN,
        bottomMargin=MARGIN,
        title=title,
        author=author,
    )
    document.build(flowables)
    return output.getvalue()
