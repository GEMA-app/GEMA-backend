import re
from dataclasses import dataclass

from app.domain.exceptions import EmptyHashedPasswordError, InvalidEmailError, WeakPasswordError


@dataclass(frozen=True)
class Email:
    """Objeto de valor que representa y valida una dirección de correo electrónico."""

    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, 'value', self.value.strip().lower())
        if not self.value or not isinstance(self.value, str):
            raise InvalidEmailError("El correo electrónico no puede estar vacío.")

        # Validación de formato de correo electrónico
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(pattern, self.value):
            raise InvalidEmailError(
                f"El correo electrónico '{self.value}' tiene un formato inválido."
            )


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
            raise EmptyHashedPasswordError("El hash de la contraseña no puede estar vacío.")
