from fastapi import FastAPI

app = FastAPI()


@app.get("/")
# es un decorador, le pega una etiqueta a la función diciendo: 
# "cuando llegue un pedido GET a la ruta /, ejecutá inicio()".

def inicio():
    return {"mensaje": "API de la biblioteca"}