from dataclasses import dataclass

@dataclass
class AuthStatus:
    enabled: bool | None  # True, False, or None if unknown
    note: str | None = None
