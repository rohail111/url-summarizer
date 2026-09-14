from unittest.mock import MagicMock, patch

import pytest

from url_summarizer.exceptions import FetchError
from url_summarizer.fetch import fetch_url_text


@patch("url_summarizer.fetch._get")
def test_fetch_url_text_extracts_content(mock_get, public_dns):
    response = MagicMock()
    response.text = """
    <html><head><title>T</title></head>
    <body><script>ignore</script><p>Hello world</p></body></html>
    """
    response.raise_for_status = MagicMock()
    mock_get.return_value = response

    text = fetch_url_text("https://example.com")
    assert "Hello world" in text
    assert "ignore" not in text


@patch("url_summarizer.fetch._get")
def test_fetch_url_text_raises_on_empty_page(mock_get, public_dns):
    response = MagicMock()
    response.text = "<html><body></body></html>"
    response.raise_for_status = MagicMock()
    mock_get.return_value = response

    with pytest.raises(FetchError):
        fetch_url_text("https://example.com")
