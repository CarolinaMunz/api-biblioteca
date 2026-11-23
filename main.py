from fastapi import FastAPI, HTTPException
from schemas import Libro, LibroConId

app = FastAPI()

libros = []
proximo_id = 1

#Tanto GET /libros/{id}, DELETE, PUT y PATCH necesitan buscar un libro y lanzar 404 si no existe.
def buscar_libro(id: int):
    for libro in libros:
        if libro["id"] == id:
            return libro
    raise HTTPException(status_code=404, detail=f"No existe el libro con id {id}")

@app.get("/")
# es un decorador, le pega una etiqueta a la función diciendo: 
# "cuando llegue un pedido GET a la ruta /, ejecutá inicio()".
def inicio():
    return {"mensaje": "API de la biblioteca"}

@app.get("/libros", response_model=list[LibroConId])
def listar_libros():
    return libros


@app.post("/libros", status_code=201, response_model=LibroConId)
#le dije a FastAPI qué forma exacta tiene la respuesta y lo documenta en /docs.
def crear_libro(libro: Libro):
    global proximo_id
    nuevo = {"id": proximo_id, **libro.model_dump()}
    # model_dump() convierte el objeto de Pydantic en un diccionario común de Python
    # ** "desarma" ese diccionario adentro de otro nuevo para pegarle el "id"
    proximo_id += 1
    libros.append(nuevo)
    return nuevo

@app.get("/libros/{id}", response_model=LibroConId)
def obtener_libro(id: int):
    return buscar_libro(id)

#borra el libro y devuelve 204 sin cuerpo (y si ese ID no existe, devuelve 404).
@app.delete("/libros/{id}", status_code=204)
def borrar_libro(id: int):
    libro = buscar_libro(id)
    libros.remove(libro)