from pathlib import Path

import requests

from hcenc.core.app import app
from hcenc.db.set_repository import set_repo


class SetImageDownloader:

    BASE_URL = "https://www.sagehc.eu"

    def __init__(self):

        self.session = requests.Session()

    def download(self, url: str, target: Path) -> bool:

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
            / "sets"
            / "materials"
        )

        root.mkdir(
            parents=True,
            exist_ok=True,
        )

        total = 0

        for row in set_repo.all_material_images():

            code = row["code"]

            images = [
                row["essence_image"],
                row["material1_image"],
                row["material2_image"],
                row["material3_image"],
                row["material4_image"],
            ]

            for url in images:

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


sync_set_images = SetImageDownloader()