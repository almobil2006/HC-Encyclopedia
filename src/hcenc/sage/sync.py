from hcenc.db.database import database
from hcenc.db.repository import repo
from hcenc.sage.client import SageClient
from hcenc.sage.parser import parser


class SageSynchronizer:

    def sync_all(self) -> int:

        database.initialize()

        sage = SageClient()

        first = sage.fetch_page(1)

        html = first.read_text(encoding="utf-8")

        pages = parser.last_page(html)

        print(f"Pages found: {pages}")

        total = 0

        for page in range(1, pages + 1):

            print(f"Page {page}/{pages}")

            file = sage.fetch_page(page)

            html = file.read_text(
                encoding="utf-8"
            )

            items = parser.parse(html)

            repo.save_items(items)

            total += len(items)

        return total


sync = SageSynchronizer()