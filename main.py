from fastapi import FastAPI
from schemas import Libro, LibroConId

app = FastAPI()

libros = []
proximo_id = 1

@app.get("/")
# es un decorador, le pega una etiqueta a la función diciendo: 
# "cuando llegue un pedido GET a la ruta /, ejecutá inicio()".
def inicio():
    return {"mensaje": "API de la biblioteca"}

@app.get("/libros", response_model=list[LibroConId])
def listar_libros():
    return libros


@app.post("/libros", status_code=201, response_model=LibroConId)
def crear_libro(libro: Libro):
    global proximo_id
    nuevo = {"id": proximo_id, **libro.model_dump()}
    proximo_id += 1
    libros.append(nuevo)
    return nuevo