"""Entry point: parse the command, open the database, run the command."""

import argparse
import sys
import uuid
from pathlib import Path

from pydantic import ValidationError

from app.core.database import SessionLocal
from app.services import users
from app.services.applications.errors import ApplicationError
from app.services.hunt.search import HuntSearchTimeoutError
from app.services.job_search.errors import MatchNotFoundError, ProfileIncompleteError
from app.services.tracking import TrackingError
from scripts.hunt import commands
from scripts.hunt.settings import load_settings, settings_path

# Expected problems: a short message for Claude instead of a traceback
KNOWN_ERRORS = (
    ValidationError,
    MatchNotFoundError,
    ProfileIncompleteError,
    ApplicationError,
    TrackingError,
    HuntSearchTimeoutError,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="scripts.hunt", description="The daily job hunt.")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("brief", help="criteria and settings: what to look for, and where")

    search = sub.add_parser("search", help="save the browser findings, then run the search")
    search.add_argument("--findings", type=Path, help="JSON file of the offers read in Chrome")
    search.add_argument("--timeout-minutes", type=int, default=15)

    candidates = sub.add_parser("candidates", help="best new matches with no application")
    candidates.add_argument("--limit", type=int, default=20)

    save = sub.add_parser("save-application", help="save an application and write its dossier")
    save.add_argument("match_id", type=uuid.UUID)
    save.add_argument("file", type=Path)

    ready = sub.add_parser("ready", help="applications waiting for the user's go")
    ready.add_argument("--count", action="store_true", help="print only how many")

    for name, help_text in [
        ("dossier", "rewrite the PDFs of a match from its reviewed application"),
        ("dismiss", "hide a match the user does not want"),
    ]:
        sub.add_parser(name, help=help_text).add_argument("match_id", type=uuid.UUID)

    sent = sub.add_parser("mark-sent", help="record an application as sent")
    sent.add_argument("match_id", type=uuid.UUID)
    sent.add_argument("--notes", help="how it was sent, e.g. 'Greenhouse form'")
    return parser


def dispatch(args: argparse.Namespace, ctx: commands.Context) -> int:
    match args.command:
        case "brief":
            return commands.brief(ctx)
        case "search":
            return commands.run_search(ctx, args.findings, args.timeout_minutes)
        case "candidates":
            return commands.candidates(ctx, args.limit)
        case "save-application":
            return commands.save_application(ctx, args.match_id, args.file)
        case "ready":
            return commands.ready(ctx, args.count)
        case "dossier":
            return commands.write_dossier(ctx, args.match_id)
        case "dismiss":
            return commands.dismiss(ctx, args.match_id)
        case "mark-sent":
            return commands.mark_sent(ctx, args.match_id, args.notes)
    raise AssertionError(args.command)


def main() -> int:
    args = build_parser().parse_args()
    path = settings_path()
    if not path.exists():
        print(f"No hunt settings at {path}: run `make hunt-install` first.", file=sys.stderr)
        return 1
    settings = load_settings(path)
    with SessionLocal() as db:
        user = users.get_user_by_email(db, settings.email)
        if user is None:
            print(f"No Postulo account for {settings.email}.", file=sys.stderr)
            return 1
        try:
            return dispatch(args, commands.Context(db, user, settings))
        except KNOWN_ERRORS as error:
            print(f"{type(error).__name__}: {error}", file=sys.stderr)
            return 1


if __name__ == "__main__":
    sys.exit(main())
