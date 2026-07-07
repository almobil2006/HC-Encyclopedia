import sqlite3
import sys

from rich import print

from hcenc.config import config


def doctor():
    """
    Check project environment.
    """

    print("[bold cyan]HC Encyclopedia Doctor[/bold cyan]")
    print()

    print(f"Python : {sys.version.split()[0]}")
    print(f"SQLite : {sqlite3.sqlite_version}")
    print()

    paths = {
        "Database": config.database_dir,
        "Profiles": config.profiles_dir,
        "Cache": config.cache_dir,
        "Images": config.images_dir,
    }

    for name, path in paths.items():
        ok = "✓" if path.exists() else "✗"
        color = "green" if path.exists() else "red"
        print(f"[{color}]{ok}[/{color}] {name:<10} {path}")
