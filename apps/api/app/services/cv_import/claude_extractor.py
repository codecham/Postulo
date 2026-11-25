"""CvExtractor backed by the Claude API."""

import base64

import anthropic
from anthropic.types.beta import BetaContentBlockParam
from anthropic.types.beta.parsed_beta_message import ParsedBetaMessage
from pydantic import ValidationError

from app.services.cv_import.errors import ExtractionFailedError
from app.services.cv_import.extraction import CvExtraction, ExtractionResult
from app.services.cv_import.prompt import SYSTEM_PROMPT, USER_PROMPT

# A CV rarely needs more than a few thousand tokens of output
MAX_OUTPUT_TOKENS = 16000
# If the model declines, the API retries on another model in the same call
FALLBACK_BETA = "server-side-fallback-2026-07-01"


class ClaudeCvExtractor:
    def __init__(self, client: anthropic.Anthropic, model: str) -> None:
        self._client = client
        self._model = model

    def extract(self, pdf: bytes) -> ExtractionResult:
        response = self._call_claude(pdf)
        if response.stop_reason != "end_turn" or response.parsed_output is None:
            # "refusal", or "max_tokens": the JSON was cut, so it is unusable
            raise ExtractionFailedError(f"Unusable answer (stop reason: {response.stop_reason})")
        return ExtractionResult(
            extraction=response.parsed_output,
            model=response.model,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
        )

    def _call_claude(self, pdf: bytes) -> ParsedBetaMessage[CvExtraction]:
        try:
            return self._client.beta.messages.parse(
                model=self._model,
                max_tokens=MAX_OUTPUT_TOKENS,
                # Extraction needs little reasoning: low effort is faster and cheaper
                output_config={"effort": "low"},
                betas=[FALLBACK_BETA],
                fallbacks="default",
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": _document_with_instructions(pdf)}],
                output_format=CvExtraction,
            )
        except (anthropic.APIStatusError, anthropic.APIConnectionError) as error:
            raise ExtractionFailedError("The Claude API call failed") from error
        except ValidationError as error:
            raise ExtractionFailedError("The answer does not match the schema") from error


def _document_with_instructions(pdf: bytes) -> list[BetaContentBlockParam]:
    return [
        {
            "type": "document",
            "source": {
                "type": "base64",
                "media_type": "application/pdf",
                "data": base64.standard_b64encode(pdf).decode("ascii"),
            },
        },
        {"type": "text", "text": USER_PROMPT},
    ]


def build_claude_extractor(api_key: str, model: str) -> ClaudeCvExtractor:
    # Retries cover rate limits and server errors; the timeout bounds a hanging call
    client = anthropic.Anthropic(api_key=api_key, timeout=120.0, max_retries=2)
    return ClaudeCvExtractor(client, model)
