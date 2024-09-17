from pony.orm import Database, Required
from ..board import models
from ..game import models
from ..gameState import models
from ..player import models
from ..figureCards import models
from ..movementCards import models

# Instanciar un objeto Database
db = Database()

# Bindear la database
db.bind(provider="sqlite", filename="elSwitcher.sqlite", create_db=True) # ver filename

# Generar los mappings y crear las tables
db.generate_mapping(create_tables=True)

