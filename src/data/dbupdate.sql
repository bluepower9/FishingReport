DROP TABLE fish;
DROP TABLE boats;
DROP TABLE ports;

CREATE TABLE IF NOT EXISTS fish (
    id INTEGER PRIMARY KEY,
    fish TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS boats (
    id INTEGER PRIMARY KEY,
    boat TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ports (
    id INTEGER PRIMARY KEY,
    port TEXT NOT NULL
);


INSERT INTO fish(fish) SELECT DISTINCT fish FROM counts;
INSERT INTO boats(boat) SELECT DISTINCT boat FROM trips;
INSERT INTO ports(port) SELECT DISTINCT port FROM trips;


-- changes fish column in counts to an int and maps it to fish table
ALTER TABLE counts RENAME COLUMN fish TO fishtmp;
ALTER TABLE counts DROP fish;
ALTER TABLE counts ADD fish INTEGER REFERENCES fish(id);

UPDATE counts SET fish = fish.id
FROM fish WHERE fish.fish = counts.fishtmp;

ALTER TABLE counts DROP fishtmp;



-- changes boats column into int and maps to new boat table
ALTER TABLE trips RENAME COLUMN boat TO boattmp;
ALTER TABLE trips DROP boat;
ALTER TABLE trips ADD boat INTEGER REFERENCES boats(id);

UPDATE trips SET boat = boats.id
FROM boats WHERE boats.boat = trips.boattmp;

ALTER TABLE trips DROP boattmp;



-- changes port column into int and maps to new ports table
ALTER TABLE trips RENAME COLUMN port TO porttmp;
ALTER TABLE trips DROP port;
ALTER TABLE trips ADD port INTEGER REFERENCES ports(id);

UPDATE trips SET port = ports.id
FROM ports WHERE ports.port = trips.porttmp;

ALTER TABLE trips DROP porttmp;
