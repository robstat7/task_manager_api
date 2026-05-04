-- migrate:up
PRAGMA foreign_keys = OFF;

CREATE TABLE task_new (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  status TEXT DEFAULT 'pending',
  user_id INTEGER NOT NULL,
  FOREIGN KEY (user_id) REFERENCES user (id)
);

DROP TABLE task;

ALTER TABLE task_new RENAME TO task;

PRAGMA foreign_keys = ON;


-- migrate:down
PRAGMA foreign_keys = OFF;

ALTER TABLE task RENAME to task_new;

CREATE TABLE task (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  status TEXT DEFAULT 'pending'
);

DROP TABLE task_new;

PRAGMA foreign_keys = ON;
