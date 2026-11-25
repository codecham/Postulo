"""Check that a JSON file is a valid CV extraction, for the /import-cv Claude Code command.

Usage (from apps/api): uv run python -m scripts.check_cv_extraction /path/to/extraction.json
Prints the errors and exits with status 1 when the JSON does not match the schema.
"""

import sys
from pathlib import Path

from pydantic import ValidationError

from app.services.cv_import.extraction import CvExtraction

try:
    extraction = CvExtraction.model_validate_json(Path(sys.argv[1]).read_text())
except ValidationError as error:
    print(error)
    sys.exit(1)
print(f"Valid extraction: {len(extraction.experiences)} experience(s).")
