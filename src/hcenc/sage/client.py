from pathlib import Path

import requests

from hcenc.core.app import app


class SageClient:

    BASE_URL = "https://www.sagehc.eu"

    def __init__(self):
        self.session = requests.Session()

    def fetch_page(self, page: int = 1) -> Path:

        url = (
            f"{self.BASE_URL}/services/resp_search.aspx"
            f"?search=1"
            f"&pagenumber={page}"
            f"&keywords="
            f"&filter="
            f"&itemCase=r"
            f"&searchCase="
        )

        response = self.session.post(
            url,
            data={},
            timeout=30,
        )

        response.raise_for_status()

        cache_dir = app.config.cache / "html"
        cache_dir.mkdir(parents=True, exist_ok=True)

        file = cache_dir / f"page_{page:03}.html"

        file.write_text(
            response.text,
            encoding="utf-8",
        )

        return file


sage = SageClient()
