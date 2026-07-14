from dataclasses import dataclass


@dataclass(slots=True)
class RecommendedItem:

    set_code: str

    item_code: str = ""

    item_name: str = ""

    fighter_type: str = ""

    rarity: str = ""

    slot: str = ""

    item_url: str = ""

    image: str = ""

    source_url: str = ""

    image_local: str = ""

    position: int = 0