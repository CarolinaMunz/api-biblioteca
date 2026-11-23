from pydantic import BaseModel, Field
from typing import Optional

class Libro(BaseModel):
    titulo: str = Field(min_length=3, max_length=100)
    autor: str = Field(min_length=3, max_length=60)
    anio: int = Field(ge=1000, le=2100)
    disponible: bool = True

# LibroConId(Libro) hereda los 4 campos de Libro y le agrega id: int
class LibroConId(Libro):
    id: int

# modelo nuevo para PATCH donde todos los campos sean opcionales con valor por defecto None.
class LibroParcial(BaseModel):
    titulo: Optional[str] = Field(default=None, min_length=3, max_length=100)
    autor: Optional[str] = Field(default=None, min_length=3, max_length=60)
    anio: Optional[int] = Field(default=None, ge=1000, le=2100)
    disponible: Optional[bool] = None