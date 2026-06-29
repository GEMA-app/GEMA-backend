"""Entidad MaintenancePlan — plan de mantenimiento preventivo de un activo."""

import uuid
from dataclasses import dataclass
from datetime import date, datetime

from app.domain.enums import MaintenanceType
from app.domain.exceptions.maintenance_plan import (
    MaintenancePlanDueDateError,
    MaintenancePlanIntervalError,
    MaintenancePlanNameEmptyError,
)
from app.domain.value_objects import AssetId, CompanyId, MaintenancePlanId, UserId


@dataclass
class MaintenancePlan:
    """Entidad que representa un plan de mantenimiento preventivo programado.

    Define la periodicidad, el activo asociado, el técnico responsable
    y las tareas a ejecutar en cada ciclo de mantenimiento.
    """

    id: MaintenancePlanId
    empresa_id: CompanyId
    activo_id: AssetId
    nombre: str
    tipo: MaintenanceType
    intervalo_dias: int
    proxima_ejecucion: date
    tecnico_responsable_id: UserId | None = None
    descripcion_tareas: str | None = None
    activo: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def __post_init__(self) -> None:
        """Valida invariantes de la entidad al ser inicializada.

        Raises:
            MaintenancePlanNameEmptyError: Si el nombre está vacío.
            MaintenancePlanIntervalError: Si el intervalo es menor o igual a cero.
            MaintenancePlanDueDateError: Si la fecha de próxima ejecución es None.
        """
        if not self.nombre or not self.nombre.strip():
            raise MaintenancePlanNameEmptyError()
        if self.intervalo_dias <= 0:
            raise MaintenancePlanIntervalError(self.intervalo_dias)
        if self.proxima_ejecucion is None:
            raise MaintenancePlanDueDateError()

    @classmethod
    def create(
        cls,
        empresa_id: CompanyId,
        activo_id: AssetId,
        nombre: str,
        tipo: MaintenanceType,
        intervalo_dias: int,
        proxima_ejecucion: date,
        tecnico_responsable_id: UserId | None = None,
        descripcion_tareas: str | None = None,
    ) -> "MaintenancePlan":
        """Crea un nuevo plan de mantenimiento.

        Args:
            empresa_id: Empresa propietaria del plan.
            activo_id: Activo asociado al plan.
            nombre: Nombre descriptivo del plan.
            tipo: Tipo de mantenimiento (preventivo, predictivo, etc.).
            intervalo_dias: Días entre ejecuciones.
            proxima_ejecucion: Fecha de la próxima ejecución programada.
            tecnico_responsable_id: Técnico responsable (opcional).
            descripcion_tareas: Descripción de las tareas a realizar (opcional).

        Returns:
            Un nuevo MaintenancePlan con id autogenerado.

        Raises:
            MaintenancePlanNameEmptyError: Si el nombre está vacío.
            MaintenancePlanIntervalError: Si el intervalo es menor o igual a cero.
            MaintenancePlanDueDateError: Si la fecha de próxima ejecución es None.
        """
        # uuid4 asume colisión despreciable en single-node.
        # Cambiar a snowflake si el sistema escala horizontalmente.
        plan = cls(
            id=MaintenancePlanId(uuid.uuid4()),
            empresa_id=empresa_id,
            activo_id=activo_id,
            nombre=nombre.strip(),
            tipo=tipo,
            intervalo_dias=intervalo_dias,
            proxima_ejecucion=proxima_ejecucion,
            tecnico_responsable_id=tecnico_responsable_id,
            descripcion_tareas=descripcion_tareas.strip() if descripcion_tareas else None,
        )
        return plan

    def deactivate(self) -> None:
        """Desactiva el plan de mantenimiento."""
        self.activo = False

    def activate(self) -> None:
        """Activa el plan de mantenimiento."""
        self.activo = True

    def reschedule(self, new_date: date) -> None:
        """Reprograma la próxima ejecución del plan.

        Args:
            new_date: Nueva fecha de próxima ejecución.
        """
        # no valida que new_date >= hoy.
        # agregar cuando el negocio lo exija.
        self.proxima_ejecucion = new_date
