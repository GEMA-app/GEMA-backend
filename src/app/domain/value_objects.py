import re
import uuid
from dataclasses import dataclass
from app.domain.exceptions import InvalidEmailError, WeakPasswordError


@dataclass(frozen=True)
class Email:
    """Objeto de valor que representa y valida una dirección de correo electrónico."""
    value: str

    def __post_init__(self) -> None:
        if not self.value or not isinstance(self.value, str):
            raise InvalidEmailError("El correo electrónico no puede estar vacío.")
        
        # Validación de formato de correo electrónico
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(pattern, self.value):
            raise InvalidEmailError(f"El correo electrónico '{self.value}' tiene un formato inválido.")


@dataclass(frozen=True)
class PlainPassword:
    """Objeto de valor que representa una contraseña en texto plano y valida su fortaleza."""
    value: str

    def __post_init__(self) -> None:
        if not self.value or len(self.value) < 8:
            raise WeakPasswordError("La contraseña debe tener al menos 8 caracteres.")
        if not re.search(r"[A-Z]", self.value):
            raise WeakPasswordError("La contraseña debe contener al menos una letra mayúscula.")
        if not re.search(r"\d", self.value):
            raise WeakPasswordError("La contraseña debe contener al menos un número.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>\-_]", self.value):
            raise WeakPasswordError("La contraseña debe contener al menos un carácter especial.")


@dataclass(frozen=True)
class HashedPassword:
    """Objeto de valor que representa una contraseña ya hasheada."""
    value: str

    def __post_init__(self) -> None:
        if not self.value or not isinstance(self.value, str):
            raise ValueError("El hash de la contraseña no puede estar vacío.")


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


@dataclass(frozen=True)
class Slug:
    """Objeto de valor que representa un identificador URL-friendly para una empresa.

    Formato válido: solo letras minúsculas, dígitos y guiones (a-z, 0-9, -).
    No puede comenzar ni terminar con guión. Longitud entre 2 y 63 caracteres.
    """
    value: str

    _PATTERN = re.compile(r"^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$")

    def __post_init__(self) -> None:
        if not self.value or not isinstance(self.value, str):
            raise ValueError("El slug no puede estar vacío.")
        if not self._PATTERN.match(self.value):
            raise ValueError(
                f"El slug '{self.value}' tiene un formato inválido. "
                "Solo se permiten letras minúsculas, dígitos y guiones, "
                "sin comenzar ni terminar con guión."
            )

    @classmethod
    def from_name(cls, name: str) -> "Slug":
        """Genera un slug a partir de un nombre de empresa."""
        import unicodedata
        # Normalizar unicode y eliminar acentos
        normalized = unicodedata.normalize("NFD", name.lower())
        ascii_name = "".join(c for c in normalized if unicodedata.category(c) != "Mn")
        # Reemplazar espacios y caracteres no válidos por guiones
        slug = re.sub(r"[^a-z0-9]+", "-", ascii_name).strip("-")
        return cls(value=slug[:63] if slug else "empresa")
