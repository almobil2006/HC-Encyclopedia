from pathlib import Path

import requests

from hcenc.core.app import app


class SetClient:

    BASE = "https://www.sagehc.eu"

    def __init__(self):

        self.session = requests.Session()

    def _post(
        self,
        url: str,
    ) -> str:

        response = self.session.post(
            url,
            timeout=30,
        )

        response.raise_for_status()

        return response.text

    def list_page(
        self,
        page: int,
    ) -> str:

        url = (
            self.BASE
            + "/services/items.aspx"
            + "?search=1"
            + f"&pagenumber={page}"
            + "&keywords="
            + "&filter=ALL"
            + "&itemCase=s"
            + "&searchcase=NAME"
        )

        return self._post(url)

    def detail(
        self,
        set_id: int,
    ) -> str:

        url = (
            self.BASE
            + "/services/items.aspx"
            + f"?search=2&setId={set_id}"
        )

        html = self._post(url)

        cache = (
            app.config.assets.parent
            / "cache"
            / "sets"
        )

        cache.mkdir(
            parents=True,
            exist_ok=True,
        )

        (
            cache
            / f"SET{set_id}.html"
        ).write_text(
            html,
            encoding="utf-8",
        )

        return html

    def recommended_items(
        self,
        set_id: int,
    ) -> str:

        url = (
            self.BASE
            + "/services/items.aspx"
            + f"?search=4&setId={set_id}"
        )

        return self._post(url)


set_client = SetClient()