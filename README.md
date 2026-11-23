# API de la Biblioteca

API REST desarrollada con FastAPI para gestionar los libros de una biblioteca.
Permite crear, listar, buscar, filtrar, paginar, actualizar, prestar, devolver y eliminar libros con persistencia en archivo JSON.

## Instalación

1. Clonar el repositorio y entrar a la carpeta del proyecto:

```bash
git clone [https://github.com/CarolinaMunz/api-biblioteca.git](https://github.com/CarolinaMunz/api-biblioteca.git)
cd api-biblioteca
```

2. Crear el entorno virtual:

- **Windows:**

```bash
python -m venv venv
```

- **Mac / Linux:**

```bash
python3 -m venv venv
```

3. Activar el entorno virtual:

- **Windows:**

```bash
venv\Scripts\activate
```

- **Mac / Linux:**

```bash
source venv/bin/activate
```

4. Instalar las dependencias:

```bash
pip install -r requirements.txt
```

## Cómo correr el proyecto

1. Asegurate de estar en la carpeta raíz del proyecto (`api-biblioteca/`) con el entorno virtual `(venv)` activo.
2. Levantá el servidor de desarrollo con cualquiera de estos dos comandos:

```bash
fastapi dev main.py
```

*(Alternativa equivalente con Uvicorn: `uvicorn main:app --reload`)*

3. Con el servidor corriendo, abrí en el navegador:

- **API:** `http://127.0.0.1:8000`
- **Documentación interactiva (Swagger):** `http://127.0.0.1:8000/docs`

4. Para frenar el servidor, presioná `Ctrl + C` en la terminal.