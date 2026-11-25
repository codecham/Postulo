from app.services.job_search.regions import remote_region_accepts


def test_an_unknown_region_is_accepted() -> None:
    assert remote_region_accepts(None, ("BE",), open_to_remote_abroad=False)


def test_a_region_naming_the_users_country_is_accepted() -> None:
    assert remote_region_accepts("Belgium, Netherlands", ("BE",), open_to_remote_abroad=False)


def test_abroad_regions_need_the_user_to_be_open_to_them() -> None:
    assert not remote_region_accepts("Worldwide", ("BE",), open_to_remote_abroad=False)
    assert remote_region_accepts("Worldwide", ("BE",), open_to_remote_abroad=True)


def test_europe_is_accepted_for_someone_living_in_europe() -> None:
    assert remote_region_accepts("Europe (CET ± 2h)", ("BE",), open_to_remote_abroad=True)
    assert not remote_region_accepts("EMEA", ("US",), open_to_remote_abroad=True)


def test_a_region_reserved_to_other_countries_is_rejected() -> None:
    assert not remote_region_accepts("USA only", ("BE",), open_to_remote_abroad=True)
    assert not remote_region_accepts("Americas, LATAM", ("BE",), open_to_remote_abroad=True)


def test_country_codes_only_match_as_whole_words() -> None:
    # "us" is the United States, but not inside "business"
    assert not remote_region_accepts("Business hours", ("US",), open_to_remote_abroad=False)
