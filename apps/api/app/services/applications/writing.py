"""The interface of anything that writes an application, and what it returns."""

from dataclasses import dataclass
from typing import Protocol

from app.schemas.application import GeneratedApplication
from app.services.applications.context import ApplicationContext

# Application written in the user's own Claude Code session (/tailor-application)
CLAUDE_CODE_SOURCE = "claude-code"


@dataclass(frozen=True)
class WritingResult:
    application: GeneratedApplication
    model: str  # who wrote it: an API model id, or CLAUDE_CODE_SOURCE
    input_tokens: int | None = None  # None when the API was not called
    output_tokens: int | None = None


class ApplicationWriter(Protocol):
    """Writes the CV and the cover letter. Claude in production, a fake in the tests."""

    def write(self, context: ApplicationContext) -> WritingResult:
        """Raise GenerationFailedError when no usable answer can be produced."""
        ...
