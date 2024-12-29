-- Create tables for F1 data

-- Circuits table
CREATE TABLE IF NOT EXISTS circuits (
    circuit_id SERIAL PRIMARY KEY,
    circuit_name VARCHAR(255) NOT NULL,
    circuit_ref VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    country VARCHAR(255)
);

-- Races table
CREATE TABLE IF NOT EXISTS races (
    race_id SERIAL PRIMARY KEY,
    year INTEGER NOT NULL,
    round INTEGER NOT NULL,
    circuit_id INTEGER REFERENCES circuits(circuit_id),
    race_date DATE NOT NULL,
    race_name VARCHAR(255) NOT NULL
);

-- Drivers table
CREATE TABLE IF NOT EXISTS drivers (
    driver_id SERIAL PRIMARY KEY,
    driver_ref VARCHAR(255) NOT NULL,
    number INTEGER,
    code VARCHAR(3),
    forename VARCHAR(255) NOT NULL,
    surname VARCHAR(255) NOT NULL,
    nationality VARCHAR(255)
);

-- Constructors table
CREATE TABLE IF NOT EXISTS constructors (
    constructor_id SERIAL PRIMARY KEY,
    constructor_ref VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    nationality VARCHAR(255)
);

-- Qualifying table
CREATE TABLE IF NOT EXISTS qualifying (
    qualifying_id SERIAL PRIMARY KEY,
    race_id INTEGER REFERENCES races(race_id),
    driver_id INTEGER REFERENCES drivers(driver_id),
    constructor_id INTEGER REFERENCES constructors(constructor_id),
    position INTEGER,
    q1_time INTERVAL,
    q2_time INTERVAL,
    q3_time INTERVAL
);

-- Sample data for Monaco 2023
INSERT INTO circuits (circuit_name, circuit_ref, location, country) VALUES
('Monaco', 'monaco', 'Monte Carlo', 'Monaco');

INSERT INTO races (year, round, circuit_id, race_date, race_name) VALUES
(2023, 6, 1, '2023-05-28', '2023 Monaco Grand Prix');

INSERT INTO drivers (driver_ref, number, code, forename, surname, nationality) VALUES
('max_verstappen', 1, 'VER', 'Max', 'Verstappen', 'Dutch'),
('lewis_hamilton', 44, 'HAM', 'Lewis', 'Hamilton', 'British');

INSERT INTO constructors (constructor_ref, name, nationality) VALUES
('red_bull', 'Red Bull Racing', 'Austrian'),
('mercedes', 'Mercedes', 'German');

INSERT INTO qualifying (race_id, driver_id, constructor_id, position, q1_time, q2_time, q3_time) VALUES
(1, 1, 1, 1, '1:12.386', '1:11.908', '1:11.365'),
(1, 2, 2, 3, '1:12.872', '1:12.156', '1:12.012'); 