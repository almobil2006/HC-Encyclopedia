import re

from bs4 import BeautifulSoup, NavigableString

from hcenc.models.rune import Rune


class RuneParser:

    #
    # список рун
    #

    def parse(
        self,
        html: str,
    ) -> list[Rune]:

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

        runes = []

        for row in table.find_all("tr"):

            cells = row.find_all("td")

            if len(cells) < 3:
                continue

            onclick = cells[0].get(
                "onclick",
                "",
            )

            rune_id = None

            if "ViewRuneInfo('" in onclick:

                try:

                    rune_id = int(
                        onclick.split("'")[1]
                    )

                except Exception:
                    pass

            img = cells[2].find("img")

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

            runes.append(
                Rune(
                    code=(
                        f"R{rune_id}"
                        if rune_id is not None
                        else ""
                    ),
                    rune_id=rune_id,
                    name_en=cells[0].get_text(
                        strip=True,
                    ),
                    rune_type=cells[1].get_text(
                        strip=True,
                    ),
                    image=image,
                    source_url=source_url,
                )
            )

        return runes

    #
    # карточка руны
    #

    def parse_detail(
        self,
        html: str,
        rune: Rune,
    ) -> Rune:

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
            rune.name_en = name.get_text(
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

            rune.image = src

            if src.startswith("/"):
                rune.source_url = (
                    "https://www.sagehc.eu"
                    + src
                )

            else:
                rune.source_url = src

        #
        # блок информации: метки <b> и следующий
        # за ними текст (теги <p> на сайте не закрыты,
        # поэтому абзацы нельзя разбирать целиком)
        #

        info = soup.select_one(
            ".runeinfo_right"
        )

        if info:

            labels = {
                "Type": "rune_type",
                "Introduced in": "source",
                "Event": "event_name",
                "Event date": "event_date",
                "Collection": "collection",
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
                    rune,
                    field,
                    str(sibling).strip(),
                )

        #
        # код Sage Bot
        #

        match = re.search(
            r"rateItem\(\d+,\s*'R',\s*'([^']+)'",
            html,
        )

        if match:
            rune.code = match.group(1)

        #
        # описания по классам
        #

        fields = {
            "Tank": "description_tank",
            "Mage": "description_mage",
            "Archer": "description_archer",
        }

        for button in soup.find_all("input"):

            button_id = button.get(
                "id",
                "",
            )

            if not button_id.startswith(
                "runeDescrBtn_"
            ):
                continue

            index = button_id.removeprefix(
                "runeDescrBtn_"
            )

            field = fields.get(
                button.get(
                    "value",
                    "",
                )
            )

            if field is None:
                continue

            hidden = soup.find(
                "input",
                id=f"rdesc_{index}",
            )

            if hidden:
                setattr(
                    rune,
                    field,
                    hidden.get(
                        "value",
                        "",
                    ),
                )

        return rune


rune_parser = RuneParser()
