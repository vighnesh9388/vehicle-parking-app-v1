from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .lot import Lot
from .spot import Spot
from .reserve import Reserve
from .user import User
