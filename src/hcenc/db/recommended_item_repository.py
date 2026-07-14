from dataclasses import asdict

from sqlalchemy import text

from hcenc.db.engine import engine
from hcenc.models.recommended_item import RecommendedItem


_INSERT = text(
    """
    INSERT OR REPLACE INTO recommended_items
    (
        set_code,
        item_code,
        item_name,
        fighter_type,
        rarity,
        slot,
        item_url,
        image,
        source_url,
        image_local,
        position
    )
    VALUES
    (
        :set_code,
        :item_code,
        :item_name,
        :fighter_type,
        :rarity,
        :slot,
        :item_url,
        :image,
        :source_url,
        :image_local,
        :position
    )
    """
)


class RecommendedItemRepository:

    def save(
        self,
        items: list[RecommendedItem],
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

    def by_set(
        self,
        set_code: str,
    ) -> list[RecommendedItem]:

        with engine.begin() as conn:

            rows = conn.execute(
                text(
                    """
                    SELECT
                        set_code,
                        item_code,
                        item_name,
                        fighter_type,
                        rarity,
                        slot,
                        item_url,
                        image,
                        source_url,
                        image_local,
                        position
                    FROM recommended_items
                    WHERE set_code=:set_code
                    ORDER BY position
                    """
                ),
                {
                    "set_code": set_code,
                },
            ).mappings()

            return [
                RecommendedItem(**dict(row))
                for row in rows
            ]

    def all(self) -> list[RecommendedItem]:

        with engine.begin() as conn:

            rows = conn.execute(
                text(
                    """
                    SELECT
                        set_code,
                        item_code,
                        item_name,
                        fighter_type,
                        rarity,
                        slot,
                        item_url,
                        image,
                        source_url,
                        image_local,
                        position
                    FROM recommended_items
                    ORDER BY
                        set_code,
                        position
                    """
                )
            ).mappings()

            return [
                RecommendedItem(**dict(row))
                for row in rows
            ]

    def all_images(self):

        with engine.begin() as conn:

            return conn.execute(
                text(
                    """
                    SELECT
                        item_code,
                        source_url,
                        image_local
                    FROM recommended_items
                    WHERE source_url <> ''
                    ORDER BY set_code, position
                    """
                )
            ).mappings().all()


recommended_item_repo = RecommendedItemRepository()