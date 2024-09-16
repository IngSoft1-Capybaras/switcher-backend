# How To: Backend

Una vez clonado el repositorio se deberá ejecutar los siguientes comandos desde la raíz del proyecto.

## Linux

### Crear virtual enviroment y activarlo

`python -m venv .venv`

`source .venv/bin/activate`

### Instalar requisitos 

`pip install --upgrade pip`

`pip install -r requirements.txt`

### Levantar el servidor

`uvicorn main:app --reload`

