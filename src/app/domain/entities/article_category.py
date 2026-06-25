from dataclasses import dataclass
from uuid import UUID
from app.domain.exceptions.base import ValidationError

@dataclass
class ArticleCategory:
    id: UUID
    empresa_id: UUID
    nombre: str
    descripcion: str | None
    version: int

    @classmethod
    def create(cls, id: UUID, empresa_id: UUID, nombre: str, descripcion: str | None) -> "ArticleCategory":
        """Fábrica de dominio rica que protege las invariantes de negocio."""
        if not nombre or len(nombre.strip()) == 0:
            raise ValidationError("El nombre de la categoría es obligatorio.")
        if len(nombre) > 100:
            raise ValidationError("El nombre no puede exceder los 100 caracteres.")
            
        return cls(
            id=id,
            empresa_id=empresa_id,
            nombre=nombre.strip(),
            descripcion=descripcion.strip() if descripcion else None,
            version=1
        )

    def change_nombre(self, nuevo_nombre: str) -> None:
        if not nuevo_nombre or len(nuevo_nombre.strip()) == 0:
            raise ValidationError("El nombre de la categoría es obligatorio.")
        if len(nuevo_nombre) > 100:
            raise ValidationError("El nombre no puede exceder los 100 caracteres.")
        self.nombre = nuevo_nombre.strip()

    def change_descripcion(self, nueva_descripcion: str | None) -> None:
        if nueva_descripcion and len(nueva_descripcion) > 255:
            raise ValidationError("La descripción no puede exceder los 255 caracteres.")
        self.descripcion = nueva_descripcion.strip() if nueva_descripcion else None