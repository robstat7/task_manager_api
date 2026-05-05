-- migrate:up
ALTER TABLE task ADD COLUMN category TEXT;


-- migrate:down
ALTER TABLE task DROP COLUMN category;
