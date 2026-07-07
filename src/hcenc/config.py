from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Config:
    root: Path

    @property
    def database(self) -> Path:
        return self.root / "database"

    @property
    def migrations(self) -> Path:
        return self.database / "migrations"

    @property
    def profiles(self) -> Path:
        return self.root / "profiles"

    @property
    def assets(self) -> Path:
        return self.root / "assets"

    @property
    def cache(self) -> Path:
        return self.assets / "cache"

    @property
    def images(self) -> Path:
        return self.assets / "images"


config = Config(
    root=Path.cwd(),
)
