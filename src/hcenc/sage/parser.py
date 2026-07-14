from bs4 import BeautifulSoup

from hcenc.models.item import Item


class SageParser:

    def parse(self, html: str) -> list[Item]:

        html = html.removeprefix("200#")

        soup = BeautifulSoup(html, "html.parser")

        table = soup.find("table", id="items")

        if table is None:
            return []

        items = []

        for row in table.find_all("tr"):

            cells = row.find_all("td")

            if len(cells) < 6:
                continue

            onclick = cells[0].get("onclick", "")

            gear_id = None

            if "ViewItemInfo('" in onclick:
                gear_id = int(onclick.split("'")[1])

            img = cells[5].find("img")

            items.append(
                Item(
                    gear_id=gear_id,
                    code=cells[4].get_text(strip=True),
                    name_en=cells[0].get_text(strip=True),
                    type_en=cells[1].get_text(strip=True),
                    fighter_type=cells[2].get_text(strip=True),
                    event_name=cells[3].get_text(strip=True),
                    image=img["src"] if img else "",
                )
            )

        return items

    def last_page(self, html: str) -> int:

        html = html.removeprefix("200#")

        soup = BeautifulSoup(html, "html.parser")

        values = []

        for button in soup.find_all("input"):

            value = button.get("value", "")

            if value.isdigit():
                values.append(int(value))

        return max(values) if values else 1

    def parse_detail(self, html: str, item: Item) -> Item:

        html = html.removeprefix("200#")

        soup = BeautifulSoup(html, "html.parser")

        #
        # описание
        #

        desc = soup.select_one(".card-third p")

        if desc:
            item.description_en = desc.get_text(" ", strip=True)

        #
        # картинка
        #

        img = soup.select_one(".left-section img")

        if img:

            src = img.get("src", "")

            item.image = src

            item.source_url = (
                "https://www.sagehc.eu" + src
                if src.startswith("/")
                else src
            )

        #
        # тип предмета
        #

        icon = soup.select_one(".right-section img")

        if icon:

            src = icon.get("src", "").lower()

            if "amulet" in src:
                item.type_en = "Amulet"
            elif "ring" in src:
                item.type_en = "Ring"
            elif "armor" in src:
                item.type_en = "Armor"
            elif "artifact" in src:
                item.type_en = "Artifact"
            elif "bow" in src:
                item.type_en = "Bow"
            elif "wand" in src:
                item.type_en = "Wand"
            elif "soul" in src:
                item.type_en = "Soul"
            elif "totem" in src:
                item.type_en = "Totem"

        #
        # требования
        #

        req = soup.select_one(".gear-requirements")

        if req:
            item.requirements = req.get_text(strip=True)

        #
        # правая колонка
        #

        for p in soup.select(".runeinfo_right p"):

            b = p.find("b")

            if not b:
                continue

            key = b.get_text(" ", strip=True).rstrip(":")

            value = p.get_text(" ", strip=True).replace(b.get_text(" ", strip=True), "").strip()

            if key == "User rating":
                item.user_rating = value

            elif key == "Event":
                item.event_name = value

            elif key == "Event date":
                item.last_seen = value

            elif key == "Sage bot code":
                item.sage_bot_code = value

            elif key == "First trigger":
                item.first_trigger = value

            elif key == "Cooldown":
                item.cooldown = value

            elif key == "Other locations the gear can be found":
                item.obtained_from = value

        #
        # название комплекта
        #

        for a in soup.find_all("a"):

            href = a.get("href", "")

            if "set" in href.lower():

                item.set_code = a.get_text(strip=True)

                break

        return item


parser = SageParser()