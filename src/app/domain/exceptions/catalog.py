"""Excepciones de dominio para el módulo de catálogo (artículos y categorías)."""

from app.domain.exceptions.base import DomainException


class CatalogArticleException(DomainException):
    """Base para excepciones de artículos de catálogo."""


class CatalogArticleNotFoundError(CatalogArticleException):
    """El artículo de catálogo solicitado no existe."""

    def __init__(self, article_id: str = "") -> None:
        msg = (
            f"Artículo de catálogo no encontrado: {article_id}"
            if article_id
            else "Artículo de catálogo no encontrado."
        )
        super().__init__(msg)


class EmptyCatalogArticleNameError(CatalogArticleException):
    """El nombre del artículo de catálogo no puede estar vacío."""

    def __init__(self) -> None:
        super().__init__("El nombre del artículo de catálogo no puede estar vacío.")


class EmptyCatalogArticleCodeError(CatalogArticleException):
    """El código del artículo de catálogo no puede estar vacío."""

    def __init__(self) -> None:
        super().__init__("El código del artículo de catálogo no puede estar vacío.")


class CatalogArticleHasAssetsError(CatalogArticleException):
    """El artículo de catálogo tiene activos vinculados y no puede eliminarse."""

    def __init__(self, article_id: str = "") -> None:
        msg = (
            f"El artículo de catálogo {article_id} tiene activos vinculados."
            if article_id
            else "El artículo de catálogo tiene activos vinculados."
        )
        super().__init__(msg)
