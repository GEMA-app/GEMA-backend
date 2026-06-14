"""Repositorio base genérico con CRUD para SQLAlchemy 2.0 asíncrono."""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.events import DomainEvent, EventProducer

ModelT = TypeVar("ModelT")
EntityT = TypeVar("EntityT")
IdT = TypeVar("IdT")


class SqlAlchemyRepository(Generic[ModelT, EntityT, IdT], ABC):
    """Repositorio base con operaciones CRUD genéricas utilizando SQLAlchemy 2.0."""

    pk_column: str = "id"

    def __init__(
        self,
        session: AsyncSession,
        model_class: type[ModelT],
        pending_events: list[DomainEvent] | None = None,
    ) -> None:
        """Inicializa el repositorio con la sesión de base de datos y la clase de modelo.

        Args:
            session: Sesión asíncrona de SQLAlchemy.
            model_class: La clase de modelo ORM asociada.
            pending_events: Lista compartida para acumular eventos de dominio.
        """
        self.session = session
        self.model_class = model_class
        self.pending_events = pending_events

    @abstractmethod
    def _to_model(self, entity: EntityT) -> ModelT:
        """Convierte una entidad de dominio a un modelo ORM."""
        ...

    @abstractmethod
    def _to_entity(self, model: ModelT) -> EntityT:
        """Convierte un modelo ORM a una entidad de dominio."""
        ...

    def _collect_events(self, entity: EntityT) -> None:
        """Extrae eventos de la entidad si es EventProducer y los agrega a pending_events."""
        if isinstance(entity, EventProducer) and self.pending_events is not None:
            events = entity.pull_events()
            if events:
                self.pending_events.extend(events)

    async def save(self, entity: EntityT) -> None:
        """Persiste o actualiza una entidad en el repositorio sin confirmar la transacción.

        Utiliza session.merge() para soportar correctamente operaciones de creación
        y actualización sobre modelos con IDs generados en la aplicación.

        Args:
            entity: La entidad de dominio a guardar.
        """
        model = self._to_model(entity)
        await self.session.merge(model)
        self._collect_events(entity)


    async def get_by_id(self, id: IdT) -> EntityT | None:
        """Busca una entidad por su identificador único.

        Args:
            id: El identificador único de la entidad.

        Returns:
            La entidad de dominio si fue encontrada; de lo contrario, None.
        """
        # Se asume que 'id' es un objeto de valor que tiene una propiedad 'value'
        id_val = id.value if hasattr(id, "value") else id
        pk_attr = getattr(self.model_class, self.pk_column)
        stmt = select(self.model_class).where(pk_attr == id_val)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_entity(model)

    async def delete(self, id: IdT) -> None:
        """Elimina una entidad por su identificador único.

        Args:
            id: El identificador único de la entidad a eliminar.
        """
        id_val = id.value if hasattr(id, "value") else id
        pk_attr = getattr(self.model_class, self.pk_column)
        stmt = delete(self.model_class).where(pk_attr == id_val)
        await self.session.execute(stmt)
