from enum import StrEnum


class CompanyStatus(StrEnum):
    """Estado del ciclo de vida de una empresa en la plataforma."""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"


class PermissionModule(StrEnum):
    """Módulos del sistema sobre los cuales se pueden definir permisos."""
    ASSETS = "assets"
    MAINTENANCE = "maintenance"
    INVENTORY = "inventory"
    REPORTS = "reports"
    ADMIN = "admin"


class AssetStatus(StrEnum):
    """Estado operativo de un activo registrado en el sistema."""
    OPERATIONAL = "operational"
    UNDER_MAINTENANCE = "under_maintenance"
    OUT_OF_SERVICE = "out_of_service"
    DECOMMISSIONED = "decommissioned"


class LocationType(StrEnum):
    """Tipo de nodo en la jerarquía de ubicaciones físicas de una empresa."""
    HEADQUARTERS = "headquarters"
    PLANT = "plant"
    AREA = "area"
    SECTION = "section"
