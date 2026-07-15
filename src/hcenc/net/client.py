from pathlib import Path

import requests

from hcenc.core.app import app


class SageClient:

    BASE_URL = "https://www.sagehc.eu"

    def __init__(self):

        self.session = requests.Session()

    def _post(
        self,
        params: dict,
    ) -> str:

        response = self.session.post(
            self.BASE_URL + "/services/items.aspx",
            params=params,
            timeout=30,
        )

        response.raise_for_status()

        return response.text

    #
    # Sets
    #

    def search_sets(
        self,
        page: int,
    ) -> str:

        return self._post(
            {
                "search": 1,
                "pagenumber": page,
                "keywords": "",
                "filter": "ALL",
                "itemCase": "s",
                "searchcase": "NAME",
            }
        )

    def get_set_detail(
        self,
        set_id: int,
    ) -> str:

        return self._post(
            {
                "search": 4,
                "setId": set_id,
            }
        )

    #
    # Items
    #

    def search_items(
        self,
        page: int,
    ) -> str:

        return self._post(
            {
                "search": 1,
                "pagenumber": page,
                "keywords": "",
                "filter": "ALL",
                "itemCase": "g",
                "searchcase": "NAME",
            }
        )

    #
    # Images
    #

    def download(
        self,
        url: str,
        target: Path,
    ) -> None:

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


client = SageClient()