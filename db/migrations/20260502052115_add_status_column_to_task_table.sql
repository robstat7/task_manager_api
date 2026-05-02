-- migrate:up
ALTER TABLE task ADD COLUMN status TEXT DEFAULT 'pending';


-- migrate:down
ALTER TABLE task DROP COLUMN status;

