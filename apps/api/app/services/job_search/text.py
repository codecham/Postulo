"""Small text helpers for job offers: plain text, language and work mode."""

import re
from html.parser import HTMLParser

# Tags after which a line break keeps the text readable
_BLOCK_TAGS = {"p", "br", "li", "div", "h1", "h2", "h3", "h4", "h5", "h6", "tr", "ul", "ol"}


def _words(text: str) -> frozenset[str]:
    return frozenset(text.split())


# Frequent short words of each language: enough to tell them apart in a job offer
_STOPWORDS: dict[str, frozenset[str]] = {
    "fr": _words("le la les des et est une pour dans avec vous nous sur du au aux qui"),
    "en": _words("the and is are for with you we our to of in on a an will your"),
    "nl": _words("de het een en van voor met je jij wij ons is zijn op te bij"),
    "de": _words("der die das und ist für mit sie wir unser zu von im ein eine auf"),
    "es": _words("el los las y es para con usted nosotros en un una por del que"),
}
# Below this many stopwords, the text is too short to guess its language
_MIN_STOPWORDS = 5

_REMOTE = re.compile(r"\b(remote|full[- ]?remote|t[ée]l[ée]travail|thuiswerk)\b", re.IGNORECASE)
_HYBRID = re.compile(r"\b(hybrid|hybride)\b", re.IGNORECASE)
_WORD = re.compile(r"[^\W\d_]+")


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in _BLOCK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def html_to_text(html: str) -> str:
    """The visible text of an HTML fragment, with simple line breaks."""
    extractor = _TextExtractor()
    extractor.feed(html)
    extractor.close()
    lines = (" ".join(line.split()) for line in "".join(extractor.parts).splitlines())
    return "\n".join(line for line in lines if line)


def detect_language(text: str) -> str | None:
    """The ISO 639-1 code of the text's language, or None when unsure."""
    words = [word.casefold() for word in _WORD.findall(text)]
    counts = {
        code: sum(word in stopwords for word in words) for code, stopwords in _STOPWORDS.items()
    }
    language, count = max(counts.items(), key=lambda item: item[1])
    return language if count >= _MIN_STOPWORDS else None


def guess_work_mode(text: str) -> str:
    """remote, hybrid or onsite, from the words of an offer that does not say it clearly."""
    if _HYBRID.search(text):
        return "hybrid"
    if _REMOTE.search(text):
        return "remote"
    return "onsite"


def truncate(text: str | None, max_length: int) -> str | None:
    if text is None or len(text) <= max_length:
        return text
    return text[: max_length - 1] + "…"
