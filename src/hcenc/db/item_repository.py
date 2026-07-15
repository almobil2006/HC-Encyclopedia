from dataclasses import asdict

from sqlalchemy import text

from hcenc.db.engine import engine
from hcenc.models.item import Item


_INSERT = text(
    """
    INSERT OR REPLACE INTO items
    (
        code,
        item_id,

        name_en,
        name_ru,

        fighter_type,
        rarity,
        slot,
        quality,

        min_level,
        max_level,

        image,
        source_url,
        image_local,

        skin_image,
        skin_source_url,
        skin_local,

        description_en,
        description_ru,

        health,
        damage,
        armor,
        magic_armor,

        dodge,
        critical,
        accuracy,

        spell_power,
        healing,

        ability_name,
        ability_description,

        cooldown,
        trigger,

        source,
        page_url,

        cached
    )
    VALUES
    (
        :code,
        :item_id,

        :name_en,
        :name_ru,

        :fighter_type,
        :rarity,
        :slot,
        :quality,

        :min_level,
        :max_level,

        :image,
        :source_url,
        :image_local,

        :skin_image,
        :skin_source_url,
        :skin_local,

        :description_en,
        :description_ru,

        :health,
        :damage,
        :armor,
        :magic_armor,

        :dodge,
        :critical,
        :accuracy,

        :spell_power,
        :healing,

        :ability_name,
        :ability_description,

        :cooldown,
        :trigger,

        :source,
        :page_url,

        :cached
    )
    """
)


class ItemRepository:

    def save(
        self,
        items: list[Item],
    ) -> None:

        if not items:
            return

        with engine.begin() as conn:

            conn.execute(
                _INSERT,
                [
                    asdict(item)
                    for item in items
                ],
            )

    def all(self) -> list[Item]:

        with engine.begin() as conn:

            rows = conn.execute(
                text(
                    """
                    SELECT
                        code,
                        item_id,

                        name_en,
                        name_ru,

                        fighter_type,
                        rarity,
                        slot,
                        quality,

                        min_level,
                        max_level,

                        image,
                        source_url,
                        image_local,

                        skin_image,
                        skin_source_url,
                        skin_local,

                        description_en,
                        description_ru,

                        health,
                        damage,
                        armor,
                        magic_armor,

                        dodge,
                        critical,
                        accuracy,

                        spell_power,
                        healing,

                        ability_name,
                        ability_description,

                        cooldown,
                        trigger,

                        source,
                        page_url,

                        cached
                    FROM items
                    ORDER BY
                        fighter_type,
                        slot,
                        rarity,
                        name_en
                    """
                )
            ).mappings()

            return [
                Item(**dict(row))
                for row in rows
            ]

    def get(
        self,
        code: str,
    ) -> Item | None:

        with engine.begin() as conn:

            row = conn.execute(
                text(
                    """
                    SELECT
                        code,
                        item_id,

                        name_en,
                        name_ru,

                        fighter_type,
                        rarity,
                        slot,
                        quality,

                        min_level,
                        max_level,

                        image,
                        source_url,
                        image_local,

                        skin_image,
                        skin_source_url,
                        skin_local,

                        description_en,
                        description_ru,

                        health,
                        damage,
                        armor,
                        magic_armor,

                        dodge,
                        critical,
                        accuracy,

                        spell_power,
                        healing,

                        ability_name,
                        ability_description,

                        cooldown,
                        trigger,

                        source,
                        page_url,

                        cached
                    FROM items
                    WHERE code=:code
                    """
                ),
                {
                    "code": code,
                },
            ).mappings().first()

        if row is None:
            return None

        return Item(**dict(row))

    def all_images(self):

        with engine.begin() as conn:

            return conn.execute(
                text(
                    """
                    SELECT
                        code,
                        source_url,
                        image_local
                    FROM items
                    WHERE source_url <> ''
                    ORDER BY name_en
                    """
                )
            ).mappings().all()


item_repo = ItemRepository()