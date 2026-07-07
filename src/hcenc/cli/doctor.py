import sqlite3
import sys

from rich import print

from hcenc.core.app import app


def doctor() -> None:
    """Check project environment."""

    print("[bold cyan]HC Encyclopedia Doctor[/bold cyan]")
    print()

    print(f"Python : {sys.version.split()[0]}")
    print(f"SQLite : {sqlite3.sqlite_version}")
    print()

    paths = {
        "Database": app.config.database,
        "Profiles": app.config.profiles,
        "Cache": app.config.cache,
        "Images": app.config.images,
    }

    for name, path in paths.items():
        exists = path.exists()

        icon = "✓" if exists else "✗"
        color = "green" if exists else "red"

        print(f"[{color}]{icon}[/{color}] {name:<10} {path}")
