from dataclasses import dataclass


@dataclass(slots=True)
class Item:

    code: str

    gear_id: int | None = None

    name_en: str = ""
    name_ru: str = ""

    type_en: str = ""
    type_ru: str = ""

    fighter_type: str = ""

    event_name: str = ""

    image: str = ""

    rarity: str = ""

    slot: str = ""

    class_name: str = ""

    source_url: str = ""

    image_local: str = ""

    description_en: str = ""

    description_ru: str = ""

    obtained_from: str = ""

    last_seen: str = ""
