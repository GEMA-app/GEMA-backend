from pydantic import BaseModel, EmailStr

class SupplierCreate(BaseModel):
    nombre: str
    rif: str
    telefono: str
    email: EmailStr  # Pydantic validará automáticamente que sea un email real
    contacto: str