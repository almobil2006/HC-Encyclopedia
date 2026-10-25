from dataclasses import dataclass


@dataclass(slots=True)
class Rune:

    #
    # идентификаторы
    #

    code: str = ""
    rune_id: int | None = None

    #
    # названия
    #

    name_en: str = ""
    name_ru: str = ""

    #
    # классификация
    #

    rune_type: str = ""

    #
    # событие получения
    #

    event_name: str = ""
    event_date: str = ""
    collection: str = ""

    #
    # источник получения
    #

    source: str = ""

    #
    # изображения
    #

    image: str = ""
    source_url: str = ""
    image_local: str = ""

    #
    # описания по классам владельца
    #

    description_tank: str = ""
    description_mage: str = ""
    description_archer: str = ""

    #
    # ссылки
    #

    page_url: str = ""

    #
    # служебное
    #

    cached: bool = False
