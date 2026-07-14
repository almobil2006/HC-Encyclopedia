from dataclasses import asdict

from sqlalchemy import text

from hcenc.db.engine import engine
from hcenc.models.item import Item
from hcenc.models.set import Set


_INSERT_ITEM = text(
    """
    INSERT OR REPLACE INTO items
    (
        code,
        gear_id,
        set_code,
        name_en,
        name_ru,
        type_en,
        type_ru,
        fighter_type,
        rarity,
        slot,
        class_name,
        event_name,
        obtained_from,
        last_seen,
        image,
        source_url,
        image_local,
        description_en,
        description_ru,
        sage_bot_code,
        user_rating,
        requirements,
        first_trigger,
        cooldown,
        health,
        armor,
        magic_armor,
        damage,
        spell_power,
        dodge,
        crit,
        crit_damage,
        attack_speed,
        healing,
        vampirism,
        effects
    )
    VALUES
    (
        :code,
        :gear_id,
        :set_code,
        :name_en,
        :name_ru,
        :type_en,
        :type_ru,
        :fighter_type,
        :rarity,
        :slot,
        :class_name,
        :event_name,
        :obtained_from,
        :last_seen,
        :image,
        :source_url,
        :image_local,
        :description_en,
        :description_ru,
        :sage_bot_code,
        :user_rating,
        :requirements,
        :first_trigger,
        :cooldown,
        :health,
        :armor,
        :magic_armor,
        :damage,
        :spell_power,
        :dodge,
        :crit,
        :crit_damage,
        :attack_speed,
        :healing,
        :vampirism,
        :effects
    )
    """
)

_INSERT_SET = text(
    """
    INSERT OR REPLACE INTO sets
    (
        code,
        name_en,
        name_ru,
        image,
        source_url,
        image_local,
        description_en,
        description_ru,
        bonus_2,
        bonus_4,
        bonus_6
    )
    VALUES
    (
        :code,
        :name_en,
        :name_ru,
        :image,
        :source_url,
        :image_local,
        :description_en,
        :description_ru,
        :bonus_2,
        :bonus_4,
        :bonus_6
    )
    """
)


class Repository:

    def save_items(self, items: list[Item]) -> None:

        if not items:
            return

        with engine.begin() as conn:
            conn.execute(
                _INSERT_ITEM,
                [asdict(item) for item in items],
            )

    def save_sets(self, sets: list[Set]) -> None:

        if not sets:
            return

        with engine.begin() as conn:
            conn.execute(
                _INSERT_SET,
                [asdict(s) for s in sets],
            )

    def count_items(self) -> int:

        with engine.begin() as conn:
            return conn.execute(
                text("SELECT COUNT(*) FROM items")
            ).scalar_one()

    def count_sets(self) -> int:

        with engine.begin() as conn:
            return conn.execute(
                text("SELECT COUNT(*) FROM sets")
            ).scalar_one()

    def all_codes(self) -> list[str]:

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

            return [row.code for row in rows]

    def all_items(self):

        with engine.begin() as conn:

            rows = conn.execute(
                text(
                    """
                    SELECT gear_id, code
                    FROM items
                    WHERE gear_id IS NOT NULL
                    ORDER BY gear_id
                    """
                )
            )

            return list(rows)

    def get_item(self, code: str):

        with engine.begin() as conn:

            row = conn.execute(
                text(
                    """
                    SELECT
                        code,
                        gear_id,
                        set_code,
                        name_en,
                        name_ru,
                        type_en,
                        type_ru,
                        fighter_type,
                        rarity,
                        slot,
                        class_name,
                        event_name,
                        obtained_from,
                        last_seen,
                        image,
                        source_url,
                        image_local,
                        description_en,
                        description_ru,
                        sage_bot_code,
                        user_rating,
                        requirements,
                        first_trigger,
                        cooldown,
                        health,
                        armor,
                        magic_armor,
                        damage,
                        spell_power,
                        dodge,
                        crit,
                        crit_damage,
                        attack_speed,
                        healing,
                        vampirism,
                        effects
                    FROM items
                    WHERE code=:code
                    """
                ),
                {"code": code},
            ).mappings().first()

        if row is None:
            return None

        return Item(**dict(row))

    def get_set(self, code: str):

        with engine.begin() as conn:

            row = conn.execute(
                text(
                    """
                    SELECT
                        code,
                        name_en,
                        name_ru,
                        image,
                        source_url,
                        image_local,
                        description_en,
                        description_ru,
                        bonus_2,
                        bonus_4,
                        bonus_6
                    FROM sets
                    WHERE code=:code
                    """
                ),
                {"code": code},
            ).mappings().first()

        if row is None:
            return None

        return Set(**dict(row))

    def all_sets(self):

        with engine.begin() as conn:

            rows = conn.execute(
                text(
                    """
                    SELECT
                        code,
                        name_en,
                        name_ru,
                        image,
                        source_url,
                        image_local,
                        description_en,
                        description_ru,
                        bonus_2,
                        bonus_4,
                        bonus_6
                    FROM sets
                    ORDER BY code
                    """
                )
            ).mappings()

            return [Set(**dict(row)) for row in rows]

    def all_with_images(self):

        with engine.begin() as conn:

            rows = conn.execute(
                text(
                    """
                    SELECT
                        code,
                        gear_id,
                        set_code,
                        name_en,
                        name_ru,
                        type_en,
                        type_ru,
                        fighter_type,
                        rarity,
                        slot,
                        class_name,
                        event_name,
                        obtained_from,
                        last_seen,
                        image,
                        source_url,
                        image_local,
                        description_en,
                        description_ru,
                        sage_bot_code,
                        user_rating,
                        requirements,
                        first_trigger,
                        cooldown,
                        health,
                        armor,
                        magic_armor,
                        damage,
                        spell_power,
                        dodge,
                        crit,
                        crit_damage,
                        attack_speed,
                        healing,
                        vampirism,
                        effects
                    FROM items
                    WHERE source_url IS NOT NULL
                      AND source_url <> ''
                    ORDER BY gear_id
                    """
                )
            ).mappings()

            return [Item(**dict(row)) for row in rows]


repo = Repository()