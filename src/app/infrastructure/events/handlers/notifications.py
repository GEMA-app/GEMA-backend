"""Handlers de eventos de dominio que despachan notificaciones y registros de auditoría."""

import uuid
from dataclasses import fields
from typing import Any

import structlog

from app.application.ports.notifications import NotificationPort
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.entities.system_audit import SystemAudit
from app.domain.events import (
    AssetCreated,
    AssetDecommissioned,
    AssetDeleted,
    AssetLocationChanged,
    AssetMaintenanceStarted,
    AssetOutOfService,
    AssetPutInService,
    AssetUpdated,
    CompanyActivated,
    CompanyCancelled,
    CompanyCreated,
    CompanyProfileUpdated,
    CompanySuspended,
    DomainEvent,
    FailureReportCreated,
    FailureReportDeleted,
    FailureReportUpdated,
    InterventionCreated,
    InterventionDeleted,
    InterventionUpdated,
    InventoryEntryCreated,
    InventoryPartCreated,
    InventoryPartDeleted,
    InventoryPartUpdated,
    LocationCreated,
    LocationDeleted,
    LocationMoved,
    LocationUpdated,
    MaintenancePlanCreated,
    MaintenancePlanDeleted,
    MaintenancePlanUpdated,
    PasswordChanged,
    PasswordResetCompleted,
    PasswordResetInitiated,
    PlanExecutionCreated,
    PreferenceUpdated,
    RoleAssigned,
    RoleCreated,
    RoleDeleted,
    RoleRevoked,
    RoleUpdated,
    SupplierCreated,
    SupplierDeleted,
    SupplierUpdated,
    UsedPartCreated,
    UsedPartDeleted,
    UsedPartUpdated,
    UserActivated,
    UserDeactivated,
    UserLoggedIn,
    UserRegistered,
    WorkOrderCreated,
    WorkOrderDeleted,
    WorkOrderUpdated,
)
from app.domain.value_objects import CompanyId, UserId
from app.infrastructure.context import client_ip, current_user_id

logger = structlog.get_logger()


async def handle_user_registered(
    event: UserRegistered,
    notification: NotificationPort,
) -> None:
    """Despacha el email de bienvenida al usuario recién registrado.

    Args:
        event: Evento de dominio con datos del usuario registrado.
        notification: Puerto de notificaciones para enviar el correo.
    """
    logger.info(
        "handle_user_registered",
        user_id=event.user_id,
        email=event.email,
    )
    await notification.send_welcome(
        email=event.email,
        nombre=event.nombre or event.email.split("@")[0],
        company_name=event.company_name or "tu empresa",
    )


async def handle_password_changed(
    event: PasswordChanged,
    notification: NotificationPort,
    uow: UnitOfWorkPort | None = None,
) -> None:
    """Envía la alerta de seguridad cuando la contraseña ha sido cambiada.

    Args:
        event: Evento de dominio con datos del cambio de contraseña.
        notification: Puerto de notificaciones para enviar el correo.
        uow: Unit of Work opcional para persistir auditoría.
    """
    logger.info("handle_password_changed", user_id=event.user_id)
    await notification.send_password_changed(email=event.email)
    empresa_id = getattr(event, "empresa_id", None)
    if uow and empresa_id and event.user_id:
        try:
            audit = SystemAudit.create(
                empresa_id=CompanyId(value=uuid.UUID(empresa_id)),
                usuario_id=UserId(value=uuid.UUID(event.user_id)),
                accion="cambio_contrasena",
                detalles={"email": event.email},
            )
            async with uow:
                await uow.system_audits.save(audit)
                await uow.commit()
        except Exception as err:
            logger.warning("audit_log_failed", error=str(err))


async def handle_password_reset_initiated(
    event: PasswordResetInitiated,
    notification: NotificationPort,
) -> None:
    """Handler de auditoría â€” el email ya fue enviado desde el use case.

    Args:
        event: Evento de dominio con datos del restablecimiento.
        notification: Puerto de notificaciones (no se envía correo aquí).
    """
    logger.info(
        "handle_password_reset_initiated",
        user_id=event.user_id,
        email=event.email,
        msg="Email de reset enviado desde el use case (raw_token nunca persiste)",
    )


async def handle_password_reset_completed(
    event: PasswordResetCompleted,
    notification: NotificationPort,
    uow: UnitOfWorkPort | None = None,
) -> None:
    """Envía la confirmación de que la contraseña fue restablecida.

    Args:
        event: Evento de dominio con datos del restablecimiento completado.
        notification: Puerto de notificaciones para enviar el correo.
        uow: Unit of Work opcional para auditoría.
    """
    logger.info("handle_password_reset_completed", user_id=event.user_id)
    await notification.send_password_reset_confirmation(email=event.email)
    empresa_id = getattr(event, "empresa_id", None)
    if uow and empresa_id and event.user_id:
        try:
            audit = SystemAudit.create(
                empresa_id=CompanyId(value=uuid.UUID(empresa_id)),
                usuario_id=UserId(value=uuid.UUID(event.user_id)),
                accion="restablecimiento_contrasena",
                detalles={"email": event.email},
            )
            async with uow:
                await uow.system_audits.save(audit)
                await uow.commit()
        except Exception as err:
            logger.warning("audit_log_failed", error=str(err))


async def handle_user_logged_in(
    event: UserLoggedIn,
    uow: UnitOfWorkPort,
) -> None:
    """Registra el inicio de sesión en la tabla de auditoría.

    Args:
        event: Evento de dominio con datos del usuario que inició sesión.
        uow: Unit of Work para persistir el registro de auditoría.
    """
    logger.info("handle_user_logged_in", user_id=event.user_id, email=event.email)

    audit = SystemAudit.create(
        empresa_id=CompanyId(value=uuid.UUID(event.empresa_id)),
        usuario_id=UserId(value=uuid.UUID(event.user_id)),
        accion="inicio_sesion",
        detalles={"email": event.email},
    )

    async with uow:
        await uow.system_audits.save(audit)
        await uow.commit()


# Mapping genérico de eventos → acción de auditoría
# un solo handler cubre todos los módulos; si necesitas lógica
# específica por evento, extrae un handler dedicado.

_EVENT_AUDIT_MAP: dict[type[DomainEvent], str] = {
    # Auth / Usuarios
    UserRegistered: "registro_usuario",
    UserLoggedIn: "inicio_sesion",
    PasswordChanged: "cambio_contrasena",
    PasswordResetInitiated: "solicitud_reset_contrasena",
    PasswordResetCompleted: "restablecimiento_contrasena",
    RoleAssigned: "asignacion_rol",
    RoleRevoked: "revocacion_rol",
    UserDeactivated: "desactivacion_usuario",
    UserActivated: "activacion_usuario",
    # Activos
    AssetCreated: "creacion_activo",
    AssetUpdated: "actualizacion_activo",
    AssetLocationChanged: "cambio_ubicacion_activo",
    AssetMaintenanceStarted: "activo_en_mantenimiento",
    AssetDecommissioned: "baja_activo",
    AssetPutInService: "activo_en_servicio",
    AssetOutOfService: "activo_fuera_servicio",
    # Mantenimiento
    FailureReportCreated: "creacion_reporte_falla",
    # Ubicaciones
    LocationCreated: "creacion_ubicacion",
    LocationMoved: "movimiento_ubicacion",
    # Empresa / Sistema
    CompanyCreated: "creacion_empresa",
    CompanySuspended: "suspension_empresa",
    CompanyActivated: "activacion_empresa",
    CompanyCancelled: "cancelacion_empresa",
    CompanyProfileUpdated: "actualizacion_empresa",
    # Activos
    AssetDeleted: "eliminacion_activo",
    # Mantenimiento
    FailureReportUpdated: "actualizacion_reporte_falla",
    FailureReportDeleted: "eliminacion_reporte_falla",
    WorkOrderCreated: "creacion_orden_trabajo",
    WorkOrderUpdated: "actualizacion_orden_trabajo",
    WorkOrderDeleted: "eliminacion_orden_trabajo",
    MaintenancePlanCreated: "creacion_plan_mantenimiento",
    MaintenancePlanUpdated: "actualizacion_plan_mantenimiento",
    MaintenancePlanDeleted: "eliminacion_plan_mantenimiento",
    # Ubicaciones
    LocationUpdated: "actualizacion_ubicacion",
    LocationDeleted: "eliminacion_ubicacion",
    # Roles
    RoleCreated: "creacion_rol",
    RoleUpdated: "actualizacion_rol",
    RoleDeleted: "eliminacion_rol",
    # Inventario
    InventoryPartCreated: "creacion_repuesto",
    InventoryPartUpdated: "actualizacion_repuesto",
    InventoryPartDeleted: "eliminacion_repuesto",
    InventoryEntryCreated: "movimiento_inventario",
    # Proveedores
    SupplierCreated: "creacion_proveedor",
    SupplierUpdated: "actualizacion_proveedor",
    SupplierDeleted: "eliminacion_proveedor",
    # Preferencias
    PreferenceUpdated: "actualizacion_preferencias",
    InterventionCreated: "creacion_intervencion",
    InterventionUpdated: "actualizacion_intervencion",
    InterventionDeleted: "eliminacion_intervencion",
    PlanExecutionCreated: "creacion_ejecucion_plan",
    UsedPartCreated: "creacion_repuesto_usado",
    UsedPartUpdated: "actualizacion_repuesto_usado",
    UsedPartDeleted: "eliminacion_repuesto_usado",
}


_MODULE_EVENT_MAP: dict[type[DomainEvent], str] = {
    AssetCreated: "activos",
    AssetUpdated: "activos",
    AssetDecommissioned: "activos",
    AssetLocationChanged: "activos",
    AssetMaintenanceStarted: "activos",
    AssetPutInService: "activos",
    AssetOutOfService: "activos",
    FailureReportCreated: "mantenimiento",
    LocationCreated: "sistema",
    LocationMoved: "sistema",
    UserRegistered: "usuarios",
    RoleAssigned: "usuarios",
    RoleRevoked: "usuarios",
    UserDeactivated: "usuarios",
    UserActivated: "usuarios",
    CompanyCreated: "sistema",
    CompanySuspended: "sistema",
    CompanyActivated: "sistema",
    CompanyCancelled: "sistema",
    CompanyProfileUpdated: "sistema",
    AssetDeleted: "activos",
    FailureReportUpdated: "mantenimiento",
    FailureReportDeleted: "mantenimiento",
    WorkOrderCreated: "mantenimiento",
    WorkOrderUpdated: "mantenimiento",
    WorkOrderDeleted: "mantenimiento",
    MaintenancePlanCreated: "mantenimiento",
    MaintenancePlanUpdated: "mantenimiento",
    MaintenancePlanDeleted: "mantenimiento",
    LocationUpdated: "sistema",
    LocationDeleted: "sistema",
    RoleCreated: "usuarios",
    RoleUpdated: "usuarios",
    RoleDeleted: "usuarios",
    InventoryPartCreated: "inventario",
    InventoryPartUpdated: "inventario",
    InventoryPartDeleted: "inventario",
    InventoryEntryCreated: "inventario",
    SupplierCreated: "sistema",
    SupplierUpdated: "sistema",
    SupplierDeleted: "sistema",
    PreferenceUpdated: "sistema",
    InterventionCreated: "mantenimiento",
    InterventionUpdated: "mantenimiento",
    InterventionDeleted: "mantenimiento",
    PlanExecutionCreated: "mantenimiento",
    UsedPartCreated: "mantenimiento",
    UsedPartUpdated: "mantenimiento",
    UsedPartDeleted: "mantenimiento",
}

_DESCRIPTION_MAP: dict[type[DomainEvent], str] = {
    AssetCreated: "Activo creado",
    AssetUpdated: "Activo actualizado",
    AssetDecommissioned: "Activo dado de baja",
    FailureReportCreated: "Reporte de falla creado",
    UserRegistered: "Usuario registrado",
    RoleAssigned: "Rol asignado a usuario",
    CompanyCreated: "Empresa creada",
    AssetDeleted: "Activo eliminado",
    FailureReportUpdated: "Reporte de falla actualizado",
    FailureReportDeleted: "Reporte de falla eliminado",
    WorkOrderCreated: "Orden de trabajo creada",
    WorkOrderUpdated: "Orden de trabajo actualizada",
    WorkOrderDeleted: "Orden de trabajo eliminada",
    MaintenancePlanCreated: "Plan de mantenimiento creado",
    MaintenancePlanUpdated: "Plan de mantenimiento actualizado",
    MaintenancePlanDeleted: "Plan de mantenimiento eliminado",
    LocationUpdated: "Ubicación actualizada",
    LocationDeleted: "Ubicación eliminada",
    RoleCreated: "Rol creado",
    RoleUpdated: "Rol actualizado",
    RoleDeleted: "Rol eliminado",
    InventoryPartCreated: "Repuesto creado",
    InventoryPartUpdated: "Repuesto actualizado",
    InventoryPartDeleted: "Repuesto eliminado",
    InventoryEntryCreated: "Movimiento de inventario",
    SupplierCreated: "Proveedor creado",
    SupplierUpdated: "Proveedor actualizado",
    SupplierDeleted: "Proveedor eliminado",
    PreferenceUpdated: "Preferencias actualizadas",
    InterventionCreated: "Intervención creada",
    InterventionUpdated: "Intervención actualizada",
    InterventionDeleted: "Intervención eliminada",
    PlanExecutionCreated: "Ejecución de plan creada",
    UsedPartCreated: "Repuesto usado creado",
    UsedPartUpdated: "Repuesto usado actualizado",
    UsedPartDeleted: "Repuesto usado eliminado",
}


def _infer_module_from_event(event: DomainEvent) -> str | None:
    return _MODULE_EVENT_MAP.get(type(event))


def _build_description(event: DomainEvent, accion: str) -> str:
    return _DESCRIPTION_MAP.get(type(event), accion.replace("_", " "))


def _get_event_field(event: DomainEvent, field_name: str) -> str | None:
    """Intenta obtener un campo del evento de forma segura."""
    try:
        value = getattr(event, field_name, None)
        return str(value) if value else None
    except Exception:
        return None


def _build_details(event: DomainEvent) -> dict[str, Any]:
    """Extrae campos relevantes del evento como detalles de auditoría."""
    details: dict[str, Any] = {}
    skip = {"event_id", "occurred_on"}
    for f in fields(event):
        if f.name in skip:
            continue
        val = getattr(event, f.name, None)
        if val is not None:
            details[f.name] = str(val) if not isinstance(val, str | int | float | bool) else val
    return details


async def handle_generic_audit(
    event: DomainEvent,
    uow: UnitOfWorkPort,
) -> None:
    """Handler genérico de auditoría â€” crea un registro por cada evento de dominio.

    Lee user_id e IP desde contextvars (no desde el evento) para no contaminar
    la capa de dominio con concerns de infraestructura.
    """
    accion = _EVENT_AUDIT_MAP.get(type(event))
    if accion is None:
        return

    empresa_id_str = _get_event_field(event, "empresa_id")
    if not empresa_id_str:
        return

    # Leer contexto desde contextvars â€” no desde el evento de dominio
    user_id_str = current_user_id.get()
    ip = client_ip.get()

    try:
        detalles = _build_details(event)
        modulo = _infer_module_from_event(event)
        if modulo:
            detalles["modulo"] = modulo
        detalles["descripcion"] = _build_description(event, accion)

        audit = SystemAudit.create(
            empresa_id=CompanyId(value=uuid.UUID(empresa_id_str)),
            usuario_id=UserId(value=uuid.UUID(user_id_str)) if user_id_str else None,
            accion=accion,
            detalles=detalles,
            ip_address=ip,
        )
        async with uow:
            await uow.system_audits.save(audit)
            await uow.commit()
    except Exception as err:
        logger.warning("audit_log_failed", event_type=type(event).__name__, error=str(err))
