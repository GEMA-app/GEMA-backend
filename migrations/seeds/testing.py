# migrations/seeds/testing.py
"""Seed de pruebas: Reutiliza el seed de desarrollo para tener un entorno consistente."""

from migrations.seeds.development import seed

__all__ = ["seed"]
