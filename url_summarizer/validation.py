import ipaddress
import socket
from urllib.parse import urlparse

from url_summarizer.exceptions import InvalidUrlError

_BLOCKED_NETWORKS = (
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
)


def _is_blocked_ip(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    return any(ip in network for network in _BLOCKED_NETWORKS)


def validate_url(url: str) -> str:
    """Validate and normalize a user-supplied URL (SSRF-safe)."""
    normalized = url.strip()
    if not normalized:
        raise InvalidUrlError("URL is required.")

    parsed = urlparse(normalized)
    if parsed.scheme not in {"http", "https"}:
        raise InvalidUrlError("Only http and https URLs are supported.")
    if not parsed.hostname:
        raise InvalidUrlError("URL must include a hostname.")

    hostname = parsed.hostname.lower()
    if hostname in {"localhost", "127.0.0.1", "::1"}:
        raise InvalidUrlError("Localhost URLs are not allowed.")

    try:
        addr_infos = socket.getaddrinfo(hostname, parsed.port or (443 if parsed.scheme == "https" else 80))
    except socket.gaierror as exc:
        raise InvalidUrlError(f"Could not resolve hostname: {hostname}") from exc

    for info in addr_infos:
        ip_str = info[4][0]
        ip = ipaddress.ip_address(ip_str)
        if _is_blocked_ip(ip):
            raise InvalidUrlError("URL resolves to a private or reserved address.")

    return normalized
