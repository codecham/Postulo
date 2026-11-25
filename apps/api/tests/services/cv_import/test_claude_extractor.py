"""ClaudeCvExtractor with a fake Anthropic client: checks how answers are handled."""

from types import SimpleNamespace
from typing import Any, cast

import anthropic
import httpx2
import pytest

from app.services.cv_import.claude_extractor import ClaudeCvExtractor
from app.services.cv_import.errors import ExtractionFailedError
from tests.fakes import make_extraction, make_pdf


class FakeAnthropicClient:
    """Mimics `client.messages.parse(...)`: returns `response` or raises `error`."""

    def __init__(self, response: Any = None, error: Exception | None = None) -> None:
        self.requests: list[dict[str, Any]] = []
        self._response = response
        self._error = error
        self.messages = SimpleNamespace(parse=self._parse)

    def _parse(self, **request: Any) -> Any:
        self.requests.append(request)
        if self._error is not None:
            raise self._error
        return self._response


def make_response(stop_reason: str = "end_turn", parsed: Any = "default") -> SimpleNamespace:
    return SimpleNamespace(
        stop_reason=stop_reason,
        parsed_output=make_extraction() if parsed == "default" else parsed,
        model="claude-test",
        usage=SimpleNamespace(input_tokens=1500, output_tokens=300),
    )


def make_extractor(client: FakeAnthropicClient) -> ClaudeCvExtractor:
    return ClaudeCvExtractor(cast(anthropic.Anthropic, client), model="claude-test")


def test_a_complete_answer_returns_the_extraction_and_the_usage() -> None:
    client = FakeAnthropicClient(response=make_response())

    result = make_extractor(client).extract(make_pdf())

    assert result.extraction.full_name == "Alice Martin"
    assert (result.model, result.input_tokens, result.output_tokens) == ("claude-test", 1500, 300)


def test_the_pdf_is_sent_as_a_document() -> None:
    client = FakeAnthropicClient(response=make_response())

    make_extractor(client).extract(make_pdf())

    document = client.requests[0]["messages"][0]["content"][0]
    assert document["type"] == "document"
    assert document["source"]["media_type"] == "application/pdf"


@pytest.mark.parametrize(
    "response",
    [make_response(stop_reason="refusal", parsed=None), make_response(stop_reason="max_tokens")],
)
def test_an_unusable_answer_raises(response: SimpleNamespace) -> None:
    client = FakeAnthropicClient(response=response)

    with pytest.raises(ExtractionFailedError):
        make_extractor(client).extract(make_pdf())


def test_an_api_error_raises() -> None:
    request = httpx2.Request("POST", "https://api.anthropic.com/v1/messages")
    client = FakeAnthropicClient(error=anthropic.APIConnectionError(request=request))

    with pytest.raises(ExtractionFailedError):
        make_extractor(client).extract(make_pdf())
