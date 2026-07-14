from bs4 import BeautifulSoup

from hcenc.models.recommended_item import RecommendedItem
from hcenc.models.set import Set


class SetParser:

    def parse(self, html: str) -> list[Set]:

        html = html.removeprefix("200#")

        soup = BeautifulSoup(html, "html.parser")

        table = soup.find("table", id="items")

        if table is None:
            return []

        sets = []

        for row in table.find_all("tr"):

            cells = row.find_all("td")

            if len(cells) < 5:
                continue

            onclick = cells[0].get("onclick", "")

            set_id = None

            if "ViewSetInfo('" in onclick:

                try:
                    set_id = int(
                        onclick.split("'")[1]
                    )
                except Exception:
                    pass

            img = cells[4].find("img")

            image = ""
            source_url = ""

            if img:

                image = img.get("src", "")

                if image.startswith("/"):
                    source_url = (
                        "https://www.sagehc.eu"
                        + image
                    )
                else:
                    source_url = image

            sets.append(
                Set(
                    code=cells[3].get_text(strip=True),
                    set_id=set_id,
                    name_en=cells[0].get_text(strip=True),
                    fighter_type=cells[1].get_text(strip=True),
                    event_name=cells[2].get_text(strip=True),
                    image=image,
                    source_url=source_url,
                )
            )

        return sets

    def last_page(self, html: str) -> int:

        html = html.removeprefix("200#")

        soup = BeautifulSoup(html, "html.parser")

        values = []

        for button in soup.find_all("input"):

            value = button.get("value", "")

            if value.isdigit():
                values.append(int(value))

        return max(values) if values else 1

    def parse_detail(
        self,
        html: str,
        item: Set,
    ) -> Set:

        html = html.removeprefix("200#")

        soup = BeautifulSoup(html, "html.parser")

        descriptions = {}

        for h3 in soup.find_all("h3"):

            title = h3.get_text(strip=True).lower()

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

        sections = soup.find_all(
            "div",
            class_="settypeinfo",
        )

        for section in sections:

            header = section.find(
                "div",
                class_="settypeinfo-header",
            )

            if header is None:
                continue

            title = header.get_text(
                " ",
                strip=True,
            ).lower()

            data = {}

            for h3 in section.find_all("h3"):

                key = h3.get_text(
                    strip=True
                ).lower()

                div = h3.find_next("div")

                if div is None:
                    continue

                data[key] = div.get_text(
                    "\n",
                    strip=True,
                )

            if "chaos" in title:

                item.substance_red_2 = data.get("description 2/6", "")
                item.substance_red_4 = data.get("description 4/6", "")
                item.substance_red_6 = data.get("description 6/6", "")

            elif "greatness" in title:

                item.substance_yellow_2 = data.get("description 2/6", "")
                item.substance_yellow_4 = data.get("description 4/6", "")
                item.substance_yellow_6 = data.get("description 6/6", "")

            elif "harmony" in title:

                item.substance_purple_2 = data.get("description 2/6", "")
                item.substance_purple_4 = data.get("description 4/6", "")
                item.substance_purple_6 = data.get("description 6/6", "")

        tables = soup.find_all("table")

        for table in tables:

            rows = table.find_all("tr")

            if len(rows) < 5:
                continue

            names = []
            images = []

            for row in rows:

                cells = row.find_all("td")

                if len(cells) < 2:
                    continue

                img = cells[0].find("img")

                if img:
                    images.append(
                        img.get("src", "")
                    )

                names.append(
                    cells[1].get_text(
                        " ",
                        strip=True,
                    )
                )

            if len(names) >= 5:

                item.essence_name = names[0]
                item.material1_name = names[1]
                item.material2_name = names[2]
                item.material3_name = names[3]
                item.material4_name = names[4]

                item.essence_image = images[0]
                item.material1_image = images[1]
                item.material2_image = images[2]
                item.material3_image = images[3]
                item.material4_image = images[4]

                break

        return item

    def parse_recommended_items(
        self,
        html: str,
        set_code: str,
    ) -> list[RecommendedItem]:

        html = html.removeprefix("200#")

        soup = BeautifulSoup(html, "html.parser")

        items = []

        for row in soup.find_all("tr"):

            cells = row.find_all("td")

            if len(cells) < 5:
                continue

            onclick = row.get("onclick", "")

            item_code = ""
            item_url = ""

            if "ViewItemInfo('" in onclick:

                try:
                    item_code = onclick.split("'")[1]

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

                image = img.get("src", "")

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
                    item_name=cells[0].get_text(strip=True),
                    slot=cells[3].get_text(strip=True),
                    item_url=item_url,
                    image=image,
                    source_url=source_url,
                )
            )

        return items


set_parser = SetParser()