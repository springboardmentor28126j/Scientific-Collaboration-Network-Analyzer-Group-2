from eralchemy2 import render_er
from app.db.base import Base

# Import all models so SQLAlchemy registers them
from app.models import *  # noqa

render_er(Base, "docs/er_diagram.pdf")
