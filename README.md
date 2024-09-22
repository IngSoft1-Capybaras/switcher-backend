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

`export ENVIRONMENT="production"`
`export PYTHONPATH="/path/to/this/project/`
`uvicorn main:app --reload`

Los valores posibles de ENVIRONMENT son `production`, `test` y `development`. Para cada valor, se crea una base de datos distinta

### Testing

Se puede usar el Makefile para correr los tests. 
Para correr los unittests:
`make run_unit_tests`

Para correr los integration tests:
`make run_integration_tests`

