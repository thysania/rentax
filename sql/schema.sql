PRAGMA foreign_keys = ON;

-- =====================
-- OWNERS
-- =====================
CREATE TABLE owners (
    id              INTEGER PRIMARY KEY,
    name            TEXT NOT NULL,
    phone           TEXT,
    legal_id        TEXT,              -- CIN or IF
    family_count    INTEGER DEFAULT 0
);

-- =====================
-- CLIENTS
-- =====================
CREATE TABLE clients (
    id              INTEGER PRIMARY KEY,
    name            TEXT NOT NULL,
    phone           TEXT,
    client_type     TEXT CHECK (client_type IN ('PP','PM')) NOT NULL,
    legal_id        TEXT,
    ras_ir          INTEGER DEFAULT 0   -- 0 = no, 1 = yes
);

-- =====================
-- UNITS
-- =====================
CREATE TABLE units (
    id              INTEGER PRIMARY KEY,
    name            TEXT NOT NULL,
    neighborhood    TEXT,
    floor           INTEGER,
    unit_type       TEXT CHECK (unit_type IN ('apt','store','house','office')),
    status          TEXT DEFAULT 'vacant'
);

-- =====================
-- OWNERSHIPS
-- =====================
CREATE TABLE ownerships (
    id              INTEGER PRIMARY KEY,
    unit_id         INTEGER NOT NULL,
    owner_id        INTEGER NOT NULL,
    share_percent   REAL NOT NULL,
    is_alternating  INTEGER DEFAULT 0,
    odd_even        TEXT CHECK (odd_even IN ('odd','even')),
    FOREIGN KEY (unit_id) REFERENCES units(id),
    FOREIGN KEY (owner_id) REFERENCES owners(id)
);

-- =====================
-- ASSIGNMENTS
-- =====================
CREATE TABLE assignments (
    id              INTEGER PRIMARY KEY,
    unit_id         INTEGER NOT NULL,
    client_id       INTEGER NOT NULL,
    start_date      DATE NOT NULL,
    end_date        DATE,
    rent_amount     REAL NOT NULL,
    FOREIGN KEY (unit_id) REFERENCES units(id),
    FOREIGN KEY (client_id) REFERENCES clients(id)
);

-- =====================
-- RECEIPTS
-- =====================
CREATE TABLE receipts (
    id              INTEGER PRIMARY KEY,
    assignment_id   INTEGER NOT NULL,
    ownership_id    INTEGER NOT NULL,
    period          DATE NOT NULL,
    amount          REAL NOT NULL,
    created_at      DATE DEFAULT CURRENT_DATE,
    FOREIGN KEY (assignment_id) REFERENCES assignments(id),
    FOREIGN KEY (ownership_id) REFERENCES ownerships(id)
);