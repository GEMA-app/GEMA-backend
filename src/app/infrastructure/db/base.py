"""Clase base declarativa para todos los modelos ORM de SQLAlchemy 2.0."""

from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase


class Base(AsyncAttrs, DeclarativeBase):
    """Clase base declarativa para todos los modelos ORM de SQLAlchemy 2.0."""

    pass
