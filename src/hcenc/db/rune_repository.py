from dataclasses import asdict

from sqlalchemy import text

from hcenc.db.engine import engine
from hcenc.models.rune import Rune


_COLUMNS = """
    code,
    rune_id,

    name_en,
    name_ru,

    rune_type,

    event_name,
    event_date,
    collection,

    source,

    image,
    source_url,
    image_local,

    description_tank,
    description_mage,
    description_archer,

    page_url,

    cached
"""

_INSERT = text(
    f"""
    INSERT OR REPLACE INTO runes
    (
        {_COLUMNS}
    )
    VALUES
    (
        :code,
        :rune_id,

        :name_en,
        :name_ru,

        :rune_type,

        :event_name,
        :event_date,
        :collection,

        :source,

        :image,
        :source_url,
        :image_local,

        :description_tank,
        :description_mage,
        :description_archer,

        :page_url,

        :cached
    )
    """
)


class RuneRepository:

    def save(
        self,
        runes: list[Rune],
    ) -> None:

        if not runes:
            return

        with engine.begin() as conn:

            conn.execute(
                _INSERT,
                [
                    asdict(rune)
                    for rune in runes
                ],
            )

    def all(self) -> list[Rune]:

        with engine.begin() as conn:

            rows = conn.execute(
                text(
                    f"""
                    SELECT
                        {_COLUMNS}
                    FROM runes
                    ORDER BY
                        rune_type,
                        name_en
                    """
                )
            ).mappings()

            return [
                Rune(**dict(row))
                for row in rows
            ]

    def get(
        self,
        code: str,
    ) -> Rune | None:

        with engine.begin() as conn:

            row = conn.execute(
                text(
                    f"""
                    SELECT
                        {_COLUMNS}
                    FROM runes
                    WHERE code=:code
                    """
                ),
                {
                    "code": code,
                },
            ).mappings().first()

        if row is None:
            return None

        return Rune(**dict(row))

    def all_images(self):

        with engine.begin() as conn:

            return conn.execute(
                text(
                    """
                    SELECT
                        code,
                        source_url,
                        image_local
                    FROM runes
                    WHERE source_url <> ''
                    ORDER BY name_en
                    """
                )
            ).mappings().all()


    def count(self) -> int:

        with engine.begin() as conn:

            return conn.execute(
                text("SELECT COUNT(*) FROM runes")
            ).scalar_one()

    def types(self) -> list[str]:

        with engine.begin() as conn:

            rows = conn.execute(
                text(
                    """
                    SELECT DISTINCT rune_type
                    FROM runes
                    WHERE rune_type <> ''
                    ORDER BY rune_type
                    """
                )
            )

            return [
                row[0]
                for row in rows
            ]

    def page(
        self,
        q: str = "",
        rune_type: str = "",
        page: int = 1,
        size: int = 100,
    ) -> tuple[list[Rune], int]:

        conditions = []
        params: dict = {}

        if q:
            conditions.append(
                "(lower(name_en) LIKE :q"
                " OR lower(name_ru) LIKE :q"
                " OR lower(code) LIKE :q)"
            )
            params["q"] = f"%{q.lower()}%"

        if rune_type:
            conditions.append("rune_type = :rune_type")
            params["rune_type"] = rune_type

        where = (
            "WHERE " + " AND ".join(conditions)
            if conditions
            else ""
        )

        with engine.begin() as conn:

            total = conn.execute(
                text(
                    f"""
                    SELECT COUNT(*)
                    FROM runes
                    {where}
                    """
                ),
                params,
            ).scalar_one()

            rows = conn.execute(
                text(
                    f"""
                    SELECT
                        code,
                        rune_id,
                        name_en,
                        name_ru,
                        rune_type,
                        event_name,
                        event_date,
                        collection,
                        source,
                        image,
                        source_url,
                        image_local
                    FROM runes
                    {where}
                    ORDER BY
                        rune_id DESC
                    LIMIT :limit OFFSET :offset
                    """
                ),
                {
                    **params,
                    "limit": size,
                    "offset": (page - 1) * size,
                },
            ).mappings()

            runes = [
                Rune(**dict(row))
                for row in rows
            ]

        return runes, total


rune_repo = RuneRepository()
