from sqlalchemy import text

from hcenc.db.engine import engine
from hcenc.models.item import Item
from hcenc.models.unit import Unit


SLOTS = (
    "Weapon",
    "Armor",
    "Ring",
    "Amulet",
    "Artifact",
    "Totem",
)


class UnitRepository:

    def all(self) -> list[Unit]:

        with engine.begin() as conn:

            rows = conn.execute(
                text(
                    """
                    SELECT
                        id,
                        name,
                        fighter_type,
                        level,
                        set_code
                    FROM units
                    ORDER BY id
                    """
                )
            ).mappings()

            return [
                Unit(**dict(row))
                for row in rows
            ]

    def get(
        self,
        unit_id: int,
    ) -> Unit | None:

        with engine.begin() as conn:

            row = conn.execute(
                text(
                    """
                    SELECT
                        id,
                        name,
                        fighter_type,
                        level,
                        set_code
                    FROM units
                    WHERE id=:unit_id
                    """
                ),
                {
                    "unit_id": unit_id,
                },
            ).mappings().first()

        if row is None:
            return None

        return Unit(**dict(row))

    def create(
        self,
        name: str,
        fighter_type: str,
        level: int | None,
    ) -> int:

        with engine.begin() as conn:

            result = conn.execute(
                text(
                    """
                    INSERT INTO units
                        (name, fighter_type, level)
                    VALUES
                        (:name, :fighter_type, :level)
                    """
                ),
                {
                    "name": name,
                    "fighter_type": fighter_type,
                    "level": level,
                },
            )

            return result.lastrowid

    def delete(
        self,
        unit_id: int,
    ) -> None:

        with engine.begin() as conn:

            conn.execute(
                text(
                    """
                    DELETE FROM unit_items
                    WHERE unit_id=:unit_id
                    """
                ),
                {
                    "unit_id": unit_id,
                },
            )

            conn.execute(
                text(
                    """
                    DELETE FROM units
                    WHERE id=:unit_id
                    """
                ),
                {
                    "unit_id": unit_id,
                },
            )

    def assign_set(
        self,
        unit_id: int,
        set_code: str,
    ) -> None:

        with engine.begin() as conn:

            conn.execute(
                text(
                    """
                    UPDATE units
                    SET set_code=:set_code
                    WHERE id=:unit_id
                    """
                ),
                {
                    "unit_id": unit_id,
                    "set_code": set_code,
                },
            )

    def equipment(
        self,
        unit_id: int,
    ) -> dict[str, Item | None]:

        with engine.begin() as conn:

            rows = conn.execute(
                text(
                    """
                    SELECT
                        unit_items.slot,
                        items.code,
                        items.item_id,
                        items.name_en,
                        items.name_ru,
                        items.image,
                        items.source_url,
                        items.image_local
                    FROM unit_items
                    LEFT JOIN items
                        ON items.code = unit_items.item_code
                    WHERE unit_items.unit_id=:unit_id
                    """
                ),
                {
                    "unit_id": unit_id,
                },
            ).mappings()

            equipped = {
                row["slot"]: (
                    Item(**dict(row))
                    if row["code"] is not None
                    else None
                )
                for row in rows
                if row["slot"] in SLOTS
            }

        return {
            slot: equipped.get(slot)
            for slot in SLOTS
        }

    def equipped_codes(
        self,
        exclude_unit: int | None = None,
    ) -> set[str]:

        with engine.begin() as conn:

            rows = conn.execute(
                text(
                    """
                    SELECT item_code
                    FROM unit_items
                    WHERE item_code <> ''
                    """
                )
            )

            return {
                row[0]
                for row in rows
            }

    def assign(
        self,
        unit_id: int,
        slot: str,
        item_code: str,
    ) -> None:

        if slot not in SLOTS:
            return

        with engine.begin() as conn:

            if not item_code:

                conn.execute(
                    text(
                        """
                        DELETE FROM unit_items
                        WHERE unit_id=:unit_id
                          AND slot=:slot
                        """
                    ),
                    {
                        "unit_id": unit_id,
                        "slot": slot,
                    },
                )

                return

            conn.execute(
                text(
                    """
                    INSERT INTO unit_items
                        (unit_id, slot, item_code)
                    VALUES
                        (:unit_id, :slot, :item_code)
                    ON CONFLICT (unit_id, slot)
                    DO UPDATE SET
                        item_code=:item_code
                    """
                ),
                {
                    "unit_id": unit_id,
                    "slot": slot,
                    "item_code": item_code,
                },
            )


unit_repo = UnitRepository()
