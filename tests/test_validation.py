from unittest.mock import patch

import pytest

from url_summarizer.exceptions import InvalidUrlError
from url_summarizer.validation import validate_url


def test_validate_url_accepts_https(public_dns):
    assert validate_url("https://example.com") == "https://example.com"
    public_dns.assert_called_once()


def test_validate_url_rejects_empty():
    with pytest.raises(InvalidUrlError):
        validate_url("")


def test_validate_url_rejects_localhost():
    with pytest.raises(InvalidUrlError):
        validate_url("http://localhost/admin")


def test_validate_url_rejects_non_http_scheme():
    with pytest.raises(InvalidUrlError):
        validate_url("file:///etc/passwd")


def test_validate_url_rejects_private_ip_resolution():
    private_addrinfo = [(2, 1, 6, "", ("192.168.1.1", 80))]
    with patch("url_summarizer.validation.socket.getaddrinfo", return_value=private_addrinfo):
        with pytest.raises(InvalidUrlError, match="private or reserved"):
            validate_url("http://evil.example.com")
