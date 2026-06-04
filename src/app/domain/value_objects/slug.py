import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Slug:
    """Objeto de valor que representa un identificador URL-friendly para una empresa.

    Formato válido: solo letras minúsculas, dígitos y guiones (a-z, 0-9, -).
    No puede comenzar ni terminar con guión. Longitud entre 2 y 63 caracteres.
    """

    value: str

    _PATTERN = re.compile(r"^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$")

    def __post_init__(self) -> None:
        if not self.value or not isinstance(self.value, str):
            raise ValueError("El slug no puede estar vacío.")
        if not self._PATTERN.match(self.value):
            raise ValueError(
                f"El slug '{self.value}' tiene un formato inválido. "
                "Solo se permiten letras minúsculas, dígitos y guiones, "
                "sin comenzar ni terminar con guión."
            )

    @classmethod
    def from_name(cls, name: str) -> "Slug":
        """Genera un slug a partir de un nombre de empresa."""
        import unicodedata

        # Normalizar unicode y eliminar acentos
        normalized = unicodedata.normalize("NFD", name.lower())
        ascii_name = "".join(c for c in normalized if unicodedata.category(c) != "Mn")
        # Reemplazar espacios y caracteres no válidos por guiones
        slug = re.sub(r"[^a-z0-9]+", "-", ascii_name).strip("-")
        return cls(value=slug[:63] if slug else "empresa")
