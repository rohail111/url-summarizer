import logging

import requests
from bs4 import BeautifulSoup
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from url_summarizer.config import get_settings
from url_summarizer.exceptions import FetchError
from url_summarizer.validation import validate_url

logger = logging.getLogger(__name__)

_USER_AGENT = "UrlSummarizer/1.0 (+https://github.com/url-summarizer)"


@retry(
    retry=retry_if_exception_type(requests.RequestException),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    reraise=True,
)
def _get(url: str) -> requests.Response:
    settings = get_settings()
    return requests.get(
        url,
        timeout=settings.fetch_timeout_seconds,
        headers={"User-Agent": _USER_AGENT},
        allow_redirects=True,
    )


def fetch_url_text(url: str) -> str:
    """Fetch and extract readable text from a URL."""
    safe_url = validate_url(url)
    settings = get_settings()

    try:
        response = _get(safe_url)
        response.raise_for_status()
    except requests.RequestException as exc:
        logger.warning("Fetch failed for %s: %s", safe_url, exc)
        raise FetchError(f"Failed to fetch URL: {exc}") from exc

    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    content = "\n".join(lines)

    if not content:
        raise FetchError("No readable text found on the page.")

    truncated = content[: settings.max_content_chars]
    logger.info(
        "Fetched %d chars from %s (returning %d)",
        len(content),
        safe_url,
        len(truncated),
    )
    return truncated
