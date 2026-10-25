from sqlalchemy import create_engine, event

from hcenc.core.app import app

DB_FILE = app.config.database / "game.sqlite"

engine = create_engine(
    f"sqlite:///{DB_FILE}",
    future=True,
    echo=False,
)


#
# Стандартный LIKE в SQLite не учитывает регистр
# только для латиницы; регистрируем собственный
# lower с поддержкой кириллицы
#


@event.listens_for(engine, "connect")
def _register_unicode_lower(dbapi_conn, record):

    dbapi_conn.create_function(
        "lower",
        1,
        lambda value: (
            value.lower()
            if isinstance(value, str)
            else value
        ),
    )
