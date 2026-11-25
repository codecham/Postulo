"""ClaudeApplicationWriter with a fake Anthropic client: checks how answers are handled."""

from types import SimpleNamespace
from typing import Any, cast

import anthropic
import httpx2
import pytest

from app.models import Profile
from app.services.applications.claude_writer import ClaudeApplicationWriter
from app.services.applications.context import ApplicationContext, build_context
from app.services.applications.errors import GenerationFailedError
from tests.fakes import make_generated_application
from tests.services.cv_import.test_claude_extractor import FakeAnthropicClient
from tests.services.job_search.helpers import make_offer


def make_response(stop_reason: str = "end_turn", parsed: Any = "default") -> SimpleNamespace:
    return SimpleNamespace(
        stop_reason=stop_reason,
        parsed_output=make_generated_application() if parsed == "default" else parsed,
        model="claude-test",
        usage=SimpleNamespace(input_tokens=4000, output_tokens=1200),
    )


def make_writer(client: FakeAnthropicClient) -> ClaudeApplicationWriter:
    return ClaudeApplicationWriter(cast(anthropic.Anthropic, client), model="claude-test")


def make_context() -> ApplicationContext:
    return build_context(Profile(skills=["Python"], languages=[]), [], [], make_offer())


def test_a_complete_answer_returns_the_application_and_the_usage() -> None:
    client = FakeAnthropicClient(response=make_response())

    result = make_writer(client).write(make_context())

    assert result.application.cv.headline == "Python backend developer"
    assert (result.model, result.input_tokens, result.output_tokens) == ("claude-test", 4000, 1200)


def test_the_offer_and_the_profile_are_sent_in_the_message() -> None:
    client = FakeAnthropicClient(response=make_response())

    make_writer(client).write(make_context())

    message = client.requests[0]["messages"][0]["content"]
    assert "Python developer" in message
    assert "Document language: en" in message


@pytest.mark.parametrize(
    "response",
    [make_response(stop_reason="refusal", parsed=None), make_response(stop_reason="max_tokens")],
)
def test_an_unusable_answer_raises(response: SimpleNamespace) -> None:
    client = FakeAnthropicClient(response=response)

    with pytest.raises(GenerationFailedError):
        make_writer(client).write(make_context())


def test_an_api_error_raises() -> None:
    request = httpx2.Request("POST", "https://api.anthropic.com/v1/messages")
    client = FakeAnthropicClient(error=anthropic.APIConnectionError(request=request))

    with pytest.raises(GenerationFailedError):
        make_writer(client).write(make_context())
