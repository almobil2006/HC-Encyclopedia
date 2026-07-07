from bs4 import BeautifulSoup


class SageParser:
    def parse(self, html: str) -> list[dict]:
        html = html.removeprefix("200#")

        soup = BeautifulSoup(html, "html.parser")

        table = soup.find("table", id="items")
        if table is None:
            return []

        # Берём ВСЕ td подряд
        cells = table.find_all("td")

        items = []

        # Последняя строка пагинации имеет один td colspan=6.
        # Поэтому обрабатываем только группы по 6 ячеек.
        for i in range(0, len(cells), 6):

            if i + 5 >= len(cells):
                break

            group = cells[i:i + 6]

            # Пагинация
            if group[0].find("input"):
                break

            img = group[5].find("img")

            items.append(
                {
                    "name": group[0].get_text(strip=True),
                    "type": group[1].get_text(strip=True),
                    "fighter": group[2].get_text(strip=True),
                    "event": group[3].get_text(strip=True),
                    "code": group[4].get_text(strip=True),
                    "image": img["src"] if img else "",
                }
            )

        return items


parser = SageParser()
