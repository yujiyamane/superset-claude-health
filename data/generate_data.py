import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

HOSPITALS = [
    (1, "Royal Prince Alfred Hospital", "Sydney", "Tertiary", 600),
    (2, "Sydney Hospital", "Sydney", "Metropolitan", 200),
    (3, "Westmead Hospital", "Western Sydney", "Tertiary", 800),
    (4, "Blacktown Hospital", "Western Sydney", "Metropolitan", 350),
    (5, "Liverpool Hospital", "South Western Sydney", "Tertiary", 700),
    (6, "Campbelltown Hospital", "South Western Sydney", "Metropolitan", 400),
    (7, "St George Hospital", "South Eastern Sydney", "Tertiary", 550),
    (8, "Prince of Wales Hospital", "South Eastern Sydney", "Metropolitan", 450),
    (9, "Royal North Shore Hospital", "Northern Sydney", "Tertiary", 650),
    (10, "Mona Vale Hospital", "Northern Sydney", "District", 150),
]

WARD_TYPES = [
    "Emergency", "General", "ICU", "Surgical", "Medical",
    "Maternity", "Paediatric", "Mental Health", "Rehabilitation", "Oncology",
]

TRIAGE_DATA = [
    (1, 1, "Immediate", 0),
    (2, 2, "Emergency", 10),
    (3, 3, "Urgent", 30),
    (4, 4, "Semi-urgent", 60),
    (5, 5, "Non-urgent", 120),
]

DEPARTURE_STATUSES = ["Discharged", "Admitted", "Transferred", "Did Not Wait", "Deceased"]
DEPARTURE_WEIGHTS = [0.60, 0.25, 0.08, 0.06, 0.01]

PATIENT_GENDERS = ["Male", "Female", "Other"]
GENDER_WEIGHTS = [0.485, 0.485, 0.03]

TRIAGE_WAIT_PARAMS = {
    1: {"mu": 1.0, "sigma": 0.3, "scale": 1.5},
    2: {"mu": 1.8, "sigma": 0.4, "scale": 4.0},
    3: {"mu": 2.5, "sigma": 0.5, "scale": 12.0},
    4: {"mu": 3.0, "sigma": 0.5, "scale": 30.0},
    5: {"mu": 3.3, "sigma": 0.5, "scale": 55.0},
}

TRIAGE_WEIGHTS = [0.03, 0.10, 0.30, 0.35, 0.22]


def _make_dim_hospital():
    rows = []
    for h_id, name, lhd, h_type, beds in HOSPITALS:
        rows.append({
            "hospital_id": h_id,
            "hospital_name": name,
            "lhd_name": lhd,
            "hospital_type": h_type,
            "bed_count": beds,
        })
    return pd.DataFrame(rows)


def _make_dim_ward():
    rows = []
    ward_id = 1
    for h_id, _, _, _, _ in HOSPITALS:
        for w_type in WARD_TYPES:
            rows.append({
                "ward_id": ward_id,
                "hospital_id": h_id,
                "ward_name": f"{w_type} Ward {h_id}",
                "ward_type": w_type,
                "bed_capacity": np.random.randint(10, 60),
            })
            ward_id += 1
    return pd.DataFrame(rows)


def _make_dim_triage():
    rows = []
    for t_id, t_cat, t_name, max_wait in TRIAGE_DATA:
        rows.append({
            "triage_id": t_id,
            "triage_category": t_cat,
            "triage_name": t_name,
            "max_wait_minutes": max_wait,
        })
    return pd.DataFrame(rows)


def _make_dim_date(start_date: datetime, n_days: int):
    rows = []
    aus_public_holidays = {
        "2024-07-05", "2024-08-05", "2024-09-23", "2024-10-07",
        "2024-11-05", "2024-12-25", "2024-12-26", "2025-01-01",
        "2025-01-27", "2025-04-18", "2025-04-19", "2025-04-21",
        "2025-04-25", "2025-06-09", "2025-07-04", "2025-08-04",
        "2025-09-22", "2025-10-06", "2025-11-04", "2025-12-25",
        "2025-12-26", "2026-01-01", "2026-01-26", "2026-04-03",
        "2026-04-04", "2026-04-06", "2026-04-25", "2026-06-08",
    }
    for i in range(n_days):
        d = start_date + timedelta(days=i)
        fy = f"FY{d.year}-{str(d.year + 1)[-2:]}" if d.month >= 7 else f"FY{d.year - 1}-{str(d.year)[-2:]}"
        rows.append({
            "date_id": i + 1,
            "full_date": d.date(),
            "day_of_week": d.weekday(),
            "day_name": d.strftime("%A"),
            "month": d.month,
            "month_name": d.strftime("%B"),
            "quarter": (d.month - 1) // 3 + 1,
            "financial_year": fy,
            "is_weekend": d.weekday() >= 5,
            "is_public_holiday": d.strftime("%Y-%m-%d") in aus_public_holidays,
        })
    return pd.DataFrame(rows)


def _bimodal_arrival_hour(rng, n):
    mask = rng.random(n) < 0.55
    morning = rng.normal(10, 2, n).clip(6, 14).astype(int)
    evening = rng.normal(20, 2, n).clip(15, 23).astype(int)
    return np.where(mask, morning, evening)


def _make_fact_ed_visits(dim_hospital, dim_ward, dim_date, rng):
    n_days = len(dim_date)
    hospital_ids = dim_hospital["hospital_id"].values
    ward_df = dim_ward.copy()

    records = []
    visit_id = 1

    for _, date_row in dim_date.iterrows():
        date_id = int(date_row["date_id"])
        full_date = pd.Timestamp(date_row["full_date"])
        is_weekend = date_row["is_weekend"]
        base_visits = rng.integers(220, 320) if not is_weekend else rng.integers(270, 380)

        h_ids = rng.choice(hospital_ids, size=base_visits)
        triage_ids = rng.choice([1, 2, 3, 4, 5], size=base_visits, p=TRIAGE_WEIGHTS)
        ages = rng.integers(1, 95, size=base_visits)
        genders = rng.choice(PATIENT_GENDERS, size=base_visits, p=GENDER_WEIGHTS)
        arrival_hours = _bimodal_arrival_hour(rng, base_visits)
        arrival_mins = rng.integers(0, 60, size=base_visits)

        for i in range(base_visits):
            h_id = int(h_ids[i])
            t_id = int(triage_ids[i])
            params = TRIAGE_WAIT_PARAMS[t_id]

            wait_raw = np.exp(rng.normal(params["mu"], params["sigma"])) * params["scale"]
            wait_minutes = max(0, int(round(wait_raw)))

            treatment_minutes = max(10, int(round(np.exp(rng.normal(3.5, 0.6)))))
            total_los = wait_minutes + treatment_minutes

            four_hour_breach = total_los > 240

            arrival_dt = full_date + pd.Timedelta(hours=int(arrival_hours[i]), minutes=int(arrival_mins[i]))
            triage_dt = arrival_dt + pd.Timedelta(minutes=rng.integers(1, 5))
            treatment_start = arrival_dt + pd.Timedelta(minutes=wait_minutes)
            departure_dt = treatment_start + pd.Timedelta(minutes=treatment_minutes)

            ward_options = ward_df[ward_df["hospital_id"] == h_id]["ward_id"].values
            w_id = int(rng.choice(ward_options))

            dep_status = rng.choice(DEPARTURE_STATUSES, p=DEPARTURE_WEIGHTS)

            records.append({
                "visit_id": visit_id,
                "hospital_id": h_id,
                "ward_id": w_id,
                "triage_id": t_id,
                "date_id": date_id,
                "arrival_time": arrival_dt,
                "triage_time": triage_dt,
                "treatment_start_time": treatment_start,
                "departure_time": departure_dt,
                "wait_time_minutes": wait_minutes,
                "treatment_time_minutes": treatment_minutes,
                "total_los_minutes": total_los,
                "departure_status": dep_status,
                "four_hour_breach": four_hour_breach,
                "patient_age": int(ages[i]),
                "patient_gender": genders[i],
            })
            visit_id += 1

    return pd.DataFrame(records)


def generate_all(data_dir: str, seed: int = 42):
    rng = np.random.default_rng(seed)
    np.random.seed(seed)

    os.makedirs(data_dir, exist_ok=True)

    dim_hospital = _make_dim_hospital()
    dim_ward = _make_dim_ward()
    dim_triage = _make_dim_triage()

    start_date = datetime(2024, 7, 1)
    dim_date = _make_dim_date(start_date, 730)

    fact_ed = _make_fact_ed_visits(dim_hospital, dim_ward, dim_date, rng)

    dim_hospital.to_csv(os.path.join(data_dir, "dim_hospital.csv"), index=False)
    dim_ward.to_csv(os.path.join(data_dir, "dim_ward.csv"), index=False)
    dim_triage.to_csv(os.path.join(data_dir, "dim_triage.csv"), index=False)
    dim_date.to_csv(os.path.join(data_dir, "dim_date.csv"), index=False)
    fact_ed.to_csv(os.path.join(data_dir, "fact_ed_visits.csv"), index=False)


if __name__ == "__main__":
    base = os.path.dirname(__file__)
    generate_all(base)
    print("Data generation complete.")
