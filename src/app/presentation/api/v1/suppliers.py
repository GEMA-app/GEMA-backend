from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

# Importamos las piezas que construiste
from app.application.use_cases.create_supplier import CreateSupplierUseCase
from app.infrastructure.repositories.supplier_repository import SqlAlchemySupplierRepository
from app.presentation.schemas.supplier import SupplierCreate
from app.infrastructure.db.session import get_db

router = APIRouter(prefix="/proveedores", tags=["Proveedores"])

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_supplier(
    data: SupplierCreate, 
    db: AsyncSession = Depends(get_db)
):
    # 1. Instanciamos el repositorio y el caso de uso
    repo = SqlAlchemySupplierRepository(db)
    use_case = CreateSupplierUseCase(repo)
    
    # 2. Ejecutamos la lógica
    new_supplier = await use_case.execute(
        empresa_id=UUID(data.empresa_id),
        nombre=data.nombre,
        rif=data.rif,
        telefono=data.telefono,
        email=data.email,
        contacto=data.contacto
    )
    
    return {"message": "Proveedor creado con éxito", "id": new_supplier.id}