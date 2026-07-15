from pathlib import Path

import requests

from hcenc.core.app import app
from hcenc.db.recommended_item_repository import (
    recommended_item_repo,
)


class RecommendedItemImageDownloader:

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
            / "items"
            / "recommended"
        )

        root.mkdir(
            parents=True,
            exist_ok=True,
        )

        total = 0

        for row in recommended_item_repo.all_images():

            url = row["source_url"]

            if not url:
                continue

            filename = url.split("/")[-1]

            target = root / filename

            if self.download(
                url,
                target,
            ):
                total += 1

                if total % 25 == 0:
                    print(total)

        return total


sync_recommended_item_images = (
    RecommendedItemImageDownloader()
)