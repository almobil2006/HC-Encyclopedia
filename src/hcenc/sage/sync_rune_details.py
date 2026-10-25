from hcenc.core.app import app
from hcenc.db.rune_repository import rune_repo
from hcenc.net.client import client
from hcenc.sage.rune_parser import rune_parser


class RuneDetailSynchronizer:

    def sync(self) -> int:

        cache = (
            app.config.cache / "runes"
        )

        cache.mkdir(
            parents=True,
            exist_ok=True,
        )

        total = 0

        runes = rune_repo.all()

        for rune in runes:

            if rune.rune_id is None:
                continue

            cache_file = cache / f"{rune.code}.html"

            if cache_file.exists():

                html = cache_file.read_text(
                    encoding="utf-8",
                )

            else:

                html = client.get_rune_detail(
                    rune.rune_id
                )

                cache_file.write_text(
                    html,
                    encoding="utf-8",
                )

            rune = rune_parser.parse_detail(
                html,
                rune,
            )

            rune_repo.save(
                [rune]
            )

            total += 1

            if total % 10 == 0:
                print(total)

        return total


sync_rune_details = RuneDetailSynchronizer()
