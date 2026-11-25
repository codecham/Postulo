"""Print what Claude needs to write an application, for the /tailor-application command.

Usage (from apps/api): uv run python -m scripts.application_instructions <match id>
Reads the match's offer and its owner's profile from the database, then prints the same
rules, facts and JSON schema as the API generation, so both ways give the same result.
"""

import json
import sys
import uuid

from sqlalchemy import select

from app.core.database import SessionLocal
from app.models import JobMatch
from app.schemas.application import GeneratedApplication
from app.services.applications.applications import load_context
from app.services.applications.errors import EmptyProfileError
from app.services.applications.prompt import SYSTEM_PROMPT, USER_PROMPT


def main() -> int:
    match_id = uuid.UUID(sys.argv[1])
    with SessionLocal() as db:
        user_id = db.scalar(select(JobMatch.user_id).where(JobMatch.id == match_id))
        if user_id is None:
            print(f"No match with the id {match_id}.", file=sys.stderr)
            return 1
        try:
            context = load_context(db, user_id, match_id)
        except EmptyProfileError:
            print("The profile is empty: fill it in Postulo first.", file=sys.stderr)
            return 1
    print(SYSTEM_PROMPT)
    print(context.as_prompt())
    print(f"\n{USER_PROMPT}")
    print("Answer with one JSON object that matches this JSON schema:\n")
    print(json.dumps(GeneratedApplication.model_json_schema(), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
