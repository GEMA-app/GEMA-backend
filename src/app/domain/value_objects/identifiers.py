import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class UserId:
    """Objeto de valor que representa el identificador único de un usuario (UUID)."""

    value: uuid.UUID

    def __str__(self) -> str:
        return str(self.value)

    @classmethod
    def from_string(cls, user_id_str: str) -> "UserId":
        try:
            return cls(value=uuid.UUID(user_id_str))
        except ValueError:
            raise ValueError(f"El identificador '{user_id_str}' no es un UUID válido.")


@dataclass(frozen=True)
class CompanyId:
    """Objeto de valor que representa el identificador único de una empresa (UUID)."""

    value: uuid.UUID

    def __str__(self) -> str:
        return str(self.value)

    @classmethod
    def from_string(cls, value: str) -> "CompanyId":
        try:
            return cls(value=uuid.UUID(value))
        except ValueError:
            raise ValueError(f"El identificador '{value}' no es un UUID válido.")


@dataclass(frozen=True)
class RoleId:
    """Objeto de valor que representa el identificador único de un rol (UUID)."""

    value: uuid.UUID

    def __str__(self) -> str:
        return str(self.value)

    @classmethod
    def from_string(cls, value: str) -> "RoleId":
        try:
            return cls(value=uuid.UUID(value))
        except ValueError:
            raise ValueError(f"El identificador '{value}' no es un UUID válido.")


@dataclass(frozen=True)
class AssetId:
    """Objeto de valor que representa el identificador único de un activo (UUID)."""

    value: uuid.UUID

    def __str__(self) -> str:
        return str(self.value)

    @classmethod
    def from_string(cls, value: str) -> "AssetId":
        try:
            return cls(value=uuid.UUID(value))
        except ValueError:
            raise ValueError(f"El identificador '{value}' no es un UUID válido.")


@dataclass(frozen=True)
class LocationId:
    """Objeto de valor que representa el identificador único de una ubicación (UUID)."""

    value: uuid.UUID

    def __str__(self) -> str:
        return str(self.value)

    @classmethod
    def from_string(cls, value: str) -> "LocationId":
        try:
            return cls(value=uuid.UUID(value))
        except ValueError:
            raise ValueError(f"El identificador '{value}' no es un UUID válido.")
