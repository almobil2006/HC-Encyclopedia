from hcenc.core.app import app
from hcenc.db.database import database
from hcenc.db.item_repository import item_repo
from hcenc.net.client import client
from hcenc.sage.item_parser import item_parser


class ItemDetailSynchronizer:

    def sync(self) -> int:

        database.initialize()

        cache = (
            app.config.cache / "items"
        )

        cache.mkdir(
            parents=True,
            exist_ok=True,
        )

        total = 0

        items = item_repo.all()

        for item in items:

            if item.item_id is None:
                continue

            cache_file = cache / f"{item.code}.html"

            if cache_file.exists():

                html = cache_file.read_text(
                    encoding="utf-8",
                )

            else:

                html = client.get_item_detail(
                    item.item_id
                )

                cache_file.write_text(
                    html,
                    encoding="utf-8",
                )

            item = item_parser.parse_detail(
                html,
                item,
            )

            item_repo.save(
                [item]
            )

            total += 1

            if total % 100 == 0:
                print(total)

        return total


sync_item_details = ItemDetailSynchronizer()
