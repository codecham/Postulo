"""Check that a JSON file is a valid application, for the /tailor-application command.

Usage (from apps/api): uv run python -m scripts.check_application /path/to/application.json
Prints the errors and exits with status 1 when the JSON does not match the schema.
"""

import sys
from pathlib import Path

from pydantic import ValidationError

from app.schemas.application import GeneratedApplication

try:
    application = GeneratedApplication.model_validate_json(Path(sys.argv[1]).read_text())
except ValidationError as error:
    print(error)
    sys.exit(1)
words = sum(len(text.split()) for text in application.cover_letter.paragraphs)
print(
    f"Valid application: {len(application.cv.experiences)} experience(s), "
    f"cover letter of {words} words."
)
