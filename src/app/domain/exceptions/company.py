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
