"""ApplicationWriter backed by the Claude API."""

import anthropic
from anthropic.types.parsed_message import ParsedMessage
from pydantic import ValidationError

from app.schemas.application import GeneratedApplication
from app.services.applications.context import ApplicationContext
from app.services.applications.errors import GenerationFailedError
from app.services.applications.prompt import SYSTEM_PROMPT, USER_PROMPT
from app.services.applications.writing import WritingResult

# A CV and a one-page letter fit well within this
MAX_OUTPUT_TOKENS = 16000


class ClaudeApplicationWriter:
    def __init__(self, client: anthropic.Anthropic, model: str) -> None:
        self._client = client
        self._model = model

    def write(self, context: ApplicationContext) -> WritingResult:
        response = self._call_claude(context)
        if response.stop_reason != "end_turn" or response.parsed_output is None:
            # "refusal": the model declined; "max_tokens": the JSON was cut off
            raise GenerationFailedError(f"Unusable answer (stop reason: {response.stop_reason})")
        return WritingResult(
            application=response.parsed_output,
            model=response.model,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
        )

    def _call_claude(self, context: ApplicationContext) -> ParsedMessage[GeneratedApplication]:
        try:
            return self._client.messages.parse(
                model=self._model,
                max_tokens=MAX_OUTPUT_TOKENS,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": f"{context.as_prompt()}\n\n{USER_PROMPT}"}],
                output_format=GeneratedApplication,
            )
        except (anthropic.APIStatusError, anthropic.APIConnectionError) as error:
            raise GenerationFailedError("The Claude API call failed") from error
        except ValidationError as error:
            raise GenerationFailedError("The answer does not match the schema") from error


def build_claude_writer(api_key: str, model: str) -> ClaudeApplicationWriter:
    # Retries cover rate limits and server errors; the timeout bounds a hanging call
    client = anthropic.Anthropic(api_key=api_key, timeout=120.0, max_retries=2)
    return ClaudeApplicationWriter(client, model)
