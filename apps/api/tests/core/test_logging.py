import json
import logging

from app.core.logging import JsonFormatter, request_id_var


def make_record(**extra: object) -> logging.LogRecord:
    record = logging.makeLogRecord({"name": "app.test", "levelname": "INFO", "msg": "hello %s"})
    record.args = ("world",)
    record.__dict__.update(extra)
    return record


def test_json_logs_hold_the_message_and_the_extra_fields() -> None:
    line = JsonFormatter().format(make_record(status=200))

    entry = json.loads(line)

    assert entry["message"] == "hello world"
    assert entry["level"] == "INFO"
    assert entry["logger"] == "app.test"
    assert entry["status"] == 200


def test_json_logs_hold_the_current_request_id() -> None:
    token = request_id_var.set("req-1")
    try:
        entry = json.loads(JsonFormatter().format(make_record()))
    finally:
        request_id_var.reset(token)

    assert entry["request_id"] == "req-1"
