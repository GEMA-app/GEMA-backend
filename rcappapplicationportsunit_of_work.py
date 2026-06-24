[1mdiff --git a/src/app/application/ports/unit_of_work.py b/src/app/application/ports/unit_of_work.py[m
[1mindex 9698cf8..7c56876 100644[m
[1m--- a/src/app/application/ports/unit_of_work.py[m
[1m+++ b/src/app/application/ports/unit_of_work.py[m
[36m@@ -1,6 +1,7 @@[m
 from typing import Any, Protocol, Self[m
 [m
 from app.application.ports.asset_repository import AssetRepositoryPort[m
[32m+[m[32mfrom app.application.ports.catalog_repository import CatalogArticleRepositoryPort[m
 from app.application.ports.company_repository import CompanyRepositoryPort[m
 from app.application.ports.event_bus import EventBusPort[m
 from app.application.ports.location_repository import LocationRepositoryPort[m
[36m@@ -16,6 +17,7 @@[m [mclass UnitOfWorkPort(Protocol):[m
     companies: CompanyRepositoryPort[m
     roles: RoleRepositoryPort[m
     assets: AssetRepositoryPort[m
[32m+[m[32m    catalog_articles: CatalogArticleRepositoryPort[m
     locations: LocationRepositoryPort[m
     event_bus: EventBusPort[m
     preferences: PreferenceRepositoryPort[m
