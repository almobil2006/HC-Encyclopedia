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

        cached,

        owned
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

        :cached,

        :owned
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

                        cached,

                        owned
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

                        cached,

                        owned
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


    def count(self) -> int:

        with engine.begin() as conn:

            return conn.execute(
                text("SELECT COUNT(*) FROM items")
            ).scalar_one()

    def facets(self) -> dict:

        with engine.begin() as conn:

            def distinct(column: str) -> list[str]:

                rows = conn.execute(
                    text(
                        f"""
                        SELECT DISTINCT {column}
                        FROM items
                        WHERE {column} <> ''
                        ORDER BY {column}
                        """
                    )
                )

                return [
                    row[0]
                    for row in rows
                ]

            return {
                "fighter_type": distinct("fighter_type"),
                "slot": distinct("slot"),
                "rarity": distinct("rarity"),
            }

    def page(
        self,
        q: str = "",
        fighter_type: str = "",
        slot: str = "",
        rarity: str = "",
        owned: bool = False,
        page: int = 1,
        size: int = 50,
    ) -> tuple[list[Item], int]:

        conditions = []
        params: dict = {}

        if owned:
            conditions.append("owned = 1")

        if q:
            conditions.append(
                "(lower(name_en) LIKE :q"
                " OR lower(name_ru) LIKE :q"
                " OR lower(code) LIKE :q)"
            )
            params["q"] = f"%{q.lower()}%"

        if fighter_type:
            conditions.append("fighter_type = :fighter_type")
            params["fighter_type"] = fighter_type

        if slot:
            conditions.append("slot = :slot")
            params["slot"] = slot

        if rarity:
            conditions.append("rarity = :rarity")
            params["rarity"] = rarity

        where = (
            "WHERE " + " AND ".join(conditions)
            if conditions
            else ""
        )

        #
        # при поиске сортируем по имени — совпадения
        # видны сразу, а не на следующих страницах
        #

        if q:
            order = (
                "ORDER BY lower(name_ru),"
                " lower(name_en)"
            )

        else:
            order = (
                "ORDER BY"
                " fighter_type,"
                " slot,"
                " rarity,"
                " name_en"
            )

        with engine.begin() as conn:

            total = conn.execute(
                text(
                    f"""
                    SELECT COUNT(*)
                    FROM items
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

                        description_en,
                        description_ru,

                        health,
                        damage,
                        armor,
                        magic_armor,

                        ability_name,

                        owned

                    FROM items
                    {where}
                    {order}
                    LIMIT :limit OFFSET :offset
                    """
                ),
                {
                    **params,
                    "limit": size,
                    "offset": (page - 1) * size,
                },
            ).mappings()

            items = [
                Item(**dict(row))
                for row in rows
            ]

        return items, total


    def set_owned(
        self,
        code: str,
        owned: bool,
    ) -> None:

        with engine.begin() as conn:

            conn.execute(
                text(
                    """
                    UPDATE items
                    SET owned=:owned
                    WHERE code=:code
                    """
                ),
                {
                    "code": code,
                    "owned": int(owned),
                },
            )

    def count_owned(self) -> int:

        with engine.begin() as conn:

            return conn.execute(
                text(
                    """
                    SELECT COUNT(*)
                    FROM items
                    WHERE owned = 1
                    """
                )
            ).scalar_one()

    def by_slot(
        self,
        slot: str,
        fighter_type: str = "",
        owned_only: bool = True,
        any_class: bool = False,
    ) -> list[Item]:

        conditions = ["items.slot = :slot"]
        params: dict = {"slot": slot}

        if fighter_type and not any_class:

            conditions.append(
                "(items.fighter_type = :fighter_type"
                " OR items.fighter_type = '')"
            )
            params["fighter_type"] = fighter_type

        if owned_only:
            conditions.append("items.owned = 1")

        where = "WHERE " + " AND ".join(conditions)

        #
        # при мягком режиме подходящие по классу
        # предметы идут первыми, остальные — после
        #

        if any_class and fighter_type:
            order = (
                "ORDER BY"
                " CASE WHEN items.fighter_type"
                " IN ('', :fighter_type)"
                " THEN 0 ELSE 1 END,"
                " max_level DESC,"
                " name_en"
            )
            params["fighter_type"] = fighter_type

        else:
            order = (
                "ORDER BY"
                " max_level DESC,"
                " name_en"
            )

        with engine.begin() as conn:

            rows = conn.execute(
                text(
                    f"""
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
                        image_local
                    FROM items
                    {where}
                    {order}
                    """
                ),
                params,
            ).mappings()

            return [
                Item(**dict(row))
                for row in rows
            ]


item_repo = ItemRepository()