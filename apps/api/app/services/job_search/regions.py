"""Where a remote job can be done from, read from the free text the job boards give.

Remote offers rarely have a country: they say "Anywhere", "Europe", "USA only"...
"""

import re
from collections.abc import Iterable

WORLDWIDE_WORDS = ("anywhere", "worldwide", "world", "global", "international")
EUROPE_WORDS = ("europe", "european", "emea", "eu", "eea", "cet", "cest")

# Names job boards use for each country, in English and in the local languages
COUNTRY_NAMES: dict[str, tuple[str, ...]] = {
    "AT": ("austria", "österreich"),
    "BE": ("belgium", "belgique", "belgië", "belgie", "belgien", "benelux"),
    "BG": ("bulgaria",),
    "CH": ("switzerland", "suisse", "schweiz"),
    "CY": ("cyprus",),
    "CZ": ("czechia", "czech republic"),
    "DE": ("germany", "deutschland", "dach"),
    "DK": ("denmark",),
    "EE": ("estonia",),
    "ES": ("spain", "españa"),
    "FI": ("finland",),
    "FR": ("france",),
    "GB": ("united kingdom", "uk", "england", "great britain"),
    "GR": ("greece",),
    "HR": ("croatia",),
    "HU": ("hungary",),
    "IE": ("ireland",),
    "IT": ("italy", "italia"),
    "LT": ("lithuania",),
    "LU": ("luxembourg", "benelux"),
    "LV": ("latvia",),
    "MT": ("malta",),
    "NL": ("netherlands", "nederland", "holland", "benelux"),
    "NO": ("norway",),
    "PL": ("poland", "polska"),
    "PT": ("portugal",),
    "RO": ("romania",),
    "SE": ("sweden",),
    "SI": ("slovenia",),
    "SK": ("slovakia",),
    "CA": ("canada",),
    "US": ("united states", "usa", "us"),
}
EUROPEAN_COUNTRIES = frozenset(COUNTRY_NAMES) - {"CA", "US"}


def mentions_any(text: str, words: Iterable[str]) -> bool:
    """True when the text contains one of the words as a whole word, ignoring case."""
    return any(re.search(rf"\b{re.escape(word)}\b", text, re.IGNORECASE) for word in words)


def country_names(countries: Iterable[str]) -> list[str]:
    return [name for country in countries for name in COUNTRY_NAMES.get(country, ())]


def remote_region_accepts(
    region: str | None, countries: tuple[str, ...], open_to_remote_abroad: bool
) -> bool:
    """Can someone living in one of these countries take this remote job?

    Without `open_to_remote_abroad`, the region must name one of the countries.
    """
    if not region or mentions_any(region, country_names(countries)):
        return True
    if not open_to_remote_abroad:
        return False
    if mentions_any(region, WORLDWIDE_WORDS):
        return True
    lives_in_europe = not countries or any(c in EUROPEAN_COUNTRIES for c in countries)
    return lives_in_europe and mentions_any(region, EUROPE_WORDS)
