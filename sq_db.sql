CREATE TABLE IF NOT EXISTS USERS(
    id integer PRIMARY KEY AUTOINCREMENT,
    login text NOT NULL,
    password text NOT NULL,
    email text NOT NULL
);
CREATE TABLE IF NOT EXISTS MENU(
    id integer PRIMARY KEY AUTOINCREMENT,
    name text NOT NULL,
    url text NOT NULL
);
CREATE TABLE IF NOT EXISTS OFFMENU(
    id integer PRIMARY KEY AUTOINCREMENT,
    name text NOT NULL,
    url text NOT NULL
);
CREATE TABLE IF NOT EXISTS POSTS(
    id integer PRIMARY KEY AUTOINCREMENT,
    title text NOT NULL,
    text text NOT NULL,
    url text NOT NULL,
    time integer NOT NULL
);
