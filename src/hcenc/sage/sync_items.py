from hcenc.db.item_repository import item_repo
from hcenc.net.client import client
from hcenc.sage.item_parser import item_parser


class ItemSynchronizer:

    def sync(self) -> int:

        total = 0

        page = 1

        while True:

            html = client.search_items(page)

            items = item_parser.parse(html)

            if not items:
                break

            item_repo.save(items)

            total += len(items)

            print(
                f"Page {page}: "
                f"{len(items)} items"
            )

            page += 1

        return total


sync_items = ItemSynchronizer()