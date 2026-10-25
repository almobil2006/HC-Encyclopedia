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
            # RUNES
            #

            conn.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS runes
                    (
                        code TEXT PRIMARY KEY,

                        rune_id INTEGER,

                        name_en TEXT,
                        name_ru TEXT,

                        rune_type TEXT,

                        event_name TEXT,
                        event_date TEXT,
                        collection TEXT,

                        source TEXT,

                        image TEXT,
                        source_url TEXT,
                        image_local TEXT,

                        description_tank TEXT,
                        description_mage TEXT,
                        description_archer TEXT,

                        page_url TEXT,

                        cached INTEGER DEFAULT 0,

                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
            )

            #
            # UNITS — юниты игрока
            #

            conn.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS units
                    (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,

                        name TEXT,
                        fighter_type TEXT DEFAULT '',
                        level INTEGER,

                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
            )

            #
            # UNITS migration
            #

            unit_columns = {
                "set_code": "TEXT DEFAULT ''",
            }

            existing = {
                row[1]
                for row in conn.execute(
                    text("PRAGMA table_info(units)")
                )
            }

            for column, column_type in unit_columns.items():

                if column not in existing:

                    conn.execute(
                        text(
                            f"""
                            ALTER TABLE units
                            ADD COLUMN {column} {column_type}
                            """
                        )
                    )

            #
            # UNIT ITEMS — надетые предметы
            #

            conn.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS unit_items
                    (
                        unit_id INTEGER,
                        slot TEXT,
                        item_code TEXT,

                        UNIQUE (unit_id, slot)
                    )
                    """
                )
            )

            #
            # RECOMMENDED ITEMS
            #

            conn.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS recommended_items
                    (
                        set_code TEXT,
                        item_code TEXT,
                        item_name TEXT,
                        fighter_type TEXT,
                        rarity TEXT,
                        slot TEXT,
                        item_url TEXT,
                        image TEXT,
                        source_url TEXT,
                        image_local TEXT,
                        position INTEGER DEFAULT 0
                    )
                    """
                )
            )

            conn.execute(
                text(
                    """
                    CREATE INDEX IF NOT EXISTS
                        idx_recommended_items_set
                    ON recommended_items (set_code)
                    """
                )
            )

            #
            # ITEMS migration
            #

            item_columns = {
                "gear_id": "INTEGER",
                "item_id": "INTEGER",
                "quality": "TEXT",
                "min_level": "INTEGER",
                "max_level": "INTEGER",
                "skin_image": "TEXT",
                "skin_source_url": "TEXT",
                "skin_local": "TEXT",
                "critical": "TEXT",
                "accuracy": "TEXT",
                "ability_name": "TEXT",
                "ability_description": "TEXT",
                "trigger": "TEXT",
                "source": "TEXT",
                "page_url": "TEXT",
                "cached": "INTEGER DEFAULT 0",
                "owned": "INTEGER DEFAULT 0",
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
                "substance_red_2": "TEXT",
                "substance_red_4": "TEXT",
                "substance_red_6": "TEXT",
                "substance_yellow_2": "TEXT",
                "substance_yellow_4": "TEXT",
                "substance_yellow_6": "TEXT",
                "substance_purple_2": "TEXT",
                "substance_purple_4": "TEXT",
                "substance_purple_6": "TEXT",
                "essence_name": "TEXT",
                "material1_name": "TEXT",
                "material2_name": "TEXT",
                "material3_name": "TEXT",
                "material4_name": "TEXT",
                "essence_image": "TEXT",
                "material1_image": "TEXT",
                "material2_image": "TEXT",
                "material3_image": "TEXT",
                "material4_image": "TEXT",
                "recommended_items": "TEXT",
                "mgbot_id": "INTEGER",
                "mgbot_elements": "TEXT",
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