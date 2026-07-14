from pathlib import Path

import requests

from hcenc.core.app import app
from hcenc.sage.parser import parser


class SageClient:

    BASE_URL = "https://www.sagehc.eu"

    def __init__(self):

        self.session = requests.Session()

    def fetch_page(self, page: int = 1) -> Path:

        url = (
            f"{self.BASE_URL}/services/items.aspx"
            f"?search=1"
            f"&pagenumber={page}"
            f"&keywords="
            f"&filter=ALL"
            f"&itemCase=g"
            f"&searchcase=NAME"
        )

        response = self.session.get(
            url,
            timeout=30,
        )

        response.raise_for_status()

        cache = app.config.cache / "html"
        cache.mkdir(parents=True, exist_ok=True)

        file = cache / f"page_{page:03}.html"

        file.write_text(
            response.text,
            encoding="utf-8",
        )

        return file

    def load_page(self, page: int = 1):

        file = self.fetch_page(page)

        html = file.read_text(
            encoding="utf-8"
        )

        return parser.parse(html)

    def fetch_sets_page(self, page: int = 1) -> str:

        url = (
            f"{self.BASE_URL}/services/items.aspx"
            f"?search=1"
            f"&pagenumber={page}"
            f"&keywords="
            f"&filter=ALL"
            f"&itemCase=s"
            f"&searchcase=NAME"
        )

        response = self.session.post(
            url,
            headers={
                "X-Requested-With": "XMLHttpRequest",
            },
            data="",
            timeout=30,
        )

        response.raise_for_status()

        return response.text

    def fetch_item(self, gear_id: int) -> str:

        url = (
            f"{self.BASE_URL}/services/items.aspx"
            f"?search=2"
            f"&gearIDs={gear_id}"
            f"&throne=11"
            f"&calledFrom=gearview"
        )

        response = self.session.post(
            url,
            timeout=30,
        )

        response.raise_for_status()

        return response.text

    def fetch_set(self, set_id: int) -> str:

        url = (
            f"{self.BASE_URL}/services/items.aspx"
            f"?search=3"
            f"&setID={set_id}"
            f"&throne=11"
            f"&calledFrom=setview"
        )

        response = self.session.post(
            url,
            timeout=30,
        )

        response.raise_for_status()

        return response.text

    def download(self, url: str) -> bytes:

        if url.startswith("/"):
            url = self.BASE_URL + url

        response = self.session.get(
            url,
            timeout=30,
        )

        response.raise_for_status()

        return response.content


sage = SageClient()