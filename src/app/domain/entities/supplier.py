"""Entidad de dominio Supplier (Proveedor)."""

import re
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.exceptions.base import ValidationError
from app.domain.exceptions.supplier import InvalidRifError

_NAME_MAX_LENGTH = 150
_RIF_MAX_LENGTH = 20
_PHONE_MAX_LENGTH = 30
_EMAIL_MAX_LENGTH = 100
_CONTACT_MAX_LENGTH = 100
_DIRECCION_MAX_LENGTH = 255
_RIF_PATTERN = re.compile(r"^[JGVEPjgivep]-\d{8}-\d$", re.IGNORECASE)


@dataclass
class Supplier:
    """Entidad que representa un proveedor registrado en la empresa.

    Protege las invariantes: nombre obligatorio (1-150 caracteres),
    RIF opcional con máximo 20 caracteres y formato venezolano,
    email, teléfono y dirección opcionales.
    """

    id: UUID
    empresa_id: UUID
    name: str
    rif: str | None
    phone: str | None
    email: str | None
    contact: str | None
    version: int
    is_active: bool = True
    direccion: str | None = None
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
        is_active: bool = True,
        direccion: str | None = None,
    ) -> "Supplier":
        """Crea un nuevo proveedor validando invariantes de negocio."""
        if not name or len(name.strip()) == 0:
            raise ValidationError("El nombre del proveedor es obligatorio.")
        if len(name) > _NAME_MAX_LENGTH:
            raise ValidationError(f"El nombre no puede exceder los {_NAME_MAX_LENGTH} caracteres.")
        if rif:
            rif_clean = rif.strip()
            if len(rif_clean) > _RIF_MAX_LENGTH:
                raise ValidationError(f"El RIF no puede exceder los {_RIF_MAX_LENGTH} caracteres.")
            if not _RIF_PATTERN.match(rif_clean):
                raise InvalidRifError(
                    f"RIF '{rif_clean}' no tiene formato venezolano válido (ej: J-12345678-9)."
                )
        else:
            rif_clean = None
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
        if direccion and len(direccion) > _DIRECCION_MAX_LENGTH:
            raise ValidationError(
                f"La dirección no puede exceder los {_DIRECCION_MAX_LENGTH} caracteres."
            )
        return cls(
            id=id,
            empresa_id=empresa_id,
            name=name.strip(),
            rif=rif_clean,
            phone=phone.strip() if phone else None,
            email=email.strip() if email else None,
            contact=contact.strip() if contact else None,
            is_active=is_active,
            direccion=direccion.strip() if direccion else None,
            version=1,
        )

    def update(
        self,
        name: str | None = None,
        rif: str | None = None,
        phone: str | None = None,
        email: str | None = None,
        contact: str | None = None,
        is_active: bool | None = None,
        direccion: str | None = None,
    ) -> None:
        """Actualiza los datos del proveedor validando las invariantes."""
        if name is not None:
            if not name.strip():
                raise ValidationError("El nombre del proveedor es obligatorio.")
            if len(name) > _NAME_MAX_LENGTH:
                raise ValidationError(
                    f"El nombre no puede exceder los {_NAME_MAX_LENGTH} caracteres."
                )
            self.name = name.strip()

        if rif is not None:
            rif_clean = rif.strip() if rif else None
            if rif_clean:
                if len(rif_clean) > _RIF_MAX_LENGTH:
                    raise ValidationError(
                        f"El RIF no puede exceder los {_RIF_MAX_LENGTH} caracteres."
                    )
                if not _RIF_PATTERN.match(rif_clean):
                    raise InvalidRifError(
                        f"RIF '{rif_clean}' no tiene formato venezolano válido (ej: J-12345678-9)."
                    )
            self.rif = rif_clean

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

        if is_active is not None:
            self.is_active = is_active

        if direccion is not None:
            if len(direccion) > _DIRECCION_MAX_LENGTH:
                raise ValidationError(
                    f"La dirección no puede exceder los {_DIRECCION_MAX_LENGTH} caracteres."
                )
            self.direccion = direccion.strip() if direccion else None

