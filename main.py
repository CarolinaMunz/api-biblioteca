import logging

from fastapi import FastAPI, HTTPException

from datos import calcular_proximo_id, cargar, guardar
from schemas import Libro, LibroConId, LibroParcial

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI()

libros = cargar()
proximo_id = calcular_proximo_id(libros)


def buscar_libro(id: int):
    """Devuelve el libro con ese id o lanza 404 si no existe."""
    for libro in libros:
        if libro["id"] == id:
            return libro
    logger.warning("Libro %s no existe", id)
    raise HTTPException(
        status_code=404,
        detail=f"No existe el libro con id {id}",
    )


def existe_libro(titulo: str, autor: str):
    """Devuelve True si ya existe un libro con el mismo título y autor."""
    titulo_buscado = titulo.strip().lower()
    autor_buscado = autor.strip().lower()
    return any(
        libro["titulo"].strip().lower() == titulo_buscado
        and libro["autor"].strip().lower() == autor_buscado
        for libro in libros
    )


@app.get("/")
def inicio():
    """Devuelve el mensaje de bienvenida de la API."""
    return {"mensaje": "API de la biblioteca"}


@app.get("/libros", response_model=list[LibroConId])
def listar_libros(
    autor: str | None = None,
    disponible: bool | None = None,
    desde: int = 0,
    limite: int = 100,
):
    """Lista los libros con filtros opcionales por autor y disponibilidad."""
    resultado = libros
    if autor is not None:
        autor_buscado = autor.strip().lower()
        resultado = [
            libro
            for libro in resultado
            if libro["autor"].strip().lower() == autor_buscado
        ]
    if disponible is not None:
        resultado = [libro for libro in resultado if libro["disponible"] == disponible]
    return resultado[desde : desde + limite]


@app.get("/libros/buscar", response_model=list[LibroConId])
def buscar_libros(texto: str):
    """Busca libros cuyo título o autor contenga el texto indicado."""
    buscado = texto.lower()
    return [
        libro
        for libro in libros
        if buscado in libro["titulo"].lower() or buscado in libro["autor"].lower()
    ]


@app.get("/libros/estadisticas")
def obtener_estadisticas():
    """Devuelve el total de libros, los disponibles y los prestados."""
    total = len(libros)
    disponibles = sum(1 for libro in libros if libro["disponible"])
    prestados = total - disponibles
    return {
        "total": total,
        "disponibles": disponibles,
        "prestados": prestados,
    }


@app.post("/libros", status_code=201, response_model=LibroConId)
def crear_libro(libro: Libro):
    """Crea un libro nuevo, le asigna id y lo guarda en disco."""
    global proximo_id
    if existe_libro(libro.titulo, libro.autor):
        logger.warning("Intento de crear libro duplicado: %s", libro.titulo)
        raise HTTPException(status_code=409, detail="El libro ya existe")
    nuevo = {"id": proximo_id, **libro.model_dump()}
    proximo_id += 1
    libros.append(nuevo)
    guardar(libros)
    logger.info("Libro %s creado", nuevo["id"])
    return nuevo


@app.get("/libros/{id}", response_model=LibroConId)
def obtener_libro(id: int):
    """Devuelve un libro puntual por su id."""
    return buscar_libro(id)


@app.put("/libros/{id}", response_model=LibroConId)
def reemplazar_libro(id: int, datos: Libro):
    """Reemplaza todos los campos de un libro existente."""
    libro = buscar_libro(id)
    libro.update(datos.model_dump())
    guardar(libros)
    logger.info("Libro %s reemplazado", id)
    return libro


@app.patch("/libros/{id}", response_model=LibroConId)
def actualizar_parcial(id: int, datos: LibroParcial):
    """Actualiza solo los campos enviados de un libro existente."""
    libro = buscar_libro(id)
    cambios = datos.model_dump(exclude_unset=True)
    libro.update(cambios)
    guardar(libros)
    logger.info("Libro %s actualizado parcialmente", id)
    return libro


@app.delete("/libros/{id}", status_code=204)
def borrar_libro(id: int):
    """Elimina un libro por su id sin devolver contenido."""
    libro = buscar_libro(id)
    libros.remove(libro)
    guardar(libros)
    logger.info("Libro %s eliminado", id)


@app.post("/libros/{id}/prestar", response_model=LibroConId)
def prestar_libro(id: int):
    """Marca un libro como prestado (disponible en False)."""
    libro = buscar_libro(id)
    if not libro["disponible"]:
        logger.warning("Libro %s ya estaba prestado", id)
        raise HTTPException(status_code=409, detail="El libro ya está prestado")
    libro["disponible"] = False
    guardar(libros)
    logger.info("Libro %s prestado", id)
    return libro


@app.post("/libros/{id}/devolver", response_model=LibroConId)
def devolver_libro(id: int):
    """Marca un libro como devuelto (disponible en True)."""
    libro = buscar_libro(id)
    if libro["disponible"]:
        logger.warning("Libro %s ya estaba disponible", id)
        raise HTTPException(
            status_code=409,
            detail="El libro ya está disponible",
        )
    libro["disponible"] = True
    guardar(libros)
    logger.info("Libro %s devuelto", id)
    return libro
