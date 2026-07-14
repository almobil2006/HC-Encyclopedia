from pathlib import Path

from hcenc.core.app import app
from hcenc.db.recommended_item_repository import recommended_item_repo
from hcenc.db.set_repository import set_repo
from hcenc.net.client import client
from hcenc.sage.set_parser import set_parser


class SetDetailSynchronizer:

    def sync(self) -> int:

        cache = (
            app.config.assets.parent
            / "cache"
            / "sets"
        )

        cache.mkdir(
            parents=True,
            exist_ok=True,
        )

        total = 0

        sets = set_repo.all_sets()

        for item in sets:

            cache_file = cache / f"{item.code}.html"

            if cache_file.exists():

                html = cache_file.read_text(
                    encoding="utf-8"
                )

            else:

                html = client.get_set_detail(
                    item.set_id
                )

                cache_file.write_text(
                    html,
                    encoding="utf-8",
                )

            item = set_parser.parse_detail(
                html,
                item,
            )

            set_repo.save_sets(
                [item]
            )

            recommended = (
                set_parser.parse_recommended_items(
                    html,
                    item.code,
                )
            )

            recommended_item_repo.replace(
                item.code,
                recommended,
            )

            total += 1

            if total % 10 == 0:
                print(total)

        return total


sync_set_details = SetDetailSynchronizer()