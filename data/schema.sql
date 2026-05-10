CREATE DATABASE healthcare_db;
\c healthcare_db;

CREATE TABLE dim_hospital (
    hospital_id SERIAL PRIMARY KEY,
    hospital_name VARCHAR(100) NOT NULL,
    lhd_name VARCHAR(100) NOT NULL,
    hospital_type VARCHAR(50),
    bed_count INTEGER
);

CREATE TABLE dim_ward (
    ward_id SERIAL PRIMARY KEY,
    hospital_id INTEGER REFERENCES dim_hospital(hospital_id),
    ward_name VARCHAR(100) NOT NULL,
    ward_type VARCHAR(50),
    bed_capacity INTEGER
);

CREATE TABLE dim_triage (
    triage_id SERIAL PRIMARY KEY,
    triage_category INTEGER NOT NULL,
    triage_name VARCHAR(50) NOT NULL,
    max_wait_minutes INTEGER NOT NULL
);

CREATE TABLE dim_date (
    date_id SERIAL PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,
    day_of_week INTEGER,
    day_name VARCHAR(10),
    month INTEGER,
    month_name VARCHAR(10),
    quarter INTEGER,
    financial_year VARCHAR(10),
    is_weekend BOOLEAN,
    is_public_holiday BOOLEAN
);

CREATE TABLE fact_ed_visits (
    visit_id SERIAL PRIMARY KEY,
    hospital_id INTEGER REFERENCES dim_hospital(hospital_id),
    ward_id INTEGER REFERENCES dim_ward(ward_id),
    triage_id INTEGER REFERENCES dim_triage(triage_id),
    date_id INTEGER REFERENCES dim_date(date_id),
    arrival_time TIMESTAMP NOT NULL,
    triage_time TIMESTAMP,
    treatment_start_time TIMESTAMP,
    departure_time TIMESTAMP,
    wait_time_minutes INTEGER,
    treatment_time_minutes INTEGER,
    total_los_minutes INTEGER,
    departure_status VARCHAR(50),
    four_hour_breach BOOLEAN,
    patient_age INTEGER,
    patient_gender VARCHAR(10)
);

CREATE INDEX idx_ed_visits_hospital ON fact_ed_visits(hospital_id);
CREATE INDEX idx_ed_visits_date ON fact_ed_visits(date_id);
CREATE INDEX idx_ed_visits_triage ON fact_ed_visits(triage_id);
CREATE INDEX idx_ed_visits_ward ON fact_ed_visits(ward_id);
