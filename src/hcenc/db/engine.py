from sqlalchemy import create_engine

from hcenc.core.app import app

DB_FILE = app.config.database / "game.sqlite"

engine = create_engine(
    f"sqlite:///{DB_FILE}",
    future=True,
    echo=False,
)
