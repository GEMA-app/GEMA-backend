from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.domain.entities.supplier import Supplier
from app.domain.ports.supplier_repository import SupplierRepository
from app.infrastructure.db.models.supplier import SupplierModel

class SqlAlchemySupplierRepository(SupplierRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_rif(self, empresa_id: UUID, rif: str) -> Supplier | None:
        query = select(SupplierModel).where(
            SupplierModel.empresa_id == empresa_id,
            SupplierModel.rif == rif
        )
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        
        if not model:
            return None
            
        return Supplier(
            id=model.id,
            empresa_id=model.empresa_id,
            nombre=model.nombre,
            rif=model.rif,
            telefono=model.telefono,
            email=model.email,
            contacto=model.contacto
        )

    async def save(self, supplier: Supplier) -> None:
        model = SupplierModel(
            id=supplier.id,
            empresa_id=supplier.empresa_id,
            nombre=supplier.nombre,
            rif=supplier.rif,
            telefono=supplier.telefono,
            email=supplier.email,
            contacto=supplier.contacto
        )
        self.session.add(model)
        # El commit usualmente se maneja en el UoW (Unit of Work) en GEMA, 
        # pero para simplificar, si GEMA maneja transacciones en el UoW, 
        # puedes quitar el commit aquí.
        await self.session.commit()