from dataclasses import dataclass


@dataclass(slots=True)
class Unit:

    #
    # идентификаторы
    #

    id: int | None = None

    #
    # описание
    #

    name: str = ""
    fighter_type: str = ""

    #
    # уровень
    #

    level: int | None = None

    #
    # выбранный сет
    #

    set_code: str = ""
