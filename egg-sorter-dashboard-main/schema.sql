CREATE TABLE IF NOT EXISTS eggs_tbl (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    weight REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expected_expiry TIMESTAMP DEFAULT (DATETIME('now', '+14 days')) NOT NULL
);

-- INSERT INTO eggs_tbl (weight, created_at) VALUES
-- -- Dates in late October 2023
-- (55.2, '2023-10-28 08:15:00'),
-- (58.1, '2023-10-28 08:15:00'), -- Same day, later time
-- (52.0, '2023-10-28 08:15:00'), -- Next day

-- -- Dates in early November 2023
-- (57.8, '2023-11-01 07:50:00'), -- Few days later
-- (59.0, '2023-11-01 07:50:00'),
-- (53.3, '2023-11-01 07:50:00'),

-- -- Dates in mid November 2023
-- (60.1, '2023-11-01 07:51:00'),
-- (56.7, '2023-11-01 07:51:00'),
-- (62.4, '2023-11-01 07:51:00');