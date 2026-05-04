-- migrate:up
ALTER TABLE task ADD COLUMN description TEXT;


-- migrate:down
ALTER TABLE task DROP COLUMN description;
