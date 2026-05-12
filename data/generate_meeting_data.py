import os
import random
import numpy as np
import pandas as pd
from faker import Faker
from datetime import datetime, timedelta

Faker.seed(42)
random.seed(42)
np.random.seed(42)

fake = Faker("en_AU")

FLOOR_WEIGHTS = {2: 0.137, 3: 0.150, 4: 0.150, 5: 0.1739, 6: 0.060, 7: 0.110, 8: 0.1354, 9: 0.1162}

_hour_raw = {8: 0.0159, 9: 0.1299, 10: 0.15, 11: 0.12, 12: 0.04, 13: 0.1659, 14: 0.08, 15: 0.08, 16: 0.04, 17: 0.018}
_total_h = sum(_hour_raw.values())
HOUR_WEIGHTS = {k: v / _total_h for k, v in _hour_raw.items()}

DOW_MULTIPLIER = {"Mon": 1.07, "Tue": 1.07, "Wed": 1.08, "Thu": 1.35, "Fri": 0.40}
DOW_NUMBER = {"Mon": 1, "Tue": 2, "Wed": 3, "Thu": 4, "Fri": 5}
DOW_MAP = {0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu", 4: "Fri"}

DURATIONS = [15, 25, 30, 45, 60, 90, 120]
DURATION_WEIGHTS = [0.05, 0.05, 0.25, 0.20, 0.30, 0.10, 0.05]

REGIONS = ["Region A", "Region B", "Region C", "Region D", "Region E", "Central Office"]

PROJECTS = ["Alpha", "Beta", "Phoenix", "Horizon", "Delta", "Omega", "Aurora", "Nexus"]
ROLES = ["Developer", "Analyst", "Manager", "Designer", "Engineer", "Architect"]
TOPICS = ["Agile Methods", "Data Governance", "Security", "Infrastructure", "Process Improvement"]


def _format_hour(h):
    if h == 0:
        return "12 AM"
    elif h < 12:
        return f"{h} AM"
    elif h == 12:
        return "12 PM"
    else:
        return f"{h - 12} PM"


def _generate_rooms():
    rooms = []
    for floor in range(2, 10):
        for seq in range(1, 7):
            wing = "N" if seq <= 3 else "S"
            size = 4 if seq % 2 == 1 else 6
            name = f"{floor}.{wing}.{seq}-S{size}-VC"
            rooms.append({"room_name": name, "floor_level": floor, "floor_level_name": f"Level {floor}"})
    return rooms


def _generate_organizers(n=200):
    orgs = []
    for _ in range(n):
        name = fake.name()
        region = random.choice(REGIONS)
        orgs.append(f"{name} ({region})")
    return orgs


def _random_subject():
    candidates = [
        "Team Standup",
        f"Project Review - {random.choice(PROJECTS)}",
        f"1:1 with {fake.first_name()}",
        "Budget Planning",
        "Weekly Sync",
        "Training Session",
        f"Interview - {random.choice(ROLES)}",
        f"Workshop: {random.choice(TOPICS)}",
        "Board Prep",
        "Data Review",
        "Quarterly Planning",
        "Sprint Planning",
        "Retrospective",
        f"Architecture Review - {random.choice(PROJECTS)}",
        "Status Update",
    ]
    return random.choice(candidates)


def generate_all(output_dir):
    rooms = _generate_rooms()
    floor_rooms = {}
    for r in rooms:
        floor_rooms.setdefault(r["floor_level"], []).append(r)

    organizers = _generate_organizers(200)
    business_days = pd.bdate_range(start="2024-01-01", end="2026-12-31")

    floors = list(FLOOR_WEIGHTS.keys())
    floor_wts = [FLOOR_WEIGHTS[f] for f in floors]
    hours = list(HOUR_WEIGHTS.keys())
    hour_wts = [HOUR_WEIGHTS[h] for h in hours]

    BASE_DAILY = 65
    records = []
    booking_id = 1

    for day in business_days:
        dow = DOW_MAP[day.dayofweek]
        n = max(20, int(BASE_DAILY * DOW_MULTIPLIER[dow] * np.random.normal(1.0, 0.08)))

        day_floors = random.choices(floors, weights=floor_wts, k=n)
        for floor in day_floors:
            room = random.choice(floor_rooms[floor])
            hour = random.choices(hours, weights=hour_wts, k=1)[0]
            duration = random.choices(DURATIONS, weights=DURATION_WEIGHTS, k=1)[0]
            organizer = random.choice(organizers)
            subject = _random_subject()
            is_cancelled = random.random() < 0.05

            start_dt = datetime(day.year, day.month, day.day, hour, 0)
            end_dt = start_dt + timedelta(minutes=duration)

            records.append({
                "booking_id": booking_id,
                "organizer_name": organizer,
                "room_name": room["room_name"],
                "floor_level": room["floor_level"],
                "floor_level_name": room["floor_level_name"],
                "subject": subject,
                "start_datetime": start_dt,
                "end_datetime": end_dt,
                "start_date": day.date(),
                "day_of_week": dow,
                "day_of_week_number": DOW_NUMBER[dow],
                "hour_ampm": _format_hour(hour),
                "hour_of_day": hour,
                "duration_minutes": duration,
                "is_cancelled": is_cancelled,
            })
            booking_id += 1

    df = pd.DataFrame(records)

    room_day = (
        df.groupby(["room_name", "start_date"])["duration_minutes"]
        .sum()
        .reset_index()
        .rename(columns={"duration_minutes": "total_minutes_booked"})
    )
    room_day["total_available_minutes"] = 480
    room_day["utilisation_rate"] = (room_day["total_minutes_booked"] / 480 * 100).clip(0, 100)

    df = df.merge(room_day[["room_name", "start_date", "total_minutes_booked", "total_available_minutes", "utilisation_rate"]], on=["room_name", "start_date"])

    cols = [
        "booking_id", "organizer_name", "room_name", "floor_level", "floor_level_name",
        "subject", "start_datetime", "end_datetime", "start_date", "day_of_week",
        "day_of_week_number", "hour_ampm", "hour_of_day", "duration_minutes",
        "is_cancelled", "total_available_minutes", "total_minutes_booked", "utilisation_rate",
    ]
    df = df[cols]

    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, "meeting_bookings.csv")
    df.to_csv(out_path, index=False)
    print(f"Generated {len(df):,} rows -> {out_path}")
    return df


if __name__ == "__main__":
    generate_all(os.path.join(os.path.dirname(__file__)))
