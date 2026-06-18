"""Module for app.src.utils.geoip."""

from typing import Tuple, Optional


def lookup_ip(ip: str) -> Tuple[Optional[str], Optional[str]]:
    """Placeholder geo IP lookup.

    Returns (country, city) or (None, None) if unknown.
    You can replace this with a real provider (geoip2, ipinfo, etc.).
    """
    if not ip:
        return None, None

    # Simple heuristic for localhost / private addresses
    if ip.startswith("127.") or ip.startswith("10.") or ip.startswith("192.168."):
        return None, None

    # No provider configured — return None so caller can try headers
    return None, None
