from dataclasses import asdict

from sqlalchemy import text

from hcenc.db.engine import engine
from hcenc.models.item import Item


_INSERT = text(
"""
INSERT OR REPLACE INTO items
(
code,
gear_id,
name_en,
name_ru,
type_en,
type_ru,
fighter_type,
event_name,
image,
rarity,
slot,
class_name,
source_url,
image_local,
description_en,
description_ru,
obtained_from,
last_seen
)
VALUES
(
:code,
:gear_id,
:name_en,
:name_ru,
:type_en,
:type_ru,
:fighter_type,
:event_name,
:image,
:rarity,
:slot,
:class_name,
:source_url,
:image_local,
:description_en,
:description_ru,
:obtained_from,
:last_seen
)
"""
)


class Repository:

    def save_items(self, items: list[Item]) -> None:

        if not items:
            return

        with engine.begin() as conn:
            conn.execute(
                _INSERT,
                [asdict(i) for i in items],
            )

    def count_items(self):

        with engine.begin() as conn:

            return conn.execute(
                text("SELECT COUNT(*) FROM items")
            ).scalar_one()

    def all_items(self):

        with engine.begin() as conn:

            rows = conn.execute(
                text(
                    """
                    SELECT gear_id,code
                    FROM items
                    WHERE gear_id IS NOT NULL
                    ORDER BY gear_id
                    """
                )
            )

            return list(rows)

    def all_codes(self):

        with engine.begin() as conn:

            rows = conn.execute(
                text(
                    """
                    SELECT code
                    FROM items
                    ORDER BY code
                    """
                )
            )

            return [r.code for r in rows]

    def get_item(self, code: str):

        with engine.begin() as conn:

            row = conn.execute(
                text(
                    """
                    SELECT
                    code,
                    gear_id,
                    name_en,
                    name_ru,
                    type_en,
                    type_ru,
                    fighter_type,
                    event_name,
                    image,
                    rarity,
                    slot,
                    class_name,
                    source_url,
                    image_local,
                    description_en,
                    description_ru,
                    obtained_from,
                    last_seen
                    FROM items
                    WHERE code=:code
                    """
                ),
                {"code": code},
            ).mappings().first()

        if row is None:
            return None

        return Item(**dict(row))

    def all_with_images(self):

        with engine.begin() as conn:

            rows = conn.execute(
                text(
                    """
                    SELECT
                    code,
                    gear_id,
                    name_en,
                    name_ru,
                    type_en,
                    type_ru,
                    fighter_type,
                    event_name,
                    image,
                    rarity,
                    slot,
                    class_name,
                    source_url,
                    image_local,
                    description_en,
                    description_ru,
                    obtained_from,
                    last_seen
                    FROM items
                    WHERE source_url IS NOT NULL
                    AND source_url<>''
                    ORDER BY gear_id
                    """
                )
            ).mappings()

            return [
                Item(**dict(r))
                for r in rows
            ]


repo = Repository()