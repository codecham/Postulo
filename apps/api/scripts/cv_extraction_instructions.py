"""Print the CV extraction rules and JSON schema, for the /import-cv Claude Code command.

Usage (from apps/api): uv run python -m scripts.cv_extraction_instructions
Same rules and schema as the API extraction, so both ways give the same result.
"""

import json

from app.services.cv_import.extraction import CvExtraction
from app.services.cv_import.prompt import SYSTEM_PROMPT

print(SYSTEM_PROMPT)
print("Answer with one JSON object that matches this JSON schema:\n")
print(json.dumps(CvExtraction.model_json_schema(), indent=2))
