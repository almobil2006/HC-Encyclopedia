import json

import requests

from hcenc.core.app import app


class MgBotClient:

    BASE = (
        "https://mg-bot.ru/static/wiki/hustle-castle"
    )

    def __init__(self):

        self.session = requests.Session()

        self.session.headers[
            "User-Agent"
        ] = "Mozilla/5.0 Chrome/131.0"

    def fetch(
        self,
        lang: str,
        name: str,
    ) -> dict | list | None:

        cache = (
            app.config.cache / "mgbot"
        )

        cache.mkdir(
            parents=True,
            exist_ok=True,
        )

        cache_file = (
            cache
            / f"{lang}_{name.replace('/', '_')}"
        )

        #
        # сквозной кэш: повторные синки
        # не качают одно и то же
        #

        if cache_file.exists():

            try:

                return json.loads(
                    cache_file.read_text(
                        encoding="utf-8",
                    )
                )

            except ValueError:
                pass

        url = (
            f"{self.BASE}/{lang}/{name}"
            "?v=1"
        )

        response = self.session.get(
            url,
            timeout=30,
        )

        if response.status_code != 200:
            return None

        cache_file.write_text(
            response.text,
            encoding="utf-8",
        )

        return response.json()

    def index(
        self,
        lang: str,
    ) -> dict | None:

        return self.fetch(lang, "index.json")

    def set_file(
        self,
        lang: str,
        set_id: int,
    ) -> dict | None:

        return self.fetch(
            lang,
            f"sets/s{set_id}.json",
        )


mgbot_client = MgBotClient()
