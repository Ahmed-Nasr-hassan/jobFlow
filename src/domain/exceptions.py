"""Domain exceptions - Pure business rule exceptions."""


class DomainException(Exception):
    """Base exception for all domain errors."""

    pass


class ScriptExecutionException(DomainException):
    """Raised when script execution fails."""

    def __init__(self, message: str, exit_code: int | None = None):
        super().__init__(message)
        self.exit_code = exit_code


class InvalidScriptException(DomainException):
    """Raised when script configuration is invalid."""

    pass

