"""Enumeraciones del dominio de GEMA. Define los estados, tipos y módulos del sistema."""

from enum import StrEnum


class CompanyStatus(StrEnum):
    """Estado del ciclo de vida de una empresa en la plataforma."""

    ACTIVE = "activa"
    SUSPENDED = "suspendida"
    CANCELLED = "cancelada"


class PermissionModule(StrEnum):
    """Módulos del sistema sobre los cuales se pueden definir permisos."""

    ASSETS = "activos"
    MAINTENANCE = "mantenimiento"
    INVENTORY = "inventario"
    REPORTS = "reportes"
    ADMIN = "administracion"
    PREFERENCES = "preferencias"
    SYSTEM_AUDIT = "system_audit"


class AssetStatus(StrEnum):
    """Estado operativo de un activo registrado en el sistema."""

    OPERATIONAL = "operativo"
    UNDER_MAINTENANCE = "en_mantenimiento"
    OUT_OF_SERVICE = "fuera_de_servicio"
    DECOMMISSIONED = "dado_de_baja"


class LocationType(StrEnum):
    """Tipo de nodo en la jerarquía de ubicaciones físicas de una empresa."""

    HEADQUARTERS = "sede"
    PLANT = "planta"
    AREA = "area"
    SECTION = "seccion"


class MaintenanceType(StrEnum):
    """Tipo de mantenimiento a realizar en un activo."""

    PREVENTIVE = "preventivo"
    CORRECTIVE = "correctivo"
    PREDICTIVE = "predictivo"


class WorkOrderStatus(StrEnum):
    """Estado de una orden de trabajo."""

    OPEN = "abierta"
    IN_PROGRESS = "en_proceso"
    PAUSED = "pausada"
    CLOSED = "cerrada"
    CANCELLED = "cancelada"


class PriorityLevel(StrEnum):
    """Nivel de prioridad de un reporte de falla o tarea."""

    CRITICAL = "critica"
    HIGH = "alta"
    MEDIUM = "media"
    LOW = "baja"


class ReportStatus(StrEnum):
    """Estado de procesamiento de un reporte de fallas."""

    PENDING = "pendiente"
    IN_PROGRESS = "en_proceso"
    RESOLVED = "atendido"
    DISCARDED = "descartado"


class Theme(StrEnum):
    """Tema visual de la interfaz de usuario."""

    DARK = "oscuro"
    LIGHT = "claro"
    SYSTEM = "sistema"
