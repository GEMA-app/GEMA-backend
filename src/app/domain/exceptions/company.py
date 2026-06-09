"""Excepciones del módulo de empresas (no encontrada, slug duplicado, nombre vacío)."""

from app.domain.exceptions.base import DomainException


class CompanyException(DomainException):
    """Clase base para excepciones del módulo de empresas."""

    pass


class CompanyNotFoundError(CompanyException):
    """Lanzada cuando una empresa no es encontrada."""

    pass


class CompanySlugExistsError(CompanyException):
    """Lanzada cuando se intenta crear o actualizar una empresa con un slug que ya existe."""

    pass


class EmptyCompanyNameError(CompanyException):
    """Se lanza cuando el nombre de una empresa está vacío."""

    pass


class CompanyAlreadyCancelledError(CompanyException):
    """Lanzada cuando se intenta suspender una empresa ya cancelada."""

    pass


class CompanyNotSuspendedError(CompanyException):
    """Lanzada cuando se intenta reactivar una empresa que no está suspendida."""

    pass
