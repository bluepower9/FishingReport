DROP TABLE trips;
DROP TABLE counts;

CREATE TABLE IF NOT EXISTS trips (
    id INTEGER PRIMARY KEY,
    date TEXT NOT NULL,
    anglers INTEGER NOT NULL,
    boat TEXT NOT NULL,
    port TEXT NOT NULL,
    days FLOAT NOT NULL
);

CREATE TABLE IF NOT EXISTS counts (
    id INTEGER PRIMARY KEY,
    trip_id INTEGER NOT NULL,
    fish TEXT NOT NULL,
    count INTEGER NOT NULL,

    FOREIGN KEY (trip_id) REFERENCES trips(id)
);
