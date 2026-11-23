# Todo lo que lee o escribe archivos va en un archivo separado llamado datos.py para que main.py siga corto y prolijo.
# Siempre abrimos archivos con with porque Python los cierra automáticamente al terminar el bloque, incluso si ocurre un error.
# Y siempre ponemos encoding="utf-8" para que en Windows las tildes y la ñ no se guarden como símbolos raros.

import json
from pathlib import Path

CARPETA_DATOS = (
    Path(__file__).parent / "datos"
)  # obtenemos siempre la carpeta exacta donde vive tu código .py
RUTA_ARCHIVO = CARPETA_DATOS / "libros.json"


def cargar():
    try:
        with open(RUTA_ARCHIVO, "r", encoding="utf-8") as archivo:
            datos = json.load(
                archivo
            )  # lee el archivo y te devuelve la lista de Python
            if isinstance(datos, list):
                return datos
            return []
    except (FileNotFoundError, json.JSONDecodeError):
        return []
    # Si el archivo todavía no existe lanza FileNotFoundError, y si está vacío o tiene un JSON roto lanza json.JSONDecodeError.
    # Al atrapar ambos con try / except, devolvemos [] y la API arranca limpia sin caerse.


def guardar(libros):
    CARPETA_DATOS.mkdir(
        exist_ok=True
    )  # crea la carpeta datos/ si no existe y no da error si ya existe.
    with open(RUTA_ARCHIVO, "w", encoding="utf-8") as archivo:
        json.dump(libros, archivo, indent=2, ensure_ascii=False)


# Uso el modo "w" a propósito, porque cada vez que cambia algo quiero reescribir el archivo completo con la lista actualizada
# json.dump pasa una lista o diccionario de Python al archivo (con indent=2 para que se lea lindo y ensure_ascii=False para respetar las tildes)


def calcular_proximo_id(libros):
    if not libros:
        return 1
    return max(libro["id"] for libro in libros) + 1
