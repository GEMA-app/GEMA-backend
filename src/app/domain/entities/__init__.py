# Re-exporta todas las entidades del dominio para mantener compatibilidad
# con imports existentes: `from app.domain.entities import User`
from app.domain.entities.user import User

__all__ = ["User"]
