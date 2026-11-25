"""Domain errors of the job search. The routes turn them into HTTP errors."""


class JobSearchError(Exception):
    """Base class: catch it to handle any job search problem."""


class SearchAlreadyActiveError(JobSearchError):
    """A search for this user is already waiting or running."""


class SearchRateLimitError(JobSearchError):
    """The user started too many searches by hand today."""


class ProfileIncompleteError(JobSearchError):
    """The profile has nothing to search with: no job title, headline or skill."""


class SourceError(JobSearchError):
    """A job board could not be reached or answered something unexpected."""
