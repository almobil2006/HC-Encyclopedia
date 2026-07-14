from hcenc.db.set_repository import set_repo
from hcenc.sage.set_client import set_client


class SetSynchronizer:

    def sync(self) -> int:

        page = 1
        total = 0

        while True:

            print(f"Page {page}")

            sets = set_client.load_page(page)

            if not sets:
                break

            set_repo.save_sets(sets)

            total += len(sets)

            if page >= set_client_last_page(page):
                break

            page += 1

        return total


def set_client_last_page(page: int) -> int:

    file = set_client.fetch_page(page)

    html = file.read_text(
        encoding="utf-8"
    )

    return set_client_page_count(html)


def set_client_page_count(html: str) -> int:

    return set_client_parser().last_page(html)


def set_client_parser():

    from hcenc.sage.set_parser import set_parser

    return set_parser


sync_sets = SetSynchronizer()