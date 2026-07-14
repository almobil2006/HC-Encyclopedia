from dataclasses import asdict

from sqlalchemy import text

from hcenc.db.engine import engine
from hcenc.models.set import Set


_INSERT = text(
    """
    INSERT OR REPLACE INTO sets
    (
        code,
        set_id,

        name_en,
        name_ru,

        fighter_type,
        event_name,

        image,
        source_url,
        image_local,

        description_en,
        description_ru,

        bonus_2,
        bonus_4,
        bonus_6,

        substance_red_2,
        substance_red_4,
        substance_red_6,

        substance_yellow_2,
        substance_yellow_4,
        substance_yellow_6,

        substance_purple_2,
        substance_purple_4,
        substance_purple_6,

        essence_name,
        material1_name,
        material2_name,
        material3_name,
        material4_name,

        essence_image,
        material1_image,
        material2_image,
        material3_image,
        material4_image,

        recommended_items
    )
    VALUES
    (
        :code,
        :set_id,

        :name_en,
        :name_ru,

        :fighter_type,
        :event_name,

        :image,
        :source_url,
        :image_local,

        :description_en,
        :description_ru,

        :bonus_2,
        :bonus_4,
        :bonus_6,

        :substance_red_2,
        :substance_red_4,
        :substance_red_6,

        :substance_yellow_2,
        :substance_yellow_4,
        :substance_yellow_6,

        :substance_purple_2,
        :substance_purple_4,
        :substance_purple_6,

        :essence_name,
        :material1_name,
        :material2_name,
        :material3_name,
        :material4_name,

        :essence_image,
        :material1_image,
        :material2_image,
        :material3_image,
        :material4_image,

        :recommended_items
    )
    """
)


_SELECT_ALL = """
SELECT
    code,
    set_id,

    name_en,
    name_ru,

    fighter_type,
    event_name,

    image,
    source_url,
    image_local,

    description_en,
    description_ru,

    bonus_2,
    bonus_4,
    bonus_6,

    substance_red_2,
    substance_red_4,
    substance_red_6,

    substance_yellow_2,
    substance_yellow_4,
    substance_yellow_6,

    substance_purple_2,
    substance_purple_4,
    substance_purple_6,

    essence_name,
    material1_name,
    material2_name,
    material3_name,
    material4_name,

    essence_image,
    material1_image,
    material2_image,
    material3_image,
    material4_image,

    recommended_items

FROM sets
"""


class SetRepository:

    def save_sets(self, sets: list[Set]) -> None:

        if not sets:
            return

        with engine.begin() as conn:
            conn.execute(
                _INSERT,
                [asdict(s) for s in sets],
            )

    def count_sets(self) -> int:

        with engine.begin() as conn:

            return conn.execute(
                text(
                    "SELECT COUNT(*) FROM sets"
                )
            ).scalar_one()

    def all_sets(self) -> list[Set]:

        with engine.begin() as conn:

            rows = conn.execute(
                text(
                    _SELECT_ALL
                    + """
                    WHERE set_id IS NOT NULL
                    ORDER BY set_id
                    """
                )
            ).mappings()

            return [
                Set(**dict(row))
                for row in rows
            ]

    def get_set(self, code: str) -> Set | None:

        with engine.begin() as conn:

            row = conn.execute(
                text(
                    _SELECT_ALL
                    + """
                    WHERE code=:code
                    """
                ),
                {"code": code},
            ).mappings().first()

        if row is None:
            return None

        return Set(**dict(row))

    def all_with_images(self) -> list[Set]:

        with engine.begin() as conn:

            rows = conn.execute(
                text(
                    _SELECT_ALL
                    + """
                    WHERE source_url IS NOT NULL
                      AND source_url <> ''
                    ORDER BY set_id
                    """
                )
            ).mappings()

            return [
                Set(**dict(row))
                for row in rows
            ]

    def all_material_images(self):

        with engine.begin() as conn:

            return conn.execute(
                text(
                    """
                    SELECT
                        code,

                        essence_image,
                        material1_image,
                        material2_image,
                        material3_image,
                        material4_image

                    FROM sets

                    ORDER BY set_id
                    """
                )
            ).mappings().all()


set_repo = SetRepository()