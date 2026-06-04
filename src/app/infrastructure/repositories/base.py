from typing import Generic, TypeVar, Optional
from abc import ABC, abstractmethod
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

ModelT = TypeVar("ModelT")
EntityT = TypeVar("EntityT")
IdT = TypeVar("IdT")


class SqlAlchemyRepository(Generic[ModelT, EntityT, IdT], ABC):
    """Repositorio base con operaciones CRUD genéricas utilizando SQLAlchemy 2.0."""

    def __init__(self, session: AsyncSession, model_class: type[ModelT]) -> None:
        self.session = session
        self.model_class = model_class

    @abstractmethod
    def _to_model(self, entity: EntityT) -> ModelT:
        """Convierte una entidad de dominio a un modelo ORM."""
        ...

    @abstractmethod
    def _to_entity(self, model: ModelT) -> EntityT:
        """Convierte un modelo ORM a una entidad de dominio."""
        ...

    async def save(self, entity: EntityT) -> None:
        """Persiste o actualiza una entidad en el repositorio sin confirmar la transacción."""
        model = self._to_model(entity)
        await self.session.merge(model)

    async def get_by_id(self, id: IdT) -> Optional[EntityT]:
        """Busca una entidad por su identificador único."""
        # Se asume que 'id' es un objeto de valor que tiene una propiedad 'value'
        id_val = id.value if hasattr(id, "value") else id
        stmt = select(self.model_class).where(self.model_class.id == id_val)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_entity(model)

    async def delete(self, id: IdT) -> None:
        """Elimina una entidad por su identificador único."""
        id_val = id.value if hasattr(id, "value") else id
        stmt = delete(self.model_class).where(self.model_class.id == id_val)
        await self.session.execute(stmt)
