CREATE TABLE IF NOT EXISTS USERS(
    id integer PRIMARY KEY AUTOINCREMENT,
    login text NOT NULL,
    password text NOT NULL,
    email text NOT NULL,
    avatar BLOB DEFAULT NULL,
    time integer NOT NULL
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
    userid integer,
    time integer NOT NULL
);
CREATE TABLE IF NOT EXISTS COMMENTS(
    id integer PRIMARY KEY AUTOINCREMENT,
    text text NOT NULL,
    postname text NOT NULL,
    username text NOT NULL,
    time integer NOT NULL,
    FOREIGN KEY(postname) REFERENCES POSTS(title)
    FOREIGN KEY(username) REFERENCES USERS(login)
);
