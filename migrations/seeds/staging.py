# migrations/seeds/staging.py
"""Seed de staging: Reutiliza el seed de desarrollo."""

from migrations.seeds.development import seed

__all__ = ["seed"]
