import json

import typer
from sqlalchemy import text

from hcenc.config import config
from hcenc.db.engine import engine

app = typer.Typer()


def profile_path():

    return (
        config.root
        / "backup"
        / "profile.json"
    )


@app.command("export")
def export():
    """
    Сохранить профиль игрока (юниты, инвентарь)
    в backup/profile.json — для репликации на GitHub.
    """

    with engine.begin() as conn:

        units = [
            dict(row)
            for row in conn.execute(
                text(
                    """
                    SELECT
                        id,
                        name,
                        fighter_type,
                        level,
                        set_code,
                        priority,
                        keeper_id
                    FROM units
                    ORDER BY priority DESC, id
                    """
                )
            ).mappings()
        ]

        unit_items = [
            dict(row)
            for row in conn.execute(
                text(
                    """
                    SELECT
                        unit_id,
                        slot,
                        item_code
                    FROM unit_items
                    ORDER BY unit_id, slot
                    """
                )
            ).mappings()
        ]

        owned = [
            row[0]
            for row in conn.execute(
                text(
                    """
                    SELECT code
                    FROM items
                    WHERE owned = 1
                    ORDER BY code
                    """
                )
            )
        ]

    profile = {
        "units": units,
        "unit_items": unit_items,
        "owned_items": owned,
    }

    path = profile_path()

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        json.dumps(
            profile,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    typer.echo(f"Экспортировано: {path}")


@app.command("import")
def import_profile():
    """
    Загрузить профиль игрока из backup/profile.json.
    """

    path = profile_path()

    if not path.exists():

        typer.echo("backup/profile.json не найден")

        raise typer.Exit(1)

    profile = json.loads(
        path.read_text(
            encoding="utf-8",
        )
    )

    with engine.begin() as conn:

        for unit in profile.get("units", []):

            conn.execute(
                text(
                    """
                    INSERT OR REPLACE INTO units
                        (id, name, fighter_type, level, set_code, priority, keeper_id)
                    VALUES
                        (:id, :name, :fighter_type, :level, :set_code, :priority, :keeper_id)
                    """
                ),
                unit,
            )

        for unit_item in profile.get("unit_items", []):

            conn.execute(
                text(
                    """
                    INSERT OR REPLACE INTO unit_items
                        (unit_id, slot, item_code)
                    VALUES
                        (:unit_id, :slot, :item_code)
                    """
                ),
                unit_item,
            )

        for code in profile.get("owned_items", []):

            conn.execute(
                text(
                    """
                    UPDATE items
                    SET owned = 1
                    WHERE code = :code
                    """
                ),
                {
                    "code": code,
                },
            )

    typer.echo("Профиль загружен.")
