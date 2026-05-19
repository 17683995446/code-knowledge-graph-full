"""
Custom exceptions
"""


class AppException(Exception):
    """Base application exception"""
    pass


class ValidationError(AppException):
    """Validation error"""
    pass


class NotFoundError(AppException):
    """Resource not found error"""
    pass


class AuthenticationError(AppException):
    """Authentication error"""
    pass


class AuthorizationError(AppException):
    """Authorization error"""
    pass


class DatabaseError(AppException):
    """Database error"""
    pass


class CacheError(AppException):
    """Cache error"""
    pass


class ExternalServiceError(AppException):
    """External service error"""
    pass
