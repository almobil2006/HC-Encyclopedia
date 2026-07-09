from hcenc.core.app import app
from hcenc.db.repository import repo
from hcenc.sage.client import sage
from hcenc.sage.parser import parser


class DetailDownloader:

    def sync(self) -> int:

        cache = app.config.cache / "items"
        cache.mkdir(parents=True, exist_ok=True)

        total = 0

        for gear_id, code in repo.all_items():

            file = cache / f"{code}.html"

            #
            # скачиваем страницу только один раз
            #

            if file.exists():

                html = file.read_text(
                    encoding="utf-8"
                )

            else:

                print(code)

                html = sage.fetch_detail(gear_id)

                file.write_text(
                    html,
                    encoding="utf-8",
                )

            item = repo.get_item(code)

            if item is None:
                continue

            item = parser.parse_detail(
                html,
                item,
            )

            repo.save_items([item])

            total += 1

            if total % 100 == 0:
                print(total)

        return total


sync_details = DetailDownloader()