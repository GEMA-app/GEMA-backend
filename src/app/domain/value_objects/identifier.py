"""Value Objects para identificadores UUID.

UserId, CompanyId, RoleId, AssetId, LocationId, FailureReportId,
InterventionId, RepuestoId, WorkOrderId y PlanExecutionId.
"""

import uuid
from dataclasses import dataclass

from app.domain.exceptions import InvalidUUIDError


@dataclass(frozen=True)
class UserId:
    """Objeto de valor que representa el identificador único de un usuario (UUID)."""

    value: uuid.UUID

    def __str__(self) -> str:
        """Retorna la representación en cadena del UUID."""
        return str(self.value)

    @classmethod
    def from_string(cls, user_id_str: str) -> "UserId":
        """Crea un UserId a partir de un string UUID.

        Args:
            user_id_str: String con el UUID del usuario.

        Returns:
            Un nuevo UserId.

        Raises:
            InvalidUUIDError: Si el string no es un UUID válido.
        """
        if not isinstance(user_id_str, str) or not user_id_str:
            raise InvalidUUIDError(
                f"El identificador debe ser un string no vacío, se recibió: "
                f"{type(user_id_str).__name__}"
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
        """Retorna la representación en cadena del UUID."""
        return str(self.value)

    @classmethod
    def from_string(cls, value: str) -> "CompanyId":
        """Crea un CompanyId a partir de un string UUID.

        Args:
            value: String con el UUID de la empresa.

        Returns:
            Un nuevo CompanyId.

        Raises:
            InvalidUUIDError: Si el string no es un UUID válido.
        """
        if not isinstance(value, str) or not value:
            raise InvalidUUIDError(
                f"El identificador debe ser un string no vacío, se recibió: "
                f"{type(value).__name__}"
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
        """Retorna la representación en cadena del UUID."""
        return str(self.value)

    @classmethod
    def from_string(cls, value: str) -> "RoleId":
        """Crea un RoleId a partir de un string UUID.

        Args:
            value: String con el UUID del rol.

        Returns:
            Un nuevo RoleId.

        Raises:
            InvalidUUIDError: Si el string no es un UUID válido.
        """
        if not isinstance(value, str) or not value:
            raise InvalidUUIDError(
                f"El identificador debe ser un string no vacío, se recibió: "
                f"{type(value).__name__}"
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
        """Retorna la representación en cadena del UUID."""
        return str(self.value)

    @classmethod
    def from_string(cls, value: str) -> "AssetId":
        """Crea un AssetId a partir de un string UUID.

        Args:
            value: String con el UUID del activo.

        Returns:
            Un nuevo AssetId.

        Raises:
            InvalidUUIDError: Si el string no es un UUID válido.
        """
        if not isinstance(value, str) or not value:
            raise InvalidUUIDError(
                f"El identificador debe ser un string no vacío, se recibió: "
                f"{type(value).__name__}"
            )
        try:
            return cls(value=uuid.UUID(value))
        except (ValueError, AttributeError) as e:
            raise InvalidUUIDError(f"El identificador '{value}' no es un UUID válido.") from e


@dataclass(frozen=True)
class MaintenancePlanId:
    """Objeto de valor que representa el identificador único de un plan de mantenimiento (UUID)."""

    value: uuid.UUID

    def __str__(self) -> str:
        """Retorna la representación en cadena del UUID."""
        return str(self.value)

    @classmethod
    def from_string(cls, value: str) -> "MaintenancePlanId":
        """Crea un MaintenancePlanId a partir de un string UUID.

        Args:
            value: String con el UUID del plan.

        Returns:
            Un nuevo MaintenancePlanId.

        Raises:
            InvalidUUIDError: Si el string no es un UUID válido.
        """
        if not isinstance(value, str) or not value:
            raise InvalidUUIDError(
                f"El identificador debe ser un string no vacío, se recibió: "
                f"{type(value).__name__}"
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
        """Retorna la representación en cadena del UUID."""
        return str(self.value)

    @classmethod
    def from_string(cls, value: str) -> "LocationId":
        """Crea un LocationId a partir de un string UUID.

        Args:
            value: String con el UUID de la ubicación.

        Returns:
            Un nuevo LocationId.

        Raises:
            InvalidUUIDError: Si el string no es un UUID válido.
        """
        if not isinstance(value, str) or not value:
            raise InvalidUUIDError(
                f"El identificador debe ser un string no vacío, se recibió: "
                f"{type(value).__name__}"
            )
        try:
            return cls(value=uuid.UUID(value))
        except (ValueError, AttributeError) as e:
            raise InvalidUUIDError(f"El identificador '{value}' no es un UUID válido.") from e


@dataclass(frozen=True)
class FailureReportId:
    """Objeto de valor que representa el identificador único de un reporte de falla (UUID)."""

    value: uuid.UUID

    def __str__(self) -> str:
        """Retorna la representación en cadena del UUID."""
        return str(self.value)

    @classmethod
    def from_string(cls, value: str) -> "FailureReportId":
        """Crea un FailureReportId a partir de un string UUID.

        Args:
            value: String con el UUID del reporte de falla.

        Returns:
            Un nuevo FailureReportId.

        Raises:
            InvalidUUIDError: Si el string no es un UUID válido.
        """
        if not isinstance(value, str) or not value:
            raise InvalidUUIDError(
                f"El identificador debe ser un string no vacío, se recibió: "
                f"{type(value).__name__}"
            )
        try:
            return cls(value=uuid.UUID(value))
        except (ValueError, AttributeError) as e:
            raise InvalidUUIDError(f"El identificador '{value}' no es un UUID válido.") from e


@dataclass(frozen=True)
class PlanExecutionId:
    """Objeto de valor que representa el identificador único de una ejecución de plan (UUID)."""

    value: uuid.UUID

    def __str__(self) -> str:
        """Retorna la representación en cadena del UUID."""
        return str(self.value)

    @classmethod
    def from_string(cls, value: str) -> "PlanExecutionId":
        """Crea un PlanExecutionId a partir de un string UUID.

        Args:
            value: String con el UUID de la ejecución.

        Returns:
            Un nuevo PlanExecutionId.

        Raises:
            InvalidUUIDError: Si el string no es un UUID válido.
        """
        if not isinstance(value, str) or not value:
            raise InvalidUUIDError(
                f"El identificador debe ser un string no vacío, se recibió: "
                f"{type(value).__name__}"
            )
        try:
            return cls(value=uuid.UUID(value))
        except (ValueError, AttributeError) as e:
            raise InvalidUUIDError(f"El identificador '{value}' no es un UUID válido.") from e


@dataclass(frozen=True)
class SubscriptionPlanId:
    """Objeto de valor que representa el identificador único de una suscripción a un plan (UUID)."""

    value: uuid.UUID

    def __str__(self) -> str:
        """Retorna la representación en cadena del UUID."""
        return str(self.value)

    @classmethod
    def from_string(cls, value: str) -> "SubscriptionPlanId":
        """Crea un SubscriptionPlanId a partir de un string UUID.

        Args:
            value: String con el UUID del plan.

        Returns:
            Un nuevo SubscriptionPlanId.

        Raises:
            InvalidUUIDError: Si el string no es un UUID válido.
        """
        if not isinstance(value, str) or not value:
            raise InvalidUUIDError(
                f"El identificador debe ser un string no vacío, se recibió: "
                f"{type(value).__name__}"
            )
        try:
            return cls(value=uuid.UUID(value))
        except (ValueError, AttributeError) as e:
            raise InvalidUUIDError(f"El identificador '{value}' no es un UUID válido.") from e


@dataclass(frozen=True)
class InterventionId:
    """Objeto de valor que representa el identificador único de una intervención técnica (UUID)."""

    value: uuid.UUID

    def __str__(self) -> str:
        """Retorna la representación en cadena del UUID."""
        return str(self.value)

    @classmethod
    def from_string(cls, value: str) -> "InterventionId":
        """Crea un InterventionId a partir de un string UUID.

        Args:
            value: String con el UUID de la intervención.

        Returns:
            Un nuevo InterventionId.

        Raises:
            InvalidUUIDError: Si el string no es un UUID válido.
        """
        if not isinstance(value, str) or not value:
            raise InvalidUUIDError(
                f"El identificador debe ser un string no vacío, se recibió: "
                f"{type(value).__name__}"
            )
        try:
            return cls(value=uuid.UUID(value))
        except (ValueError, AttributeError) as e:
            raise InvalidUUIDError(f"El identificador '{value}' no es un UUID válido.") from e

    @classmethod
    def generate(cls) -> "InterventionId":
        """Genera un nuevo identificador aleatorio."""
        return cls(value=uuid.uuid4())

    @classmethod
    def from_string_or_generate(cls, value: str | None = None) -> "InterventionId":
        """Crea un InterventionId a partir de un string, o genera uno nuevo si es None.

        Args:
            value: String UUID opcional.

        Returns:
            InterventionId: Nueva instancia.
        """
        if value is None:
            return cls.generate()
        return cls.from_string(value)

@dataclass(frozen=True)
class WorkOrderId:
    """Objeto de valor que representa el identificador único de una orden de trabajo (UUID)."""

    value: uuid.UUID

    def __str__(self) -> str:
        """Retorna la representación en cadena del UUID."""
        return str(self.value)

    @classmethod
    def from_string(cls, value: str) -> "WorkOrderId":
        """Crea un WorkOrderId a partir de un string UUID.

        Args:
            value: String con el UUID de la orden de trabajo.

        Returns:
            Un nuevo WorkOrderId.

        Raises:
            InvalidUUIDError: Si el string no es un UUID válido.
        """
        if not isinstance(value, str) or not value:
            raise InvalidUUIDError(
                f"El identificador debe ser un string no vacío, se recibió: "
                f"{type(value).__name__}"
            )
        try:
            return cls(value=uuid.UUID(value))
        except (ValueError, AttributeError) as e:
            raise InvalidUUIDError(f"El identificador '{value}' no es un UUID válido.") from e


@dataclass(frozen=True)
class RepuestoId:
    """Objeto de valor que representa el identificador único de un repuesto (UUID)."""

    value: uuid.UUID

    def __str__(self) -> str:
        """Retorna la representación en cadena del UUID."""
        return str(self.value)

    @classmethod
    def from_string(cls, value: str) -> "RepuestoId":
        """Crea un RepuestoId a partir de un string UUID.

        Args:
            value: String con el UUID del repuesto.

        Returns:
            Un nuevo RepuestoId.

        Raises:
            InvalidUUIDError: Si el string no es un UUID válido.
        """
        if not isinstance(value, str) or not value:
            raise InvalidUUIDError(
                f"El identificador debe ser un string no vacío, se recibió: "
                f"{type(value).__name__}"
            )
        try:
            return cls(value=uuid.UUID(value))
        except (ValueError, AttributeError) as e:
            raise InvalidUUIDError(f"El identificador '{value}' no es un UUID válido.") from e


@dataclass(frozen=True)
class ArticleId:
    """Objeto de valor que representa el identificador único de un artículo de catálogo (UUID)."""

    value: uuid.UUID

    def __str__(self) -> str:
        """Retorna la representación en cadena del UUID."""
        return str(self.value)

    @classmethod
    def from_string(cls, value: str) -> "ArticleId":
        """Crea un ArticleId a partir de un string UUID.

        Args:
            value: String con el UUID del artículo.

        Returns:
            Un nuevo ArticleId.

        Raises:
            InvalidUUIDError: Si el string no es un UUID válido.
        """
        if not isinstance(value, str) or not value:
            raise InvalidUUIDError(
                f"El identificador debe ser un string no vacío, se recibió: "
                f"{type(value).__name__}"
            )
        try:
            return cls(value=uuid.UUID(value))
        except (ValueError, AttributeError) as e:
            raise InvalidUUIDError(f"El identificador '{value}' no es un UUID válido.") from e


@dataclass(frozen=True)
class ProviderId:
    """Objeto de valor que representa el identificador único de un proveedor (UUID)."""

    value: uuid.UUID

    def __str__(self) -> str:
        """Retorna la representación en cadena del UUID."""
        return str(self.value)

    @classmethod
    def from_string(cls, value: str) -> "ProviderId":
        """Crea un ProviderId a partir de un string UUID.

        Args:
            value: String con el UUID del proveedor.

        Returns:
            Un nuevo ProviderId.

        Raises:
            InvalidUUIDError: Si el string no es un UUID válido.
        """
        if not isinstance(value, str) or not value:
            raise InvalidUUIDError(
                f"El identificador debe ser un string no vacío, se recibió: "
                f"{type(value).__name__}"
            )
        try:
            return cls(value=uuid.UUID(value))
        except (ValueError, AttributeError) as e:
            raise InvalidUUIDError(f"El identificador '{value}' no es un UUID válido.") from e
