from pydantic import BaseModel, Field


class Libro(BaseModel):
    titulo: str = Field(min_length=3, max_length=100)
    autor: str = Field(min_length=3, max_length=60)
    anio: int = Field(ge=1000, le=2100)
    disponible: bool = True

# LibroConId(Libro) hereda los 4 campos de Libro y le agrega id: int
class LibroConId(Libro):
    id: int