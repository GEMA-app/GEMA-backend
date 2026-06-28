"""Schemas JSON:API para la API v1.

Re-exporta todos los schemas de los módulos para facilitar las importaciones.
"""

from app.presentation.api.v1.schemas.interventions import (
    CreateInterventionRequest,
    InterventionDocument,
    InterventionListDocument,
    InterventionResource,
    UpdateInterventionRequest,
)

__all__ = [
    "CreateInterventionRequest",
    "InterventionDocument",
    "InterventionListDocument",
    "InterventionResource",
    "UpdateInterventionRequest",
]
