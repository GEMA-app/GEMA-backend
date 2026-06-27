"""Re-exporta todas las entidades del dominio para imports planos."""

from app.domain.entities.asset import Asset
from app.domain.entities.catalog import ArticleCategory, CatalogArticle
from app.domain.entities.company import Company
from app.domain.entities.location import Location
from app.domain.entities.permission import Permission
from app.domain.entities.plan_execution import PlanExecution
from app.domain.entities.preference import UserPreference
from app.domain.entities.role import Role
from app.domain.entities.user import User

__all__ = [
    "User",
    "Company",
    "Role",
    "Permission",
    "Location",
    "PlanExecution",
    "Asset",
    "ArticleCategory",
    "CatalogArticle",
    "UserPreference",
]
