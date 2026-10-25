from pathlib import Path

import requests

from hcenc.core.app import app
from hcenc.db.rune_repository import rune_repo


class RuneImageDownloader:

    BASE_URL = "https://www.sagehc.eu"

    def __init__(self):

        self.session = requests.Session()

    def download(
        self,
        url: str,
        target: Path,
    ) -> bool:

        if not url:
            return False

        if target.exists():
            return False

        if url.startswith("/"):
            url = self.BASE_URL + url

        response = self.session.get(
            url,
            timeout=30,
        )

        response.raise_for_status()

        target.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        target.write_bytes(
            response.content
        )

        return True

    def sync(self) -> int:

        root = (
            app.config.assets
            / "runes"
        )

        root.mkdir(
            parents=True,
            exist_ok=True,
        )

        total = 0

        for rune in rune_repo.all():

            url = rune.source_url

            if not url:
                continue

            filename = (
                url.split("/")[-1]
                .lower()
            )

            target = (
                root
                / filename
            )

            local = (
                "assets/runes/"
                + filename
            )

            if rune.image_local == local and target.exists():
                continue

            downloaded = self.download(
                url,
                target,
            )

            if downloaded:
                total += 1

                if total % 50 == 0:
                    print(total)

            if target.exists():

                rune.image_local = local

                rune_repo.save(
                    [rune]
                )

        return total


sync_rune_images = RuneImageDownloader()
