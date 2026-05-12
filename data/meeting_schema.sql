CREATE TABLE IF NOT EXISTS meeting_bookings (
    booking_id SERIAL PRIMARY KEY,
    organizer_name VARCHAR(200),
    room_name VARCHAR(50),
    floor_level INTEGER,
    floor_level_name VARCHAR(20),
    subject VARCHAR(500),
    start_datetime TIMESTAMP,
    end_datetime TIMESTAMP,
    start_date DATE,
    day_of_week VARCHAR(10),
    day_of_week_number INTEGER,
    hour_ampm VARCHAR(10),
    hour_of_day INTEGER,
    duration_minutes INTEGER,
    is_cancelled BOOLEAN,
    total_available_minutes INTEGER,
    total_minutes_booked INTEGER,
    utilisation_rate DECIMAL(5,2)
);

CREATE INDEX IF NOT EXISTS idx_meeting_floor ON meeting_bookings(floor_level);
CREATE INDEX IF NOT EXISTS idx_meeting_room ON meeting_bookings(room_name);
CREATE INDEX IF NOT EXISTS idx_meeting_date ON meeting_bookings(start_date);
CREATE INDEX IF NOT EXISTS idx_meeting_dow ON meeting_bookings(day_of_week);
CREATE INDEX IF NOT EXISTS idx_meeting_hour ON meeting_bookings(hour_of_day);
