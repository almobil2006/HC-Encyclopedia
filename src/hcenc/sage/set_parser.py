from bs4 import BeautifulSoup, NavigableString

from hcenc.models.recommended_item import RecommendedItem
from hcenc.models.set import Set


class SetParser:

    #
    # список сетов
    #
    # Разметка сайта: три колонки —
    # название, картинка, пустая
    #

    def parse(
        self,
        html: str,
    ) -> list[Set]:

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

        sets = []

        for row in table.find_all("tr"):

            cells = row.find_all("td")

            if len(cells) < 2:
                continue

            onclick = cells[0].get(
                "onclick",
                "",
            )

            set_id = None

            if "ViewSetInfo('" in onclick:

                try:

                    set_id = int(
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

            sets.append(
                Set(
                    code=(
                        f"SET{set_id}"
                        if set_id is not None
                        else ""
                    ),
                    set_id=set_id,
                    name_en=cells[0].get_text(
                        strip=True,
                    ),
                    image=image,
                    source_url=source_url,
                )
            )

        return sets

    def last_page(self, html: str) -> int:

        html = html.removeprefix("200#")

        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        values = []

        for button in soup.find_all("input"):

            value = button.get("value", "")

            if value.isdigit():
                values.append(int(value))

        return max(values) if values else 1

    #
    # карточка сета
    #

    def parse_detail(
        self,
        html: str,
        item: Set,
    ) -> Set:

        html = html.removeprefix("200#")

        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        #
        # бонусы сета
        #

        descriptions = {}

        for h3 in soup.find_all("h3"):

            title = h3.get_text(
                strip=True,
            ).lower()

            if not title.startswith("description"):
                continue

            div = h3.find_next("div")

            if div is None:
                continue

            descriptions[title] = div.get_text(
                "\n",
                strip=True,
            )

        item.bonus_2 = descriptions.get(
            "description 2/6",
            "",
        )

        item.bonus_4 = descriptions.get(
            "description 4/6",
            "",
        )

        item.bonus_6 = descriptions.get(
            "description 6/6",
            "",
        )

        item.description_en = (
            item.bonus_6
            or item.bonus_4
            or item.bonus_2
        )

        #
        # картинка
        #

        img = soup.select_one(
            ".runeinfo_left img"
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
        # блок информации: класс и событие
        #

        info = soup.select_one(
            ".runeinfo_right"
        )

        if info:

            labels = {
                "Fighter type": "fighter_type",
                "Event": "event_name",
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
        # субстанции: секции с иконкой цвета
        #

        colors = {
            "red": (
                "substance_red_2",
                "substance_red_4",
                "substance_red_6",
            ),
            "yellow": (
                "substance_yellow_2",
                "substance_yellow_4",
                "substance_yellow_6",
            ),
            "purple": (
                "substance_purple_2",
                "substance_purple_4",
                "substance_purple_6",
            ),
        }

        for section in soup.find_all(
            "div",
            class_="settypeinfo_mobile",
        ):

            header = section.find(
                "div",
                class_="settypeinfo-header",
            )

            if header is None:
                continue

            icon = header.find("img")

            color = ""

            if icon:

                src = icon.get(
                    "src",
                    "",
                ).lower()

                for name in colors:

                    if name in src:
                        color = name

                        break

            if not color:
                continue

            fields = colors[color]

            for h3 in section.find_all("h3"):

                title = h3.get_text(
                    strip=True,
                ).lower()

                div = h3.find_next("div")

                if div is None:
                    continue

                text = div.get_text(
                    "\n",
                    strip=True,
                )

                if title.endswith("2/6"):
                    setattr(
                        item,
                        fields[0],
                        text,
                    )

                elif title.endswith("4/6"):
                    setattr(
                        item,
                        fields[1],
                        text,
                    )

                elif title.endswith("6/6"):
                    setattr(
                        item,
                        fields[2],
                        text,
                    )

        #
        # материалы
        #

        names = (
            "essence",
            "material1",
            "material2",
            "material3",
            "material4",
        )

        for box in soup.select(".side-box"):

            title = box.find("p")

            if title is None:
                continue

            if title.get_text(
                strip=True,
            ) != "Materials":
                continue

            rows = box.find_all("tr")

            for index, row in enumerate(rows):

                if index >= len(names):
                    break

                img = row.find("img")

                if img:
                    setattr(
                        item,
                        names[index] + "_image",
                        img.get(
                            "src",
                            "",
                        ),
                    )

                bold = row.find("b")

                if bold:
                    setattr(
                        item,
                        names[index] + "_name",
                        bold.get_text(
                            strip=True,
                        ),
                    )

            break

        return item

    def parse_recommended_items(
        self,
        html: str,
        set_code: str,
    ) -> list[RecommendedItem]:

        html = html.removeprefix("200#")

        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        items = []

        for row in soup.find_all("tr"):

            cells = row.find_all("td")

            if len(cells) < 5:
                continue

            onclick = row.get(
                "onclick",
                "",
            )

            item_code = ""
            item_url = ""

            if "ViewItemInfo('" in onclick:

                try:

                    item_code = (
                        onclick.split("'")[1]
                    )

                    item_url = (
                        "https://www.sagehc.eu/web/item/"
                        + item_code
                    )

                except Exception:
                    pass

            img = cells[4].find("img")

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
                RecommendedItem(
                    set_code=set_code,
                    item_code=item_code,
                    item_name=cells[0].get_text(
                        strip=True,
                    ),
                    slot=cells[3].get_text(
                        strip=True,
                    ),
                    item_url=item_url,
                    image=image,
                    source_url=source_url,
                )
            )

        return items


set_parser = SetParser()
