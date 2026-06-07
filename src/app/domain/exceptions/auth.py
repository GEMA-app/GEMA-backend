from app.domain.exceptions.base import DomainException
from app.domain.exceptions.validation import ValidationException


class AuthException(DomainException):
    """Clase base para excepciones del módulo de autenticación."""

    pass


class WeakPasswordError(AuthException):
    """Lanzada cuando la contraseña en texto plano no cumple con las reglas de complejidad."""

    pass


class InvalidEmailError(AuthException):
    """Lanzada cuando la dirección de correo electrónico tiene un formato inválido."""

    pass


class UserAlreadyExistsError(AuthException):
    """Lanzada cuando se intenta registrar un usuario con un correo electrónico ya registrado."""

    pass


class InvalidCredentialsError(AuthException):
    """Lanzada cuando el correo o la contraseña son incorrectos durante el inicio de sesión."""

    pass


class UserInactiveError(AuthException):
    """Lanzada cuando se intenta realizar una acción con un usuario inactivo o suspendido."""

    pass


class InvalidTokenError(AuthException):
    """Lanzada cuando un token de autenticación es inválido, revocado o ha expirado."""

    pass


class EmptyHashedPasswordError(AuthException, ValidationException):
    """Se lanza cuando el hash de la contraseña está vacío."""

    pass
