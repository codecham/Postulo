from app.services.job_search.scoring import find_skills, score_offer


def test_score_grows_with_the_similarity() -> None:
    assert score_offer(0.3, 0, 0) == 0
    assert score_offer(0.6, 0, 0) == 50
    assert score_offer(0.9, 0, 0) == 100


def test_skills_found_in_the_offer_raise_the_score() -> None:
    without_skills = score_offer(0.8, matched_skills=0, total_skills=4)
    with_skills = score_offer(0.8, matched_skills=4, total_skills=4)

    assert (without_skills, with_skills) == (75, 100)


def test_find_skills_matches_whole_words_ignoring_case() -> None:
    text = "Good knowledge of PYTHON, C++ and .NET"

    found = find_skills(text, ["Python", "Go", "C++", ".NET", "Java"])

    assert found == ["Python", "C++", ".NET"]
