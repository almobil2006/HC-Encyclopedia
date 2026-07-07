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
