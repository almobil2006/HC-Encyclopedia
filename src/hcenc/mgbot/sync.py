import json
import re

from hcenc.db.database import database
from hcenc.db.item_repository import item_repo
from hcenc.db.set_repository import set_repo
from hcenc.mgbot.client import mgbot_client
from hcenc.models.set import Set


#
# Псевдонимы для сетов, у которых названия
# в SageHC и mg-bot заметно отличаются
#

ALIASES = {
    "shieldofempire": "empire",
}


def normalize(name: str) -> str:

    return re.sub(
        r"[^a-z0-9]",
        "",
        name.lower(),
    )


def clean(name: str) -> str:

    lowered = name.lower()

    lowered = (
        lowered
        .replace("'s set", "")
        .replace(" set", "")
        .replace("'s", "")
        .strip()
    )

    return normalize(lowered)


def match_set(
    sage_name: str,
    en_sets: dict,
) -> int | None:

    key = clean(sage_name)

    for candidate, data in en_sets.items():

        if key == clean(data["name"]):
            return candidate

    #
    # запасной проход: единственное вхождение
    # одного имени в другое
    #

    found = []

    for candidate, data in en_sets.items():

        name = clean(data["name"])

        if key and name and (
            key in name or name in key
        ):
            found.append(candidate)

    if len(found) == 1:
        return found[0]

    alias = ALIASES.get(key)

    if alias:

        for candidate, data in en_sets.items():

            if alias in clean(data["name"]):
                return candidate

    return None


def match_items(
    sage_items: list,
    en_items: list,
    ru_items: list,
) -> int:

    #
    # tag — стабильный идентификатор предмета в игре,
    # он одинаков в каталогах всех языков
    #

    tag_ru = {
        x["tag"]: x.get("n", "")
        for x in ru_items
        if x.get("tag") and x.get("n")
    }

    name_tag = {}

    for x in en_items:

        name = x.get("n", "")

        if name and name not in name_tag:
            name_tag[name] = x["tag"]

    total = 0

    for item in sage_items:

        ru_name = name_tag.get(item.name_en)

        if not ru_name:
            ru_name = name_tag.get(
                item.name_en
                .removesuffix(" Artifact")
                .strip()
            )

        if ru_name:
            ru_name = tag_ru.get(ru_name, ru_name)

        if not ru_name:
            continue

        item.name_ru = ru_name

        item_repo.save([item])

        total += 1

    return total


#
# Импорт предметов, которых нет в каталоге SageHC
# (базовые души и прочее, что есть только у mg-bot)
#

SLOT_BY_TYPE = {
    1: "Weapon",
    2: "Armor",
    3: "Ring",
    4: "Amulet",
    5: "Artifact",
    6: "Weapon Soul",
    7: "Armor Soul",
    8: "Totem",
}

CLASS_BY_CODE = {
    0: "",
    1: "Tank",
    2: "Archer",
    3: "Mage",
}


def import_missing_items(
    sage_items: list,
    en_items: list,
    ru_items: list,
) -> int:

    from hcenc.models.item import Item

    tag_ru = {
        x["tag"]: x.get("n", "")
        for x in ru_items
        if x.get("tag") and x.get("n")
    }

    #
    # один предмет на имя: вариант с максимальным
    # уровнем (каталог mg-bot идёт по возрастанию lvl)
    #

    by_name: dict = {}

    for x in sorted(
        en_items,
        key=lambda i: i.get("lvl") or 0,
    ):

        if x.get("t") not in SLOT_BY_TYPE:
            continue

        name = x.get("n") or ""

        if name:
            by_name[name] = x

    existing = {
        item.name_en
        for item in sage_items
    }

    imported = 0

    for name, x in by_name.items():

        if name in existing:
            continue

        item = Item(
            code=f"M{x['id']}",
            name_en=name,
            name_ru=tag_ru.get(x["tag"], ""),
            fighter_type=CLASS_BY_CODE.get(
                x.get("c"),
                "",
            ),
            slot=SLOT_BY_TYPE.get(x.get("t")),
            source="mg-bot",
        )

        item_repo.save([item])

        imported += 1

    return imported


class MgBotSynchronizer:

    def sync(self) -> int:

        database.initialize()

        ru_index = mgbot_client.index("ru")
        en_index = mgbot_client.index("en")

        if not ru_index or not en_index:
            print("mg-bot недоступен")
            return 0

        ru_sets = {
            x["id"]: x
            for x in ru_index["sets"]
        }

        en_sets = {
            x["id"]: x
            for x in en_index["sets"]
        }

        sets = set_repo.all_sets()

        total = 0

        for item in sets:

            mgbot_id = match_set(
                item.name_en,
                en_sets,
            )

            if mgbot_id is None:
                continue

            ru = ru_sets.get(mgbot_id)

            if ru is None:
                continue

            detail = mgbot_client.set_file(
                "ru",
                mgbot_id,
            )

            elements = []

            if detail and detail.get("set"):

                elements = (
                    detail["set"]
                    .get("elements", [])
                )

            item.mgbot_id = mgbot_id
            item.name_ru = ru["name"]
            item.mgbot_elements = json.dumps(
                elements,
                ensure_ascii=False,
            )

            set_repo.save_sets([item])

            total += 1

            print(
                f"{item.name_en}"
                f" -> {ru['name']}"
            )

        #
        # русские названия предметов
        #

        items = item_repo.all()

        ru_total = match_items(
            items,
            en_index["items"],
            ru_index["items"],
        )

        print(
            f"Items: {ru_total}"
            f"/{len(items)}"
        )

        #
        # предметы, которых нет у SageHC
        #

        imported = import_missing_items(
            items,
            en_index["items"],
            ru_index["items"],
        )

        print(f"Imported: {imported}")

        return total


sync_mgbot = MgBotSynchronizer()
