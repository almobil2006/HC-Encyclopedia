CREATE TABLE IF NOT EXISTS schema_version
(
    version INTEGER PRIMARY KEY,
    applied_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS game_info
(
    id INTEGER PRIMARY KEY,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    version TEXT NOT NULL
);

INSERT OR IGNORE INTO game_info
(
    id,
    version
)
VALUES
(
    1,
    '2.0'
);

CREATE TABLE IF NOT EXISTS items
(
    code TEXT PRIMARY KEY,

    name_en TEXT NOT NULL,
    name_ru TEXT,

    type_en TEXT,
    type_ru TEXT,

    fighter_type TEXT,

    event_name TEXT,

    image TEXT,

    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_items_type
ON items(type_en);

CREATE INDEX IF NOT EXISTS idx_items_event
ON items(event_name);
