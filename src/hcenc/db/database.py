from hcenc.core.app import app
from hcenc.db.engine import engine


class Database:
    def initialize(self) -> None:
        migrations = sorted(app.config.migrations.glob("*.sql"))

        with engine.begin() as conn:
            raw = conn.connection

            raw.execute(
                """
                CREATE TABLE IF NOT EXISTS schema_version
                (
                    version INTEGER PRIMARY KEY,
                    applied_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            current = {
                row[0]
                for row in raw.execute(
                    "SELECT version FROM schema_version"
                )
            }

            for migration in migrations:
                version = int(migration.name.split("_")[0])

                if version in current:
                    continue

                print(f"Applying {migration.name}")

                raw.executescript(
                    migration.read_text(encoding="utf-8")
                )

                raw.execute(
                    "INSERT INTO schema_version(version) VALUES(?)",
                    (version,),
                )


database = Database()
