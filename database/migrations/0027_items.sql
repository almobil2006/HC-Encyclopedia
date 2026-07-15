CREATE TABLE IF NOT EXISTS items
(
    ------------------------------------------------------------------
    -- Primary key
    ------------------------------------------------------------------

    code TEXT PRIMARY KEY,

    item_id INTEGER,

    ------------------------------------------------------------------
    -- Names
    ------------------------------------------------------------------

    name_en TEXT DEFAULT '',
    name_ru TEXT DEFAULT '',

    ------------------------------------------------------------------
    -- Classification
    ------------------------------------------------------------------

    fighter_type TEXT DEFAULT '',
    rarity TEXT DEFAULT '',
    slot TEXT DEFAULT '',
    quality TEXT DEFAULT '',

    ------------------------------------------------------------------
    -- Levels
    ------------------------------------------------------------------

    min_level INTEGER,
    max_level INTEGER,

    ------------------------------------------------------------------
    -- Images
    ------------------------------------------------------------------

    image TEXT DEFAULT '',
    source_url TEXT DEFAULT '',
    image_local TEXT DEFAULT '',

    skin_image TEXT DEFAULT '',
    skin_source_url TEXT DEFAULT '',
    skin_local TEXT DEFAULT '',

    ------------------------------------------------------------------
    -- Description
    ------------------------------------------------------------------

    description_en TEXT DEFAULT '',
    description_ru TEXT DEFAULT '',

    ------------------------------------------------------------------
    -- Stats
    ------------------------------------------------------------------

    health TEXT DEFAULT '',
    damage TEXT DEFAULT '',
    armor TEXT DEFAULT '',
    magic_armor TEXT DEFAULT '',

    dodge TEXT DEFAULT '',
    critical TEXT DEFAULT '',
    accuracy TEXT DEFAULT '',

    spell_power TEXT DEFAULT '',
    healing TEXT DEFAULT '',

    ------------------------------------------------------------------
    -- Ability
    ------------------------------------------------------------------

    ability_name TEXT DEFAULT '',
    ability_description TEXT DEFAULT '',

    cooldown TEXT DEFAULT '',
    trigger TEXT DEFAULT '',

    ------------------------------------------------------------------
    -- Source
    ------------------------------------------------------------------

    source TEXT DEFAULT '',

    page_url TEXT DEFAULT '',

    ------------------------------------------------------------------
    -- Service
    ------------------------------------------------------------------

    cached INTEGER DEFAULT 0,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_items_item_id
ON items(item_id);

CREATE INDEX IF NOT EXISTS idx_items_slot
ON items(slot);

CREATE INDEX IF NOT EXISTS idx_items_fighter_type
ON items(fighter_type);

CREATE INDEX IF NOT EXISTS idx_items_rarity
ON items(rarity);