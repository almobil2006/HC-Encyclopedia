from bs4 import BeautifulSoup

from hcenc.models.item import Item


class ItemParser:

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

            if len(cells) < 6:
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

            img = cells[5].find("img")

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
                    code=cells[4].get_text(
                        strip=True,
                    ),
                    item_id=item_id,
                    name_en=cells[0].get_text(
                        strip=True,
                    ),
                    slot=cells[1].get_text(
                        strip=True,
                    ),
                    fighter_type=cells[2].get_text(
                        strip=True,
                    ),
                    source=cells[3].get_text(
                        strip=True,
                    ),
                    image=image,
                    source_url=source_url,
                )
            )

        return items


item_parser = ItemParser()