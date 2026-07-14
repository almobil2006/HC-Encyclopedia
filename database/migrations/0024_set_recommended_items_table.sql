CREATE TABLE IF NOT EXISTS set_recommended_items
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    set_code TEXT NOT NULL,

    item_code TEXT,

    name_en TEXT,

    fighter_type TEXT,

    rarity TEXT,

    slot TEXT,

    image TEXT,

    source_url TEXT,

    position INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS
idx_set_recommended_items_set
ON set_recommended_items(set_code);

CREATE INDEX IF NOT EXISTS
idx_set_recommended_items_item
ON set_recommended_items(item_code);