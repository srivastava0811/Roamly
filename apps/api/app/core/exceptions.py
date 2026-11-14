from typing import Any, Dict, Optional


class RoamlyException(Exception):
    """Base exception for all domain and API errors."""
    def __init__(self, message: str, code: str = "INTERNAL_ERROR", status_code: int = 500, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}


class EntityNotFoundException(RoamlyException):
    def __init__(self, entity_name: str, entity_id: str):
        super().__init__(
            message=f"{entity_name} with ID '{entity_id}' was not found.",
            code="NOT_FOUND",
            status_code=404,
            details={"entity": entity_name, "id": entity_id},
        )


class ValidationException(RoamlyException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=422,
            details=details,
        )


class ProviderException(RoamlyException):
    def __init__(self, provider: str, message: str, retryable: bool = False):
        super().__init__(
            message=f"Provider '{provider}' failed: {message}",
            code="PROVIDER_ERROR",
            status_code=502,
            details={"provider": provider, "retryable": retryable},
        )


class QuotaExceededException(RoamlyException):
    def __init__(self, resource: str):
        super().__init__(
            message=f"Quota exceeded for resource '{resource}'.",
            code="QUOTA_EXCEEDED",
            status_code=429,
            details={"resource": resource},
        )
