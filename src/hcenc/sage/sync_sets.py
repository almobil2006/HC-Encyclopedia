from hcenc.db.database import database
from hcenc.db.set_repository import set_repo
from hcenc.net.client import client
from hcenc.sage.set_parser import set_parser


class SetSynchronizer:

    def sync(self) -> int:

        database.initialize()

        total = 0

        page = 1

        while True:

            html = client.search_sets(page)

            sets = set_parser.parse(html)

            if not sets:
                break

            set_repo.save_sets(sets)

            total += len(sets)

            print(
                f"Page {page}: "
                f"{len(sets)} sets"
            )

            page += 1

        return total


sync_sets = SetSynchronizer()
