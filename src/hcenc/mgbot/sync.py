import difflib
import json
import re

from hcenc.db.database import database
from hcenc.db.item_repository import item_repo
from hcenc.db.rune_repository import rune_repo
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


def normalize_name(name: str) -> str:

    lowered = name.lower()

    lowered = (
        lowered
        .replace("’", "'")
        .replace("'", "")
    )

    lowered = re.sub(
        r"[^a-z0-9]+",
        " ",
        lowered,
    )

    return re.sub(r"\s+", " ", lowered).strip()


def fuzzy_match_items(
    sage_items: list,
    en_items: list,
    ru_items: list,
) -> int:

    tag_ru = {
        x["tag"]: x.get("n", "")
        for x in ru_items
        if x.get("tag") and x.get("n")
    }

    #
    # кандидаты: имя mg -> слот, tag
    #

    info = {}

    for x in en_items:

        name = x.get("n") or ""

        if not name or name in info:
            continue

        if x["tag"] not in tag_ru:
            continue

        info[name] = {
            "slot": SLOT_BY_TYPE.get(x.get("t")),
            "tag": x["tag"],
        }

    by_slot: dict = {}

    for name, data in info.items():

        by_slot.setdefault(
            data["slot"],
            [],
        ).append(name)

    norm_cache = {
        name: normalize_name(name)
        for name in info
    }

    updated = 0

    for item in sage_items:

        if item.name_ru:
            continue

        query = normalize_name(item.name_en)

        if not query:
            continue

        #
        # предметы одного слота; для гравировок
        # и предметов без слота — все подряд
        #

        if item.slot in ("", None, "Engraving"):
            pool = list(info)

        else:
            pool = by_slot.get(item.slot, [])

        best = None

        for candidate in pool:

            ratio = difflib.SequenceMatcher(
                None,
                query,
                norm_cache[candidate],
            ).ratio()

            if best is None or ratio > best[1]:
                best = (candidate, ratio)

        if best is None or best[1] < 0.8:
            continue

        item.name_ru = tag_ru[
            info[best[0]]["tag"]
        ]

        item_repo.save([item])

        updated += 1

    return updated


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


def extract_abilities(data: dict) -> str:

    #
    # тексты способностей берём из верхнего
    # яруса предмета (подставленные значения)
    #

    tiers = data.get("x", {})

    best_key = None

    for key in tiers:

        try:
            number = int(key)
        except ValueError:
            continue

        if best_key is None or number > best_key:
            best_key = number

    if best_key is None:
        return ""

    entry = tiers.get(str(best_key), {})

    texts = []

    for block in entry.get("def", {}).get("common", []):

        text = (
            block
            .get("p", {})
            .get("node", {})
            .get("t", "")
        )

        if text and text not in texts:
            texts.append(text)

    separator = chr(10) + chr(10)
    return separator.join(texts)


def fetch_power(
    sage_items: list,
    en_items: list,
    ru_items: list,
) -> int:

    tag_g = {
        x["tag"]: x.get("g")
        for x in ru_items
        if x.get("tag")
    }

    name_tag = {}

    for x in en_items:

        name = x.get("n", "")

        if name and name not in name_tag:
            name_tag[name] = x["tag"]

    updated = 0

    for item in sage_items:

        tag = name_tag.get(item.name_en)

        if not tag:
            continue

        g = tag_g.get(tag)

        if g is None:
            continue

        data = mgbot_client.fetch(
            "ru",
            f"items/g{g}.json",
        )

        if not data:
            continue

        tiers = data.get("x", {})

        best = None

        for entry in tiers.values():

            power = entry.get("powerRange")

            if not power or len(power) != 2:
                continue

            if best is None or power[1] > best[1]:
                best = power

        if best is None:
            continue

        item.power_min = best[0]
        item.power_max = best[1]

        abilities = extract_abilities(data)

        if abilities:
            item.description_ru = abilities

        item_repo.save([item])

        updated += 1

    return updated


def match_runes() -> int:

    from hcenc.models.rune import Rune

    en = mgbot_client.fetch("en", "runes.json")
    ru = mgbot_client.fetch("ru", "runes.json")

    if not en or not ru:
        return 0

    ru_names = {
        g["gid"]: g.get("name", "")
        for g in ru.get("groups", [])
    }

    name_gid = {
        g.get("name"): g["gid"]
        for g in en.get("groups", [])
        if g.get("name")
    }

    updated = 0

    for rune in rune_repo.all():

        gid = name_gid.get(rune.name_en)

        if not gid:
            continue

        ru_name = ru_names.get(gid, "")

        if not ru_name:
            continue

        rune.name_ru = ru_name

        rune_repo.save([rune])

        updated += 1

    return updated


def format_sentences(text: str) -> str:

    #
    # одно предложение — одна строка;
    # сокращения вида «4 с.» не рвём
    #

    flat = re.sub(r"\s+", " ", text).strip()

    parts = re.split(
        r"(?<=[.!?])\s+(?=[А-ЯЁA-Z0-9])",
        flat,
    )

    result = []

    for part in parts:

        if result and result[-1].split()[-1:] in (["с."], ["т."]):
            result[-1] = result[-1] + " " + part

        else:
            result.append(part)

    separator = chr(10)

    return separator.join(result).strip()


def match_engravings() -> int:

    en = mgbot_client.fetch("en", "index.json")
    ru = mgbot_client.fetch("ru", "index.json")

    if not en or not ru:
        return 0

    ru_names = {
        row["id"]: row.get("name", "")
        for row in ru.get("engr", [])
    }

    def engr_key(name: str) -> str:

        return normalize_name(
            re.sub(
                r"engraving|artifact",
                "",
                name,
                flags=re.IGNORECASE,
            )
        )

    name_id = {
        engr_key(row["name"]): row["id"]
        for row in en.get("engr", [])
        if row.get("name")
    }

    updated = 0

    for item in item_repo.all():

        if item.slot != "Engraving":
            continue

        if item.name_ru:
            continue

        engr_id = name_id.get(
            engr_key(item.name_en)
        )

        if not engr_id:
            continue

        ru_name = ru_names.get(engr_id, "")

        if not ru_name:
            continue

        item.name_ru = ru_name

        item_repo.save([item])

        updated += 1

    return updated


#
# Запасной вариант определения слота по роду
# оружия в названии (когда предмета нет в mg)
#

KIND_SLOTS = {
    "топор": ("Weapon", "Tank"),
    "секира": ("Weapon", "Tank"),
    "копьё": ("Weapon", "Tank"),
    "копье": ("Weapon", "Tank"),
    "пистолет": ("Weapon", "Archer"),
    "пистолеты": ("Weapon", "Archer"),
    "ружьё": ("Weapon", "Archer"),
    "ружье": ("Weapon", "Archer"),
    "фонарь": ("Weapon", "Mage"),
    "лампа": ("Weapon", "Mage"),
    "книга": ("Weapon", "Mage"),
    "кинжал": ("Weapon", "Mage"),
    "кинжалы": ("Weapon", "Mage"),
    "pistol": ("Weapon", "Archer"),
    "musket": ("Weapon", "Archer"),
    "shotgun": ("Weapon", "Archer"),
    "ax": ("Weapon", "Tank"),
    "axe": ("Weapon", "Tank"),
    "spear": ("Weapon", "Tank"),
    "scythe": ("Weapon", "Tank"),
    "lantern": ("Weapon", "Mage"),
    "lamp": ("Weapon", "Mage"),
    "book": ("Weapon", "Mage"),
    "dagger": ("Weapon", "Mage"),
}

ARMOR_WORDS = (
    "лат", "одеян", "экипировк",
    "брон", "роб",
)


def fixup_slots() -> int:

    #
    # предметам без слота: тип и класс из
    # каталога mg, иначе — по роду оружия
    #

    en = mgbot_client.fetch("en", "index.json")
    ru = mgbot_client.fetch("ru", "index.json")

    if not en or not ru:
        return 0

    tag_info = {
        x["tag"]: (
            SLOT_BY_TYPE.get(x.get("t")),
            CLASS_BY_CODE.get(x.get("c"), ""),
        )
        for x in ru.get("items", [])
        if x.get("tag")
    }

    name_tag = {}

    for x in en.get("items", []):

        name = x.get("n") or ""

        if name and name not in name_tag:
            name_tag[name] = x["tag"]

    fixed = 0

    for item in item_repo.all():

        if item.slot:
            continue

        slot = ""
        cls = ""

        tag = name_tag.get(item.name_en)

        if tag and tag in tag_info:
            slot, cls = tag_info[tag]

        if not slot:

            first = (
                (item.name_ru or item.name_en)
                .lower()
                .split(" ")[0]
            )

            hit = KIND_SLOTS.get(first)

            if hit:
                slot, cls = hit

            elif first == "душа":

                rest = (item.name_ru or "").lower()

                if any(
                    word in rest
                    for word in ARMOR_WORDS
                ):
                    slot = "Armor Soul"

                else:
                    slot = "Weapon Soul"

        if not slot:
            continue

        item.slot = slot

        if cls:
            item.fighter_type = cls

        item_repo.save([item])

        fixed += 1

    return fixed


def fixup_rarity() -> int:

    #
    # редкость из каталога mg: для SageHC-предметов
    # по имени, для импортированных — по id из кода
    #

    en = mgbot_client.fetch("en", "index.json")
    ru = mgbot_client.fetch("ru", "index.json")

    if not en or not ru:
        return 0

    tag_r = {
        x["tag"]: x.get("r")
        for x in ru.get("items", [])
        if x.get("tag") and x.get("r") is not None
    }

    id_r = {
        str(x["id"]): x.get("r")
        for x in ru.get("items", [])
        if x.get("id") is not None
        and x.get("r") is not None
    }

    name_tag = {}

    for x in en.get("items", []):

        name = x.get("n") or ""

        if name and name not in name_tag:
            name_tag[name] = x["tag"]

    updated = 0

    for item in item_repo.all():

        if item.rarity:
            continue

        r = None

        if item.code.startswith("M"):
            r = id_r.get(item.code[1:])

        if r is None:
            tag = name_tag.get(item.name_en)

            if tag:
                r = tag_r.get(tag)

        if r is None:
            continue

        item.rarity = str(r)

        item_repo.save([item])

        updated += 1

    return updated


def fixup_icons() -> int:

    #
    # предметам без картинки — иконка их группы
    # из mg (иконки общие по типу, качаем один раз)
    #

    ru = mgbot_client.fetch("ru", "index.json")
    en = mgbot_client.fetch("en", "index.json")

    if not ru or not en:
        return 0

    def groups_map(index):

        result = {}

        for group in index.get("groups", []):

            ic = group.get("ic")

            name = group.get("n") or ""

            if ic and ic != -1 and name:
                result[name] = ic

        return result

    ru_icons = groups_map(ru)
    en_icons = groups_map(en)

    updated = 0

    seen_icons = set()

    for item in item_repo.all():

        if item.image_local:
            continue

        if item.source_url or item.image:
            continue

        ic = ru_icons.get(item.name_ru) or en_icons.get(
            item.name_en
        )

        if not ic:
            continue

        if ic not in seen_icons:

            data = mgbot_client.icon(ic)

            if data is None:
                continue

            seen_icons.add(ic)

        item.image_local = (
            f"assets/icons/{ic}.png"
        )

        item_repo.save([item])

        updated += 1

    print(f"Icons downloaded: {len(seen_icons)}")

    return updated


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

        substances = {
            str(key): value.get("color")
            for key, value in (
                ru_index.get("ascMeta", {})
                .get("substances", {})
                .items()
            )
            if isinstance(value, dict)
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

            #
            # русские тексты бонусов 2/4/6
            #

            if detail and detail.get("set"):

                bonus_fields = {
                    2: "bonus_2",
                    4: "bonus_4",
                    6: "bonus_6",
                }

                for bonus in detail["set"].get("bonuses", []):

                    field = bonus_fields.get(
                        bonus.get("count")
                    )

                    if not field:
                        continue

                    texts = [
                        ability.get("t", "")
                        for ability in bonus.get("abilities", [])
                        if ability.get("t")
                    ]

                    if texts:

                        setattr(
                            item,
                            field,
                            format_sentences(" ".join(texts)),
                        )

                #
                # русские тексты субстанций
                #

                colors = substances

                for bonus in (detail.get("asc") or {}).get("bonuses", []):

                    color = colors.get(
                        str(bonus.get("sub"))
                    )

                    if not color:
                        continue

                    field = (
                        f"substance_{color}_"
                        f"{bonus.get('count')}"
                    )

                    if not hasattr(item, field):
                        continue

                    texts = [
                        ability.get("t", "")
                        for ability in bonus.get("abilities", [])
                        if ability.get("t")
                    ]

                    if texts:

                        setattr(
                            item,
                            field,
                            format_sentences(" ".join(texts)),
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

        fuzzy_total = fuzzy_match_items(
            items,
            en_index["items"],
            ru_index["items"],
        )

        print(
            f"Items: {ru_total}"
            f"+{fuzzy_total}"
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

        #
        # сила предметов из файлов деталей
        #

        items = item_repo.all()

        powered = fetch_power(
            items,
            en_index["items"],
            ru_index["items"],
        )

        print(f"Power: {powered}/{len(items)}")

        #
        # русские названия рун
        #

        runes_total = match_runes()

        print(f"Runes: {runes_total}")

        #
        # гравировки из отдельной секции mg-bot
        #

        engr_total = match_engravings()

        print(f"Engravings: {engr_total}")

        #
        # предметы без слота (фонари, кинжалы,
        # пистолеты, души...)
        #

        slots_total = fixup_slots()

        print(f"Slots fixed: {slots_total}")

        #
        # редкость предметов
        #

        rarity_total = fixup_rarity()

        print(f"Rarity: {rarity_total}")

        #
        # иконки предметам без картинок
        #

        icons_total = fixup_icons()

        print(f"Icons: {icons_total}")

        return total


sync_mgbot = MgBotSynchronizer()
