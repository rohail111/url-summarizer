class UrlSummarizerError(Exception):
    """Base error for the summarizer service."""


class InvalidUrlError(UrlSummarizerError):
    """Raised when a URL fails validation."""


class FetchError(UrlSummarizerError):
    """Raised when page content cannot be fetched."""


class SummarizationError(UrlSummarizerError):
    """Raised when the LLM chain fails."""
