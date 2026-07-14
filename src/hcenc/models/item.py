from dataclasses import dataclass


@dataclass(slots=True)
class Item:

    #
    # идентификаторы
    #

    code: str
    gear_id: int | None = None

    #
    # комплект
    #

    set_code: str = ""

    #
    # названия
    #

    name_en: str = ""
    name_ru: str = ""

    #
    # классификация
    #

    type_en: str = ""
    type_ru: str = ""

    fighter_type: str = ""

    rarity: str = ""

    slot: str = ""

    class_name: str = ""

    #
    # событие
    #

    event_name: str = ""

    obtained_from: str = ""

    last_seen: str = ""

    #
    # изображения
    #

    image: str = ""

    source_url: str = ""

    image_local: str = ""

    #
    # описание
    #

    description_en: str = ""

    description_ru: str = ""

    #
    # игровая информация
    #

    sage_bot_code: str = ""

    user_rating: str = ""

    requirements: str = ""

    first_trigger: str = ""

    cooldown: str = ""

    #
    # характеристики
    #

    health: str = ""

    armor: str = ""

    magic_armor: str = ""

    damage: str = ""

    spell_power: str = ""

    dodge: str = ""

    crit: str = ""

    crit_damage: str = ""

    attack_speed: str = ""

    healing: str = ""

    vampirism: str = ""

    #
    # эффекты
    #

    effects: str = ""