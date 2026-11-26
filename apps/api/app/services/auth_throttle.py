"""Brute-force protection for login and sign-up.

- Login: at most N attempts per client IP, and N failed attempts per email, per window.
  The email limit stops a password-guessing attack spread over many IPs; only failures
  count, so a user who types the right password never reaches it.
- Sign-up: at most N accounts created per client IP per window.
"""

from dataclasses import dataclass

from app.core.config import Settings
from app.core.rate_limit import SlidingWindowCounter
from app.services.users import normalize_email


class TooManyAttemptsError(Exception):
    """Raised when a client must wait before trying again."""

    def __init__(self, retry_after_seconds: int) -> None:
        super().__init__(f"Retry in {retry_after_seconds} seconds")
        self.retry_after_seconds = retry_after_seconds


@dataclass(frozen=True)
class AuthThrottle:
    logins_per_ip: SlidingWindowCounter
    failed_logins_per_email: SlidingWindowCounter
    registrations_per_ip: SlidingWindowCounter

    @classmethod
    def from_settings(cls, settings: Settings) -> AuthThrottle:
        window = settings.auth_window_minutes * 60
        return cls(
            logins_per_ip=SlidingWindowCounter(settings.login_attempts_per_ip, window),
            failed_logins_per_email=SlidingWindowCounter(settings.failed_logins_per_email, window),
            registrations_per_ip=SlidingWindowCounter(settings.registrations_per_ip, window),
        )

    def check_login(self, client_ip: str, email: str) -> None:
        """Count a login attempt, or raise TooManyAttemptsError when over a limit."""
        email_key = normalize_email(email)
        if self.logins_per_ip.is_exceeded(client_ip):
            raise self._error(self.logins_per_ip)
        if self.failed_logins_per_email.is_exceeded(email_key):
            raise self._error(self.failed_logins_per_email)
        self.logins_per_ip.record(client_ip)

    def record_failed_login(self, email: str) -> None:
        self.failed_logins_per_email.record(normalize_email(email))

    def check_registration(self, client_ip: str) -> None:
        """Count a sign-up attempt, or raise TooManyAttemptsError when over the limit."""
        if self.registrations_per_ip.is_exceeded(client_ip):
            raise self._error(self.registrations_per_ip)
        self.registrations_per_ip.record(client_ip)

    def reset(self) -> None:
        self.logins_per_ip.reset()
        self.failed_logins_per_email.reset()
        self.registrations_per_ip.reset()

    @staticmethod
    def _error(counter: SlidingWindowCounter) -> TooManyAttemptsError:
        return TooManyAttemptsError(retry_after_seconds=int(counter.window_seconds))
