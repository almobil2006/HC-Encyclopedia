from dataclasses import asdict

from sqlalchemy import text

from hcenc.db.engine import engine
from hcenc.models.recommended_item import RecommendedItem


_DELETE = text(
    """
    DELETE FROM recommended_items
    WHERE set_code=:set_code
    """
)


_INSERT = text(
    """
    INSERT INTO recommended_items
    (
        set_code,
        slot,
        item_code,
        item_name,
        item_url,
        image,
        source_url,
        image_local
    )
    VALUES
    (
        :set_code,
        :slot,
        :item_code,
        :item_name,
        :item_url,
        :image,
        :source_url,
        :image_local
    )
    """
)


class RecommendedItemRepository:

    def replace(
        self,
        set_code: str,
        items: list[RecommendedItem],
    ) -> None:

        with engine.begin() as conn:

            conn.execute(
                _DELETE,
                {
                    "set_code": set_code,
                },
            )

            if items:

                conn.execute(
                    _INSERT,
                    [
                        asdict(item)
                        for item in items
                    ],
                )

    def all(self) -> list[RecommendedItem]:

        with engine.begin() as conn:

            rows = conn.execute(
                text(
                    """
                    SELECT

                        set_code,
                        slot,
                        item_code,
                        item_name,
                        item_url,

                        image,
                        source_url,
                        image_local

                    FROM recommended_items

                    ORDER BY
                        set_code,
                        slot
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

                        set_code,
                        slot,

                        image,
                        source_url

                    FROM recommended_items

                    WHERE source_url <> ''

                    ORDER BY
                        set_code,
                        slot
                    """
                )
            ).mappings().all()


recommended_item_repo = RecommendedItemRepository()