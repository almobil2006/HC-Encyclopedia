from pathlib import Path

from hcenc.core.app import app
from hcenc.db.repository import repo
from hcenc.sage.client import sage


class ImageDownloader:

    def sync(self) -> int:

        images_dir = app.config.assets / "images" / "items"
        images_dir.mkdir(parents=True, exist_ok=True)

        total = 0

        for item in repo.all_with_images():

            code = item.code
            url = item.source_url

            if not url:
                continue

            ext = Path(url).suffix.lower()

            if not ext:
                ext = ".png"

            filename = images_dir / f"{code}{ext}"

            if filename.exists():
                continue

            print(code)

            data = sage.download(url)

            filename.write_bytes(data)

            item.image_local = str(filename)

            repo.save_items([item])

            total += 1

        return total


sync_images = ImageDownloader()