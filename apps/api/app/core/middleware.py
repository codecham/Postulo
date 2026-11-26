"""ASGI middlewares: request size limit, security headers and access logs.

They are plain ASGI classes rather than Starlette's BaseHTTPMiddleware: they stream
the request and response untouched, and work the same for every kind of response.
"""

import logging
import re
import time
import uuid

from starlette.datastructures import MutableHeaders
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core.logging import request_id_var

logger = logging.getLogger("app.requests")

REQUEST_ID_HEADER = "X-Request-ID"
# A request id sent by a proxy is reused only when it looks like an id (no log injection)
_VALID_REQUEST_ID = re.compile(r"^[A-Za-z0-9._-]{1,64}$")


REQUEST_TOO_LARGE = "Request body too large"


class RequestTooLargeError(HTTPException):
    """The body grew past the limit while it was being read.

    An HTTPException, so FastAPI answers 413 even when it is raised while a route
    parses its body (FastAPI turns other parsing errors into a 400).
    """

    def __init__(self) -> None:
        super().__init__(status_code=413, detail=REQUEST_TOO_LARGE)


class BodySizeLimitMiddleware:
    """Answer 413 to a request whose body is larger than `max_bytes`.

    Checks the Content-Length header first, then counts the bytes actually received,
    so a chunked request without a length cannot get around the limit.
    """

    def __init__(self, app: ASGIApp, max_bytes: int) -> None:
        self.app = app
        self.max_bytes = max_bytes

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        if self._declared_length(scope) > self.max_bytes:
            await self._reject(scope, receive, send)
            return
        received = 0
        response_started = False

        async def tracking_send(message: Message) -> None:
            nonlocal response_started
            response_started = response_started or message["type"] == "http.response.start"
            await send(message)

        async def counting_receive() -> Message:
            nonlocal received
            message = await receive()
            received += len(message.get("body", b""))
            if received > self.max_bytes:
                raise RequestTooLargeError
            return message

        try:
            await self.app(scope, counting_receive, tracking_send)
        except RequestTooLargeError:
            if response_started:
                raise
            await self._reject(scope, receive, send)

    @staticmethod
    def _declared_length(scope: Scope) -> int:
        for name, value in scope["headers"]:
            if name == b"content-length":
                return int(value) if value.isdigit() else 0
        return 0

    @staticmethod
    async def _reject(scope: Scope, receive: Receive, send: Send) -> None:
        response = JSONResponse({"detail": REQUEST_TOO_LARGE}, status_code=413)
        await response(scope, receive, send)


# Headers for an API that only serves JSON (and PDF downloads) and is never framed
API_SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Cross-Origin-Resource-Policy": "same-origin",
}
# Blocks every script, style and frame: only valid while the HTML docs are turned off
API_CONTENT_SECURITY_POLICY = "default-src 'none'; frame-ancestors 'none'"


class SecurityHeadersMiddleware:
    """Add fixed security headers to every HTTP response."""

    def __init__(self, app: ASGIApp, headers: dict[str, str]) -> None:
        self.app = app
        self.headers = headers

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_with_headers(message: Message) -> None:
            if message["type"] == "http.response.start":
                response_headers = MutableHeaders(scope=message)
                for name, value in self.headers.items():
                    response_headers.setdefault(name, value)
            await send(message)

        await self.app(scope, receive, send_with_headers)


class RequestLoggingMiddleware:
    """Log one line per request (method, path, status, duration) with a request id.

    The id comes from the X-Request-ID header when a proxy set one, so a request can be
    followed across services; it is sent back in the response for support requests.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        request_id = _request_id(scope)
        token = request_id_var.set(request_id)
        started = time.perf_counter()
        status_code = 500  # what the client gets if the app crashes before answering

        async def send_with_id(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
                MutableHeaders(scope=message)[REQUEST_ID_HEADER] = request_id
            await send(message)

        try:
            await self.app(scope, receive, send_with_id)
        finally:
            _log_request(scope, status_code, time.perf_counter() - started)
            request_id_var.reset(token)


def _is_successful_health_check(path: str, status_code: int) -> bool:
    return path.startswith("/health") and status_code < 400


def _request_id(scope: Scope) -> str:
    for name, value in scope["headers"]:
        if name == REQUEST_ID_HEADER.lower().encode():
            candidate: str = value.decode("latin-1")
            if _VALID_REQUEST_ID.match(candidate):
                return candidate
    return uuid.uuid4().hex


def _log_request(scope: Scope, status_code: int, duration_seconds: float) -> None:
    if _is_successful_health_check(scope["path"], status_code):
        return  # containers probe it every few seconds: only failures are worth a line
    # The path only: query strings can carry personal data (search filters...)
    logger.log(
        logging.ERROR if status_code >= 500 else logging.INFO,
        "%s %s %s %.0fms",
        scope["method"],
        scope["path"],
        status_code,
        duration_seconds * 1000,
        extra={
            "method": scope["method"],
            "path": scope["path"],
            "status": status_code,
            "duration_ms": round(duration_seconds * 1000, 1),
        },
    )
