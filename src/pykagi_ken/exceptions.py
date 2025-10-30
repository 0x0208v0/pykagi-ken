"""
Custom exceptions for pykagi-ken.
"""


class PyKagiKenError(Exception):
    """Base exception for all pykagi-ken errors."""

    pass


class AuthenticationError(PyKagiKenError):
    """Raised when authentication fails (invalid session token)."""

    pass


class NetworkError(PyKagiKenError):
    """Raised when network request fails."""

    pass


class ParsingError(PyKagiKenError):
    """Raised when parsing response fails."""

    pass


class ValidationError(PyKagiKenError):
    """Raised when input validation fails."""

    pass
