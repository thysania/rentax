PRAGMA foreign_keys = ON;

-------------------------------------------------
-- OWNERS
-------------------------------------------------
CREATE TABLE IF NOT EXISTS owners (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT,
    legal_id TEXT,
    family_count INTEGER DEFAULT 0
);

-------------------------------------------------
-- CLIENTS
-------------------------------------------------
CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT,
    legal_id TEXT,
    client_type TEXT NOT NULL CHECK (client_type IN ('PP','PM'))
);

-------------------------------------------------
-- UNITS
-------------------------------------------------
CREATE TABLE IF NOT EXISTS units (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reference TEXT NOT NULL,
    city TEXT,
    neighborhood TEXT,
    floor INTEGER,
    unit_type TEXT CHECK (unit_type IN ('apt','store','building'))
);

-------------------------------------------------
-- OWNERSHIP (supports shared + alternating)
-------------------------------------------------
CREATE TABLE IF NOT EXISTS ownerships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    unit_id INTEGER NOT NULL,
    owner_id INTEGER NOT NULL,
    share_percent REAL NOT NULL CHECK (share_percent > 0 AND share_percent <= 100),
    alternate INTEGER DEFAULT 0 CHECK (alternate IN (0,1)),
    odd_even TEXT CHECK (odd_even IN ('odd','even')),
    FOREIGN KEY (unit_id) REFERENCES units(id),
    FOREIGN KEY (owner_id) REFERENCES owners(id)
);

-------------------------------------------------
-- ASSIGNMENTS (CONTRACTS)
-------------------------------------------------
CREATE TABLE IF NOT EXISTS assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    unit_id INTEGER NOT NULL,
    client_id INTEGER NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT,
    rent_amount REAL NOT NULL,
    ras_ir INTEGER DEFAULT 0 CHECK (ras_ir IN (0,1)),
    FOREIGN KEY (unit_id) REFERENCES units(id),
    FOREIGN KEY (client_id) REFERENCES clients(id)
);

-------------------------------------------------
-- RECEIPT DEFINITIONS (STATIC)
-------------------------------------------------
CREATE TABLE IF NOT EXISTS receipts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    assignment_id INTEGER NOT NULL,
    base_label TEXT,
    FOREIGN KEY (assignment_id) REFERENCES assignments(id)
);

-------------------------------------------------
-- RECEIPT LOG (HISTORY / IMMUTABLE)
-------------------------------------------------
CREATE TABLE IF NOT EXISTS receipt_log (
    uid INTEGER PRIMARY KEY AUTOINCREMENT,
    receipt_id INTEGER NOT NULL,
    assignment_id INTEGER NOT NULL,
    owner_id INTEGER NOT NULL,
    client_id INTEGER NOT NULL,
    receipt_no INTEGER NOT NULL,
    period TEXT NOT NULL,
    issue_date TEXT NOT NULL,
    amount REAL NOT NULL,
    FOREIGN KEY (receipt_id) REFERENCES receipts(id),
    FOREIGN KEY (assignment_id) REFERENCES assignments(id),
    FOREIGN KEY (owner_id) REFERENCES owners(id),
    FOREIGN KEY (client_id) REFERENCES clients(id)
);

-------------------------------------------------
-- PAYMENTS (records actual amounts received per receipt log)
-------------------------------------------------
CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    receipt_log_uid INTEGER NOT NULL,
    amount_received REAL NOT NULL,
    received_at TEXT,
    note TEXT,
    FOREIGN KEY (receipt_log_uid) REFERENCES receipt_log(uid)
);
