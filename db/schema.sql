CREATE TABLE task (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL
, status TEXT DEFAULT 'pending');
CREATE TABLE IF NOT EXISTS "schema_migrations" (version varchar(128) primary key);
CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);
-- Dbmate schema migrations
INSERT INTO "schema_migrations" (version) VALUES
  ('20260502052115'),
  ('20260502081612');
