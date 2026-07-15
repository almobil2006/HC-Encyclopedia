from dataclasses import dataclass


@dataclass(slots=True)
class Item:

    #
    # идентификаторы
    #

    code: str = ""
    item_id: int | None = None

    #
    # названия
    #

    name_en: str = ""
    name_ru: str = ""

    #
    # классификация
    #

    fighter_type: str = ""
    rarity: str = ""
    slot: str = ""
    quality: str = ""

    #
    # уровень
    #

    min_level: int | None = None
    max_level: int | None = None

    #
    # изображения
    #

    image: str = ""
    source_url: str = ""
    image_local: str = ""

    skin_image: str = ""
    skin_source_url: str = ""
    skin_local: str = ""

    #
    # описание
    #

    description_en: str = ""
    description_ru: str = ""

    #
    # характеристики
    #

    health: str = ""
    damage: str = ""
    armor: str = ""
    magic_armor: str = ""

    dodge: str = ""
    critical: str = ""
    accuracy: str = ""

    spell_power: str = ""
    healing: str = ""

    #
    # способности
    #

    ability_name: str = ""
    ability_description: str = ""

    cooldown: str = ""
    trigger: str = ""

    #
    # источник получения
    #

    source: str = ""

    #
    # ссылки
    #

    page_url: str = ""

    #
    # служебное
    #

    cached: bool = False