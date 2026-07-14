ALTER TABLE recommended_items
ADD COLUMN image TEXT DEFAULT '';

ALTER TABLE recommended_items
ADD COLUMN source_url TEXT DEFAULT '';

ALTER TABLE recommended_items
ADD COLUMN image_local TEXT DEFAULT '';