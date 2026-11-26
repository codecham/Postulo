"""Logging setup: readable lines in development, one JSON object per line in production.

JSON logs can be searched and filtered by any log platform (Grafana Loki, Better Stack,
a cloud provider's console...) without writing a parser.
"""

import json
import logging
from contextvars import ContextVar
from datetime import UTC, datetime

from app.core.config import Settings

# Id of the HTTP request being handled, added to every log line written during it
request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)

# Attributes every LogRecord has: anything else was passed with `extra=` and is logged
# (color_message is Uvicorn's copy of the message with terminal colors)
_STANDARD_ATTRIBUTES = frozenset(vars(logging.makeLogRecord({}))) | {
    "message",
    "asctime",
    "color_message",
}
_TEXT_FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"


class JsonFormatter(logging.Formatter):
    """Formats a record as a single-line JSON object."""

    def format(self, record: logging.LogRecord) -> str:
        entry: dict[str, object] = {
            "time": datetime.fromtimestamp(record.created, UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if request_id := request_id_var.get():
            entry["request_id"] = request_id
        entry.update(_extra_fields(record))
        if record.exc_info:
            entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(entry, default=str)


def _extra_fields(record: logging.LogRecord) -> dict[str, object]:
    return {
        key: value
        for key, value in vars(record).items()
        if key not in _STANDARD_ATTRIBUTES and not key.startswith("_")
    }


def configure_logging(settings: Settings) -> None:
    """Send every log (the app's and Uvicorn's) to stdout in the environment's format."""
    handler = logging.StreamHandler()
    formatter = JsonFormatter() if settings.is_production else logging.Formatter(_TEXT_FORMAT)
    handler.setFormatter(formatter)
    logging.basicConfig(level=settings.log_level, handlers=[handler], force=True)
    # Uvicorn installs its own handlers: route its logs through ours instead
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        uvicorn_logger = logging.getLogger(name)
        uvicorn_logger.handlers.clear()
        uvicorn_logger.propagate = True
    # The request logging middleware writes richer access logs (duration, request id)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
