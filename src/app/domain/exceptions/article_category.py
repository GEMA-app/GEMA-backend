"""Excepciones de dominio para el módulo de Categorías de Artículos."""

from app.domain.exceptions.base import DomainException


class ArticleCategoryException(DomainException):
    """Clase base para excepciones del módulo de categorías de artículos."""
    pass

class ArticleCategoryNotFoundError(ArticleCategoryException):
    """Lanzada cuando no se encuentra la categoría solicitada."""
    pass

class ArticleCategoryNameExistsError(ArticleCategoryException):
    """Lanzada cuando ya existe una categoría con el mismo nombre en la empresa."""
    pass
