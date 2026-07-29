"""Entidad de dominio para Órdenes de Trabajo."""

from dataclasses import dataclass
from datetime import UTC, datetime

from app.domain.enums import MaintenanceType, WorkOrderStatus
from app.domain.exceptions.work_order import (
    WorkOrderInvalidDataError,
    WorkOrderInvalidStateError,
)
from app.domain.value_objects.identifier import (
    AssetId,
    CompanyId,
    UserId,
    WorkOrderId,
)

# Máquina de estados explícita: cada estado enumera sus transiciones válidas.
# Agregar un estado nuevo = actualizar este dict + crear método _transition.
_VALID_TRANSITIONS: dict[WorkOrderStatus, set[WorkOrderStatus]] = {
    WorkOrderStatus.OPEN: {WorkOrderStatus.IN_PROGRESS, WorkOrderStatus.CANCELLED},
    WorkOrderStatus.IN_PROGRESS: {
        WorkOrderStatus.PAUSED,
        WorkOrderStatus.CLOSED,
        WorkOrderStatus.CANCELLED,
    },
    WorkOrderStatus.PAUSED: {WorkOrderStatus.IN_PROGRESS, WorkOrderStatus.CANCELLED},
    WorkOrderStatus.CLOSED: set(),
    WorkOrderStatus.CANCELLED: set(),
}


@dataclass
class WorkOrder:
    """Entidad que representa una orden de trabajo en el dominio de mantenimiento.

    Gestiona el ciclo de vida completo de una orden de trabajo, incluyendo
    su creación, transiciones de estado (máquina de estados) y actualización
    de detalles. Cada orden pertenece a una empresa y está asociada a un activo.
    """

    id: WorkOrderId
    empresa_id: CompanyId
    codigo_ot: str
    activo_id: AssetId
    tipo: MaintenanceType
    estado: WorkOrderStatus
    reporte_id: str | None = None
    plan_id: str | None = None
    supervisor_id: UserId | None = None
    fecha_apertura: datetime | None = None
    fecha_inicio_trabajo: datetime | None = None
    fecha_cierre: datetime | None = None
    descripcion_trabajo: str | None = None
    costo_estimado: float | None = None
    costo_real: float | None = None
    moneda: str = "USD"
    validado_por_id: UserId | None = None
    fecha_validacion: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    version: int = 1

    @classmethod
    def create(
        cls,
        work_order_id: WorkOrderId,
        empresa_id: CompanyId,
        codigo_ot: str,
        activo_id: AssetId,
        tipo: MaintenanceType,
        supervisor_id: UserId | None = None,
        descripcion_trabajo: str | None = None,
        costo_estimado: float | None = None,
        moneda: str = "USD",
    ) -> "WorkOrder":
        """Crea una nueva orden de trabajo con estado inicial ABERTA.

        Args:
            work_order_id: Identificador único de la orden.
            empresa_id: Identificador de la empresa a la que pertenece.
            codigo_ot: Código único de la orden de trabajo.
            activo_id: Identificador del activo asociado.
            tipo: Tipo de mantenimiento (preventivo, correctivo, predictivo).
            supervisor_id: Identificador del supervisor (opcional).
            descripcion_trabajo: Descripción del trabajo a realizar (opcional).
            costo_estimado: Costo estimado de la orden (opcional).
            moneda: Moneda del costo (por defecto USD).

        Returns:
            WorkOrder: Instancia creada con estado OPEN y fecha de apertura.

        Raises:
            WorkOrderInvalidDataError: Si el código está vacío o el costo es negativo.
        """
        if not codigo_ot or not codigo_ot.strip():
            raise WorkOrderInvalidDataError("El código de orden de trabajo no puede estar vacío.")
        if costo_estimado is not None and costo_estimado < 0:
            raise WorkOrderInvalidDataError("El costo estimado no puede ser negativo.")
        return cls(
            id=work_order_id,
            empresa_id=empresa_id,
            codigo_ot=codigo_ot.strip(),
            activo_id=activo_id,
            tipo=tipo,
            estado=WorkOrderStatus.OPEN,
            supervisor_id=supervisor_id,
            descripcion_trabajo=descripcion_trabajo.strip() if descripcion_trabajo else None,
            costo_estimado=costo_estimado,
            moneda=moneda,
            fecha_apertura=datetime.now(UTC),
        )

    def _transition(self, new_status: WorkOrderStatus) -> None:
        """Transiciona la orden de trabajo a un nuevo estado.

        Args:
            new_status: Nuevo estado al que transicionar.

        Raises:
            WorkOrderInvalidStateError: Si la transición no está permitida
                según la máquina de estados definida en _VALID_TRANSITIONS.
        """
        allowed = _VALID_TRANSITIONS.get(self.estado, set())
        if new_status not in allowed:
            raise WorkOrderInvalidStateError(
                f"No se puede cambiar de '{self.estado.value}' a '{new_status.value}'."
            )
        self.estado = new_status

    def start(self) -> None:
        """Inicia la orden de trabajo, moviéndola a estado EN_PROCESO.

        Registra la fecha y hora de inicio del trabajo.
        """
        self._transition(WorkOrderStatus.IN_PROGRESS)
        self.fecha_inicio_trabajo = datetime.now(UTC)

    def pause(self) -> None:
        """Pausa la orden de trabajo, moviéndola a estado PAUSADA."""
        self._transition(WorkOrderStatus.PAUSED)

    def resume(self) -> None:
        """Reanuda la orden de trabajo, volviendo a estado EN_PROCESO."""
        self._transition(WorkOrderStatus.IN_PROGRESS)

    def close(self) -> None:
        """Cierra la orden de trabajo, moviéndola a estado CERRADA.

        Registra la fecha y hora de cierre.
        """
        self._transition(WorkOrderStatus.CLOSED)
        self.fecha_cierre = datetime.now(UTC)

    def cancel(self) -> None:
        """Cancela la orden de trabajo, moviéndola a estado CANCELADA."""
        self._transition(WorkOrderStatus.CANCELLED)

    @staticmethod
    def generate_code(company_id: CompanyId) -> str:
        """Genera un código de orden de trabajo con formato OT-año-XXXX.

        Args:
            company_id: Identificador de la empresa.

        Returns:
            str: Código de orden de trabajo en formato OT-año-XXXX.
        """
        import random

        year = datetime.now(UTC).year
        val = random.randint(1000, 9999)
        return f"OT-{year}-{val:04d}"

    def update_details(
        self,
        descripcion_trabajo: str | None = None,
        costo_estimado: float | None = None,
        costo_real: float | None = None,
        supervisor_id: UserId | None = None,
    ) -> None:
        """Actualiza los detalles de la orden de trabajo.

        Solo actualiza los campos cuyo valor no sea None, permitiendo
        actualizaciones parciales. Los costos no pueden ser negativos.

        Args:
            descripcion_trabajo: Nueva descripción (opcional).
            costo_estimado: Nuevo costo estimado (opcional).
            costo_real: Nuevo costo real (opcional).
            supervisor_id: Nuevo supervisor asignado (opcional).

        Raises:
            WorkOrderInvalidDataError: Si algún costo es negativo.
        """
        if costo_estimado is not None and costo_estimado < 0:
            raise WorkOrderInvalidDataError("El costo estimado no puede ser negativo.")
        if costo_real is not None and costo_real < 0:
            raise WorkOrderInvalidDataError("El costo real no puede ser negativo.")
        if descripcion_trabajo is not None:
            self.descripcion_trabajo = descripcion_trabajo.strip()
        if costo_estimado is not None:
            self.costo_estimado = costo_estimado
        if costo_real is not None:
            self.costo_real = costo_real
        if supervisor_id is not None:
            self.supervisor_id = supervisor_id

    def validate(self, validator_id: UserId) -> None:
        """Valida la orden de trabajo.

        Solo se pueden validar órdenes de trabajo cerradas (CLOSED).

        Args:
            validator_id: Identificador del usuario que realiza la validación.

        Raises:
            WorkOrderInvalidStateError: Si la orden no está en estado CLOSED.
        """
        if self.estado != WorkOrderStatus.CLOSED:
            raise WorkOrderInvalidStateError("Solo se pueden validar órdenes de trabajo cerradas.")
        self.validado_por_id = validator_id
        self.fecha_validacion = datetime.now(UTC)
