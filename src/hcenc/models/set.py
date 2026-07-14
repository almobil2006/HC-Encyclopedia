from dataclasses import dataclass


@dataclass(slots=True)
class Set:

    #
    # идентификаторы
    #

    code: str
    set_id: int | None = None

    #
    # название
    #

    name_en: str = ""
    name_ru: str = ""

    #
    # класс
    #

    fighter_type: str = ""

    #
    # событие
    #

    event_name: str = ""

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
    # основные бонусы
    #

    bonus_2: str = ""
    bonus_4: str = ""
    bonus_6: str = ""

    #
    # Substance of Chaos
    #

    substance_red_2: str = ""
    substance_red_4: str = ""
    substance_red_6: str = ""

    #
    # Substance of Greatness
    #

    substance_yellow_2: str = ""
    substance_yellow_4: str = ""
    substance_yellow_6: str = ""

    #
    # Substance of Harmony
    #

    substance_purple_2: str = ""
    substance_purple_4: str = ""
    substance_purple_6: str = ""

    #
    # Материалы
    #

    essence_name: str = ""
    material1_name: str = ""
    material2_name: str = ""
    material3_name: str = ""
    material4_name: str = ""

    essence_image: str = ""
    material1_image: str = ""
    material2_image: str = ""
    material3_image: str = ""
    material4_image: str = ""

    #
    # Рекомендуемые предметы
    #

    recommended_items: str = ""