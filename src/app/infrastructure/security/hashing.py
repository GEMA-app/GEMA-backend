import bcrypt
import structlog

from app.application.ports.auth import PasswordHasherPort

logger = structlog.get_logger()


class BcryptPasswordHasher(PasswordHasherPort):
    """Implementación de PasswordHasherPort utilizando la librería bcrypt nativa."""

    def hash(self, password: str) -> str:
        """Genera un hash seguro utilizando bcrypt con salt automático."""
        password_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt()
        hashed_bytes = bcrypt.hashpw(password_bytes, salt)
        return hashed_bytes.decode("utf-8")

    def verify(self, password: str, hashed_password: str) -> bool:
        """Verifica que la contraseña en texto plano coincida con el hash almacenado."""
        password_bytes = password.encode("utf-8")
        hashed_bytes = hashed_password.encode("utf-8")
        try:
            return bcrypt.checkpw(password_bytes, hashed_bytes)
        except ValueError:
            logger.error("bcrypt_verify_error", hashed_length=len(hashed_password))
            return False
