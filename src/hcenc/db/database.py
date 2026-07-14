from sqlalchemy import text

from hcenc.db.engine import engine


class Database:

    def initialize(self) -> None:

        with engine.begin() as conn:

            #
            # ITEMS
            #

            conn.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS items
                    (
                        code TEXT PRIMARY KEY,

                        gear_id INTEGER,

                        name_en TEXT,
                        name_ru TEXT,

                        type_en TEXT,
                        type_ru TEXT,

                        fighter_type TEXT,

                        rarity TEXT,
                        slot TEXT,
                        class_name TEXT,

                        event_name TEXT,
                        obtained_from TEXT,
                        last_seen TEXT,

                        image TEXT,
                        source_url TEXT,
                        image_local TEXT,

                        description_en TEXT,
                        description_ru TEXT,

                        sage_bot_code TEXT,
                        user_rating TEXT,
                        requirements TEXT,
                        first_trigger TEXT,
                        cooldown TEXT,

                        health TEXT,
                        armor TEXT,
                        magic_armor TEXT,
                        damage TEXT,
                        spell_power TEXT,
                        dodge TEXT,
                        crit TEXT,
                        crit_damage TEXT,
                        attack_speed TEXT,
                        healing TEXT,
                        vampirism TEXT,

                        effects TEXT,

                        set_code TEXT,

                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
            )

            #
            # SETS
            #

            conn.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS sets
                    (
                        code TEXT PRIMARY KEY,

                        set_id INTEGER,

                        name_en TEXT,
                        name_ru TEXT,

                        fighter_type TEXT,
                        event_name TEXT,

                        image TEXT,
                        source_url TEXT,
                        image_local TEXT,

                        description_en TEXT,
                        description_ru TEXT,

                        bonus_2 TEXT,
                        bonus_4 TEXT,
                        bonus_6 TEXT,

                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
            )

            #
            # ITEMS migration
            #

            item_columns = {
                "gear_id": "INTEGER",
                "rarity": "TEXT",
                "slot": "TEXT",
                "class_name": "TEXT",
                "source_url": "TEXT",
                "image_local": "TEXT",
                "obtained_from": "TEXT",
                "last_seen": "TEXT",
                "sage_bot_code": "TEXT",
                "user_rating": "TEXT",
                "requirements": "TEXT",
                "first_trigger": "TEXT",
                "cooldown": "TEXT",
                "health": "TEXT",
                "armor": "TEXT",
                "magic_armor": "TEXT",
                "damage": "TEXT",
                "spell_power": "TEXT",
                "dodge": "TEXT",
                "crit": "TEXT",
                "crit_damage": "TEXT",
                "attack_speed": "TEXT",
                "healing": "TEXT",
                "vampirism": "TEXT",
                "effects": "TEXT",
                "set_code": "TEXT",
            }

            existing = {
                row[1]
                for row in conn.execute(
                    text("PRAGMA table_info(items)")
                )
            }

            for column, column_type in item_columns.items():

                if column not in existing:

                    conn.execute(
                        text(
                            f"""
                            ALTER TABLE items
                            ADD COLUMN {column} {column_type}
                            """
                        )
                    )

            #
            # SETS migration
            #

            set_columns = {
                "set_id": "INTEGER",
                "fighter_type": "TEXT",
                "event_name": "TEXT",
                "source_url": "TEXT",
                "image_local": "TEXT",
                "description_en": "TEXT",
                "description_ru": "TEXT",
                "bonus_2": "TEXT",
                "bonus_4": "TEXT",
                "bonus_6": "TEXT",
            }

            existing = {
                row[1]
                for row in conn.execute(
                    text("PRAGMA table_info(sets)")
                )
            }

            for column, column_type in set_columns.items():

                if column not in existing:

                    conn.execute(
                        text(
                            f"""
                            ALTER TABLE sets
                            ADD COLUMN {column} {column_type}
                            """
                        )
                    )


database = Database()