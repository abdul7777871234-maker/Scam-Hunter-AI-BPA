from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse


def validate_url(value: str) -> bool:
    """Validate HTTP(S) URLs and reject local/private/reserved targets."""
    try:
        parsed = urlparse(str(value or "").strip())
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            return False

        hostname = parsed.hostname.rstrip(".").lower()
        if hostname in {"localhost", "localhost.localdomain"}:
            return False

        try:
            ip = ipaddress.ip_address(hostname)
            if any((ip.is_private, ip.is_loopback, ip.is_link_local,
                    ip.is_reserved, ip.is_multicast, ip.is_unspecified)):
                return False
        except ValueError:
            pass

        if "." not in hostname:
            return False

        try:
            addresses = socket.getaddrinfo(
                hostname,
                parsed.port or (443 if parsed.scheme == "https" else 80),
                type=socket.SOCK_STREAM,
            )
        except OSError:
            return False

        for item in addresses:
            try:
                ip = ipaddress.ip_address(item[4][0])
            except ValueError:
                return False
            if any((ip.is_private, ip.is_loopback, ip.is_link_local,
                    ip.is_reserved, ip.is_multicast, ip.is_unspecified)):
                return False

        return True
    except (TypeError, ValueError):
        return False
