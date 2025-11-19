"""Custom exceptions for the ClassCharts API."""


class ClassChartsError(Exception):
    """Base exception for all ClassCharts API errors."""


class AuthenticationError(ClassChartsError):
    """Raised when authentication fails."""


class APIError(ClassChartsError):
    """Raised when the API returns an error response."""


class NoSessionError(ClassChartsError):
    """Raised when no session ID is available."""


class ValidationError(ClassChartsError):
    """Raised when validation fails."""
