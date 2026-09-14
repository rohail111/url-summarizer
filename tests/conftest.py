from unittest.mock import patch

import pytest

# example.com resolves to a public IP (93.184.216.34)
_PUBLIC_ADDRINFO = [(2, 1, 6, "", ("93.184.216.34", 443))]


@pytest.fixture
def public_dns():
    """Mock DNS so URL validation works offline in CI/sandbox."""
    with patch("url_summarizer.validation.socket.getaddrinfo", return_value=_PUBLIC_ADDRINFO) as mock:
        yield mock
