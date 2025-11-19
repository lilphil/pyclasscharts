"""Utility functions for the ClassCharts API."""

from typing import Dict
from urllib.parse import unquote


def parse_cookies(cookie_string: str) -> Dict[str, str]:
    """
    Parse cookies from a Set-Cookie header string.

    Args:
        cookie_string: The cookie string from the Set-Cookie header

    Returns:
        A dictionary of cookie names to values
    """
    output: Dict[str, str] = {}
    cookies = cookie_string.split(",")
    for cookie in cookies:
        cookie_part = cookie.split(";")[0]
        if "=" in cookie_part:
            key, value = cookie_part.split("=", 1)
            # Decode URL-encoded cookie names and values (like JavaScript's decodeURIComponent)
            decoded_key = unquote(key).lstrip()
            decoded_value = unquote(value)
            output[decoded_key] = decoded_value
    return output
