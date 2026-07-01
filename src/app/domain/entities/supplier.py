"""Entidad de dominio Supplier (Proveedor)."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.exceptions.base import ValidationError

_NAME_MAX_LENGTH = 150
_RIF_MAX_LENGTH = 20
_PHONE_MAX_LENGTH = 30
_EMAIL_MAX_LENGTH = 100
_CONTACT_MAX_LENGTH = 100


@dataclass
class Supplier:
    """Entidad que representa un proveedor registrado en la empresa.

    Protege las invariantes: nombre obligatorio (1-150 caracteres),
    RIF opcional con máximo 20 caracteres, email y teléfono opcionales.
    """

    id: UUID
    empresa_id: UUID
    name: str
    rif: str | None
    phone: str | None
    email: str | None
    contact: str | None
    version: int
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @classmethod
    def create(
        cls,
        id: UUID,
        empresa_id: UUID,
        name: str,
        rif: str | None = None,
        phone: str | None = None,
        email: str | None = None,
        contact: str | None = None,
    ) -> "Supplier":
        """Crea un nuevo proveedor validando invariantes de negocio.

        Args:
            id: Identificador único UUID del proveedor.
            empresa_id: Identificador UUID del tenant propietario.
            name: Nombre del proveedor (entre 1 y {_NAME_MAX_LENGTH} caracteres).
            rif: RIF del proveedor (máximo {_RIF_MAX_LENGTH} caracteres).
            phone: Teléfono de contacto (máximo {_PHONE_MAX_LENGTH} caracteres).
            email: Correo electrónico (máximo {_EMAIL_MAX_LENGTH} caracteres).
            contact: Nombre de la persona de contacto (máximo {_CONTACT_MAX_LENGTH} caracteres).

        Returns:
            Una nueva instancia de Supplier con las invariantes validadas.

        Raises:
            ValidationError: Si el nombre está vacío o excede la longitud máxima.
        """
        if not name or len(name.strip()) == 0:
            raise ValidationError("El nombre del proveedor es obligatorio.")
        if len(name) > _NAME_MAX_LENGTH:
            raise ValidationError(f"El nombre no puede exceder los {_NAME_MAX_LENGTH} caracteres.")
        if rif and len(rif) > _RIF_MAX_LENGTH:
            raise ValidationError(f"El RIF no puede exceder los {_RIF_MAX_LENGTH} caracteres.")
        if phone and len(phone) > _PHONE_MAX_LENGTH:
            raise ValidationError(
                f"El teléfono no puede exceder los {_PHONE_MAX_LENGTH} caracteres."
            )
        if email and len(email) > _EMAIL_MAX_LENGTH:
            raise ValidationError(f"El email no puede exceder los {_EMAIL_MAX_LENGTH} caracteres.")
        if contact and len(contact) > _CONTACT_MAX_LENGTH:
            raise ValidationError(
                f"El contacto no puede exceder los {_CONTACT_MAX_LENGTH} caracteres."
            )
        return cls(
            id=id,
            empresa_id=empresa_id,
            name=name.strip(),
            rif=rif.strip() if rif else None,
            phone=phone.strip() if phone else None,
            email=email.strip() if email else None,
            contact=contact.strip() if contact else None,
            version=1,
        )

    def update(
        self,
        name: str | None = None,
        rif: str | None = None,
        phone: str | None = None,
        email: str | None = None,
        contact: str | None = None,
    ) -> None:
        """Actualiza los datos del proveedor validando las invariantes.

        Args:
            name: Nuevo nombre del proveedor.
            rif: Nuevo RIF.
            phone: Nuevo teléfono.
            email: Nuevo email.
            contact: Nueva persona de contacto.

        Raises:
            ValidationError: Si algún campo excede la longitud máxima.
        """
        if name is not None:
            if not name.strip():
                raise ValidationError("El nombre del proveedor es obligatorio.")
            if len(name) > _NAME_MAX_LENGTH:
                raise ValidationError(
                    f"El nombre no puede exceder los {_NAME_MAX_LENGTH} caracteres."
                )
            self.name = name.strip()

        if rif is not None:
            if len(rif) > _RIF_MAX_LENGTH:
                raise ValidationError(f"El RIF no puede exceder los {_RIF_MAX_LENGTH} caracteres.")
            self.rif = rif.strip() if rif else None

        if phone is not None:
            if len(phone) > _PHONE_MAX_LENGTH:
                raise ValidationError(
                    f"El teléfono no puede exceder los {_PHONE_MAX_LENGTH} caracteres."
                )
            self.phone = phone.strip() if phone else None

        if email is not None:
            if len(email) > _EMAIL_MAX_LENGTH:
                raise ValidationError(
                    f"El email no puede exceder los {_EMAIL_MAX_LENGTH} caracteres."
                )
            self.email = email.strip() if email else None

        if contact is not None:
            if len(contact) > _CONTACT_MAX_LENGTH:
                raise ValidationError(
                    f"El contacto no puede exceder los {_CONTACT_MAX_LENGTH} caracteres."
                )
            self.contact = contact.strip() if contact else None
