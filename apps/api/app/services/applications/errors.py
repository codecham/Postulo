"""Domain errors of the tailored applications. The routes turn them into HTTP errors."""


class ApplicationError(Exception):
    """Base class: catch it to handle any application problem."""


class ApplicationNotFoundError(ApplicationError):
    """The match has no application yet, or belongs to another user."""


class EmptyProfileError(ApplicationError):
    """The profile has no experience, education or skill to build a CV from."""


class ApplicationRateLimitError(ApplicationError):
    """The user generated too many applications in the last hour."""


class GenerationFailedError(ApplicationError):
    """The AI could not be reached or did not return a usable answer."""
