from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Config:
    project_root: Path
    database_dir: Path
    profiles_dir: Path
    assets_dir: Path
    cache_dir: Path
    images_dir: Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

config = Config(
    project_root=PROJECT_ROOT,
    database_dir=PROJECT_ROOT / "database",
    profiles_dir=PROJECT_ROOT / "profiles",
    assets_dir=PROJECT_ROOT / "assets",
    cache_dir=PROJECT_ROOT / "assets" / "cache",
    images_dir=PROJECT_ROOT / "assets" / "images",
)
