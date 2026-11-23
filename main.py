from fastapi import FastAPI, HTTPException
from schemas import Libro, LibroConId, LibroParcial
from datos import calcular_proximo_id, cargar, guardar

app = FastAPI()

libros = cargar()
proximo_id = calcular_proximo_id(libros)

#Tanto GET /libros/{id}, DELETE, PUT y PATCH necesitan buscar un libro y lanzar 404 si no existe.
def buscar_libro(id: int):
    for libro in libros:
        if libro["id"] == id:
            return libro
    raise HTTPException(status_code=404, detail=f"No existe el libro con id {id}")


def existe_libro(titulo: str, autor: str):
    titulo_buscado = titulo.strip().lower()
    autor_buscado = autor.strip().lower()
    return any(
        libro["titulo"].strip().lower() == titulo_buscado
        and libro["autor"].strip().lower() == autor_buscado
        for libro in libros
    )
#Para ignorar mayúsculas, minúsculas y espacios de más, 
#comparé usando .strip().lower() en ambos lados.


@app.get("/")
# es un decorador, le pega una etiqueta a la función diciendo: 
# "cuando llegue un pedido GET a la ruta /, ejecutá inicio()".
def inicio():
    return {"mensaje": "API de la biblioteca"}


#En GET /libros, primero filtramos la lista y recién al final 
# aplicamos el corte con slicing (resultado[desde : desde + limite])
@app.get("/libros", response_model=list[LibroConId])
def listar_libros(
    #Al poner un valor por defecto es opcional:
    autor: str | None = None,
    disponible: bool | None = None,
    desde: int = 0,
    limite: int = 100,
):
    resultado = libros
    if autor is not None:
        autor_buscado = autor.strip().lower()
        resultado = [
            libro for libro in resultado
            if libro["autor"].strip().lower() == autor_buscado
        ]
    if disponible is not None:
        #if disponible is not None: (y no if disponible:), 
        # porque si el cliente pide ?disponible=false, False también es un filtro válido.
        resultado = [
            libro for libro in resultado
            if libro["disponible"] == disponible
        ]
    return resultado[desde : desde + limite]


#Regla fija: las rutas fijas como /libros/buscar van siempre arriba de /libros/{id}.
@app.get("/libros/buscar", response_model=list[LibroConId])
def buscar_libros(texto: str): #Al no poner valor por defecto es obligatorio
    buscado = texto.lower()
    return [
        libro for libro in libros
        if buscado in libro["titulo"].lower() or buscado in libro["autor"].lower()
    ]

# /libros/estadisticas es una ruta fija, así que tiene que ir declarada arriba de /libros/{id}. 
# Si la pongo abajo, FastAPI intenta convertir "estadisticas" a int y devuelve 422.
@app.get("/libros/estadisticas")
def obtener_estadisticas():
    total = len(libros)
    disponibles = sum(1 for libro in libros if libro["disponible"])
    prestados = total - disponibles
    return {
        "total": total,
        "disponibles": disponibles,
        "prestados": prestados,
    }


@app.post("/libros", status_code=201, response_model=LibroConId)
#le dije a FastAPI qué forma exacta tiene la respuesta y lo documenta en /docs.
def crear_libro(libro: Libro):
    global proximo_id

    #Cuando el JSON choca con algo que ya existe en tu sistema, se lanza HTTPException(409, ...):
    if existe_libro(libro.titulo, libro.autor):
        raise HTTPException(status_code=409, detail="El libro ya existe")

    nuevo = {"id": proximo_id, **libro.model_dump()}
    # model_dump() convierte el objeto de Pydantic en un diccionario común de Python
    # ** "desarma" ese diccionario adentro de otro nuevo para pegarle el "id"
    proximo_id += 1
    libros.append(nuevo)
    guardar(libros)
    return nuevo


@app.get("/libros/{id}", response_model=LibroConId)
def obtener_libro(id: int):
    return buscar_libro(id)


#PUT reemplaza todos los campos del libro con los enviados, mantiene el mismo id y devuelve 200.
@app.put("/libros/{id}", response_model=LibroConId)
def reemplazar_libro(id: int, datos: Libro):
    libro = buscar_libro(id)
    libro.update(datos.model_dump())
    guardar(libros)
    return libro


# actualiza solo los campos enviados y deja el resto igual, devolviendo 200 con el libro completo. 
# Un cuerpo vacío {} devuelve 200 sin cambios.
@app.patch("/libros/{id}", response_model=LibroConId)
def actualizar_parcial(id: int, datos: LibroParcial):
    libro = buscar_libro(id)
    cambios = datos.model_dump(exclude_unset=True)
    #Pydantic te devuelve únicamente los campos que el cliente realmente mandó en el JSON.
    libro.update(cambios)
    #actualiza únicamente las claves que vienen en cambios y deja el resto como estaba.
    guardar(libros)
    return libro


#borra el libro y devuelve 204 sin cuerpo (y si ese ID no existe, devuelve 404).
@app.delete("/libros/{id}", status_code=204)
def borrar_libro(id: int):
    libro = buscar_libro(id)
    libros.remove(libro)
    guardar(libros)


@app.post("/libros/{id}/prestar", response_model=LibroConId)
def prestar_libro(id: int):
    libro = buscar_libro(id)
    if not libro["disponible"]:
        raise HTTPException(status_code=409, detail="El libro ya está prestado")
    #Igual que con los duplicados, no podés prestar un libro que ya está prestado.
    libro["disponible"] = False
    guardar(libros)
    return libro


@app.post("/libros/{id}/devolver", response_model=LibroConId)
def devolver_libro(id: int):
    libro = buscar_libro(id)
    if libro["disponible"]:
        raise HTTPException(status_code=409, detail="El libro ya está disponible")
    libro["disponible"] = True
    guardar(libros)
    return libro