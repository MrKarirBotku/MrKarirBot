class MrKarirBotError(Exception):
    """Base exception for domain-level MrKarirBot failures."""


class ExternalServiceError(MrKarirBotError):
    """Raised when an external provider fails."""
