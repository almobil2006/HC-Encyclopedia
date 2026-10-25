from bs4 import BeautifulSoup, NavigableString

from hcenc.models.item import Item


ICON_SLOTS = {
    "artifact": "Artifact",
    "armor": "Armor",
    "amulet": "Amulet",
    "ring": "Ring",
    "totem": "Totem",
    "weaponsoul": "Weapon Soul",
    "armorsoul": "Armor Soul",
    "engraving": "Engraving",
    "soul": "Soul",
}

WEAPONS = {
    "Tank": {
        "mace", "hammer", "club",
        "sword", "axe", "blade",
        "pick", "scythe", "frypan",
    },
    "Mage": {
        "staff", "scepter", "sceptor",
        "wand", "orb", "grimoire",
    },
    "Archer": {
        "bow", "crossbow", "arbalest",
    },
}


class ItemParser:

    #
    # список предметов
    #
    # Разметка сайта: три колонки —
    # название, картинка, кнопка сравнения
    #

    def parse(
        self,
        html: str,
    ) -> list[Item]:

        html = html.removeprefix("200#")

        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        table = soup.find(
            "table",
            id="items",
        )

        if table is None:
            return []

        items = []

        for row in table.find_all("tr"):

            cells = row.find_all("td")

            if len(cells) < 2:
                continue

            onclick = cells[0].get(
                "onclick",
                "",
            )

            item_id = None

            if "ViewItemInfo('" in onclick:

                try:

                    item_id = int(
                        onclick.split("'")[1]
                    )

                except Exception:
                    pass

            img = cells[1].find("img")

            image = ""
            source_url = ""

            if img:

                image = img.get(
                    "src",
                    "",
                )

                if image.startswith("/"):
                    source_url = (
                        "https://www.sagehc.eu"
                        + image
                    )

                else:
                    source_url = image

            items.append(
                Item(
                    code=(
                        f"G{item_id}"
                        if item_id is not None
                        else ""
                    ),
                    item_id=item_id,
                    name_en=cells[0].get_text(
                        strip=True,
                    ),
                    image=image,
                    source_url=source_url,
                )
            )

        return items

    #
    # карточка предмета
    #

    def parse_detail(
        self,
        html: str,
        item: Item,
    ) -> Item:

        html = html.removeprefix("200#")

        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        #
        # название
        #

        name = soup.select_one(
            ".card-top .left-text"
        )

        if name:
            item.name_en = name.get_text(
                strip=True,
            )

        #
        # картинка
        #

        img = soup.select_one(
            ".left-section img"
        )

        if img:

            src = img.get(
                "src",
                "",
            )

            item.image = src

            if src.startswith("/"):
                item.source_url = (
                    "https://www.sagehc.eu"
                    + src
                )

            else:
                item.source_url = src

        #
        # слот по иконке типа; мифические и божественные
        # варианты помечены суффиксами _myth / _div
        #

        icon = soup.select_one(
            ".right-section img"
        )

        if icon:

            src = icon.get(
                "src",
                "",
            ).lower()

            key = src.split("card_gear_type_")[-1]

            key = (
                key
                .removesuffix(".jpg")
                .removesuffix("_myth")
                .removesuffix("_div")
            )

            slot = ICON_SLOTS.get(key)

            if slot:
                item.slot = slot

        #
        # оружие не имеет своей иконки: общий вид
        # карточки — myth/div, поэтому класс оружия
        # определяем по ключевым словам в имени
        # картинки и названии предмета
        #

        if not item.slot:

            tokens = set()

            if item.image:

                for part in item.image.lower().split("/"):
                    tokens.update(
                        part
                        .replace(".png", "")
                        .split("_")
                    )

            for word in item.name_en.lower().split():
                tokens.add(
                    "".join(
                        ch
                        for ch in word
                        if ch.isalpha()
                    )
                )

            for fighter, keys in WEAPONS.items():

                if tokens & keys:
                    item.slot = "Weapon"
                    item.fighter_type = fighter
                    break

        #
        # описание способности
        #

        desc = soup.select_one(
            ".card-third p"
        )

        if desc:
            item.description_en = (
                desc.get_text(
                    " ",
                    strip=True,
                )
            )

        #
        # требуемый уровень
        #

        requirements = soup.select_one(
            ".gear-requirements"
        )

        if requirements:

            parts = (
                requirements
                .get_text(strip=True)
                .split("-")
            )

            if len(parts) == 2:

                try:

                    item.min_level = int(
                        parts[0]
                    )

                    item.max_level = int(
                        parts[1]
                    )

                except ValueError:
                    pass

        #
        # блок информации: событие и
        # прочие места получения
        #

        info = soup.select_one(
            ".innerInfo"
        )

        if info:

            labels = {
                "Event": "source",
            }

            for bold in info.find_all("b"):

                label = (
                    bold
                    .get_text(strip=True)
                    .rstrip(":")
                )

                field = labels.get(label)

                if field is None:
                    continue

                sibling = bold.next_sibling

                if not isinstance(
                    sibling,
                    NavigableString,
                ):
                    continue

                setattr(
                    item,
                    field,
                    str(sibling).strip(),
                )

        #
        # ссылка на страницу сайта
        #

        if item.item_id is not None:
            item.page_url = (
                "https://www.sagehc.eu/web/items"
                f"?item={item.item_id}&ic=g"
            )

        return item


item_parser = ItemParser()
