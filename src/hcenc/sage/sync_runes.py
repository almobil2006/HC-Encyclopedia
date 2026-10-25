from hcenc.db.database import database
from hcenc.db.rune_repository import rune_repo
from hcenc.net.client import client
from hcenc.sage.rune_parser import rune_parser


class RuneSynchronizer:

    def sync(self) -> int:

        database.initialize()

        total = 0

        page = 1

        while True:

            html = client.search_runes(page)

            runes = rune_parser.parse(html)

            if not runes:
                break

            rune_repo.save(runes)

            total += len(runes)

            print(
                f"Page {page}: "
                f"{len(runes)} runes"
            )

            page += 1

        return total


sync_runes = RuneSynchronizer()
