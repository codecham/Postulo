import logging
from collections.abc import Iterator

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from app.core.middleware import (
    BodySizeLimitMiddleware,
    RequestLoggingMiddleware,
    SecurityHeadersMiddleware,
)

MAX_BYTES = 10


def make_client() -> TestClient:
    """A tiny app wrapped in the middlewares, to test them without the real routes."""
    app = FastAPI()

    @app.post("/echo")
    async def echo(request: Request) -> dict[str, int]:
        return {"size": len(await request.body())}

    app.add_middleware(SecurityHeadersMiddleware, headers={"X-Frame-Options": "DENY"})
    app.add_middleware(BodySizeLimitMiddleware, max_bytes=MAX_BYTES)
    app.add_middleware(RequestLoggingMiddleware)
    return TestClient(app)


def chunks(data: bytes) -> Iterator[bytes]:
    """A body sent without Content-Length (chunked), one byte at a time."""
    for byte in data:
        yield bytes([byte])


def test_a_body_within_the_limit_is_accepted() -> None:
    response = make_client().post("/echo", content=b"x" * MAX_BYTES)

    assert response.status_code == 200
    assert response.json() == {"size": MAX_BYTES}


def test_a_declared_length_over_the_limit_is_refused() -> None:
    response = make_client().post("/echo", content=b"x" * (MAX_BYTES + 1))

    assert response.status_code == 413


def test_a_chunked_body_over_the_limit_is_refused() -> None:
    response = make_client().post("/echo", content=chunks(b"x" * (MAX_BYTES + 5)))

    assert response.status_code == 413


def test_security_headers_are_added() -> None:
    response = make_client().post("/echo")

    assert response.headers["X-Frame-Options"] == "DENY"


def test_each_response_gets_a_request_id() -> None:
    client = make_client()

    first = client.post("/echo").headers["X-Request-ID"]
    second = client.post("/echo").headers["X-Request-ID"]

    assert first and second and first != second


def test_a_valid_request_id_from_a_proxy_is_kept() -> None:
    response = make_client().post("/echo", headers={"X-Request-ID": "abc-123"})

    assert response.headers["X-Request-ID"] == "abc-123"


def test_an_unsafe_request_id_is_replaced() -> None:
    response = make_client().post("/echo", headers={"X-Request-ID": "bad id\nforged log"})

    assert response.headers["X-Request-ID"] != "bad id\nforged log"


def test_each_request_is_logged_with_its_status(caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.INFO, logger="app.requests"):
        make_client().post("/echo")

    (record,) = [record for record in caplog.records if record.name == "app.requests"]
    assert record.getMessage().startswith("POST /echo 200")
