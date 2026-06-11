import uuid
from dataclasses import dataclass

from app.domain.exceptions import InvalidUUIDError


@dataclass(frozen=True)
class UserId:
    """Objeto de valor que representa el identificador único de un usuario (UUID)."""

    value: uuid.UUID

    def __str__(self) -> str:
        return str(self.value)

    @classmethod
    def from_string(cls, user_id_str: str) -> "UserId":
        if not isinstance(user_id_str, str) or not user_id_str:
            raise InvalidUUIDError(
                f"El identificador debe ser un string no vacío, se recibió: {type(user_id_str).__name__}"
            )
        try:
            return cls(value=uuid.UUID(user_id_str))
        except (ValueError, AttributeError) as e:
            raise InvalidUUIDError(f"El identificador '{user_id_str}' no es un UUID válido.") from e


@dataclass(frozen=True)
class CompanyId:
    """Objeto de valor que representa el identificador único de una empresa (UUID)."""

    value: uuid.UUID

    def __str__(self) -> str:
        return str(self.value)

    @classmethod
    def from_string(cls, value: str) -> "CompanyId":
        if not isinstance(value, str) or not value:
            raise InvalidUUIDError(
                f"El identificador debe ser un string no vacío, se recibió: {type(value).__name__}"
            )
        try:
            return cls(value=uuid.UUID(value))
        except (ValueError, AttributeError) as e:
            raise InvalidUUIDError(f"El identificador '{value}' no es un UUID válido.") from e


@dataclass(frozen=True)
class RoleId:
    """Objeto de valor que representa el identificador único de un rol (UUID)."""

    value: uuid.UUID

    def __str__(self) -> str:
        return str(self.value)

    @classmethod
    def from_string(cls, value: str) -> "RoleId":
        if not isinstance(value, str) or not value:
            raise InvalidUUIDError(
                f"El identificador debe ser un string no vacío, se recibió: {type(value).__name__}"
            )
        try:
            return cls(value=uuid.UUID(value))
        except (ValueError, AttributeError) as e:
            raise InvalidUUIDError(f"El identificador '{value}' no es un UUID válido.") from e


@dataclass(frozen=True)
class AssetId:
    """Objeto de valor que representa el identificador único de un activo (UUID)."""

    value: uuid.UUID

    def __str__(self) -> str:
        return str(self.value)

    @classmethod
    def from_string(cls, value: str) -> "AssetId":
        if not isinstance(value, str) or not value:
            raise InvalidUUIDError(
                f"El identificador debe ser un string no vacío, se recibió: {type(value).__name__}"
            )
        try:
            return cls(value=uuid.UUID(value))
        except (ValueError, AttributeError) as e:
            raise InvalidUUIDError(f"El identificador '{value}' no es un UUID válido.") from e


@dataclass(frozen=True)
class LocationId:
    """Objeto de valor que representa el identificador único de una ubicación (UUID)."""

    value: uuid.UUID

    def __str__(self) -> str:
        return str(self.value)

    @classmethod
    def from_string(cls, value: str) -> "LocationId":
        if not isinstance(value, str) or not value:
            raise InvalidUUIDError(
                f"El identificador debe ser un string no vacío, se recibió: {type(value).__name__}"
            )
        try:
            return cls(value=uuid.UUID(value))
        except (ValueError, AttributeError) as e:
            raise InvalidUUIDError(f"El identificador '{value}' no es un UUID válido.") from e
