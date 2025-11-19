"""Tests for utility functions."""

from pyclasscharts.utils import parse_cookies


class TestParseCookies:
    """Test cases for parse_cookies function."""

    def test_parses_simple_cookie(self):
        """Test parsing a simple cookie with URL encoding."""
        cookie = (
            "testCookie=Hello%20world!; expires=Tue, 28-Nov-2023 10:28:45 GMT; "
            "Max-Age=7776000; path=/"
        )
        parsed = parse_cookies(cookie)
        assert parsed["testCookie"] == "Hello world!"

    def test_parses_multiple_cookies(self):
        """Test parsing multiple cookies separated by commas."""
        cookies = (
            "firstCookie=I'm%20the%20first%20cookie; expires=Tue, 28-Nov-2023 10:28:45 GMT; "
            "Max-Age=7776000; path=/, secondCookie=I'm%20the%20second%20cookie; "
            "expires=Tue, 28-Nov-2023 10:28:45 GMT; Max-Age=7776000; path=/"
        )
        parsed = parse_cookies(cookies)
        assert parsed["firstCookie"] == "I'm the first cookie"
        assert parsed["secondCookie"] == "I'm the second cookie"

    def test_parses_cookie_with_no_value(self):
        """Test parsing a cookie with no value."""
        cookie = (
            "cookieWithNoValue=; expires=Tue, 28-Nov-2023 10:28:45 GMT; Max-Age=7776000; path=/"
        )
        parsed = parse_cookies(cookie)
        assert "cookieWithNoValue" in parsed
        assert parsed["cookieWithNoValue"] == ""
