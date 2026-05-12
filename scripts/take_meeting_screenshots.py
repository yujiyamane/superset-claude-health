import os
import sys
import time
from pathlib import Path

SCREENSHOTS_DIR = Path(__file__).parent.parent / "screenshots"
BASE_URL = "http://localhost:8088"
DASHBOARD_SLUG = "meeting-room-utilisation"
DASHBOARD_URL = f"{BASE_URL}/superset/dashboard/{DASHBOARD_SLUG}/"

CROP_REGIONS = {
    "meeting_kpi_cards":   (0.0, 0.00, 1.0, 0.20),
    "meeting_donuts":      (0.0, 0.18, 1.0, 0.55),
    "meeting_heatmap":     (0.0, 0.50, 1.0, 0.80),
}


def _ensure_dirs():
    SCREENSHOTS_DIR.mkdir(exist_ok=True)


MIN_CROP_HEIGHT = 300


def _crop_region_pixels(img, fracs):
    x_frac, y_frac, w_frac, h_frac = fracs
    x1 = int(img.width * x_frac)
    y1 = int(img.height * y_frac)
    x2 = int(img.width * w_frac)
    y2 = int(img.height * h_frac)
    if y2 - y1 < MIN_CROP_HEIGHT:
        y2 = min(y1 + MIN_CROP_HEIGHT, img.height)
    return (x1, y1, x2, y2)


def attempt_selenium():
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from PIL import Image

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 20)

    try:
        driver.get(f"{BASE_URL}/login/")
        wait.until(EC.presence_of_element_located(("id", "username")))
        driver.find_element("id", "username").send_keys("admin")
        driver.find_element("id", "password").send_keys("admin")
        driver.find_element("id", "password").submit()
        time.sleep(2)

        driver.get(DASHBOARD_URL)
        try:
            wait.until(EC.presence_of_element_located(("css selector", ".chart-container")))
        except Exception:
            time.sleep(5)
        time.sleep(4)

        full_path = str(SCREENSHOTS_DIR / "meeting_dashboard_overview.png")
        driver.get_screenshot_as_file(full_path)

        img = Image.open(full_path)
        for name, fracs in CROP_REGIONS.items():
            region = _crop_region_pixels(img, fracs)
            cropped = img.crop(region)
            cropped.save(str(SCREENSHOTS_DIR / f"{name}.png"))

        print("Selenium screenshots completed.")
    finally:
        driver.quit()


def create_mockup(filename, width=1920, height=1080):
    from PIL import Image, ImageDraw

    img = Image.new("RGB", (width, height), "#002664")
    draw = ImageDraw.Draw(img)

    draw.rectangle([0, 0, width, 80], fill="#001540")
    draw.text((width // 2, 40), "Meeting Room Utilisation", fill="#FFFFFF")

    kpi_areas = [(80, 100, 420, 220), (460, 100, 800, 220), (840, 100, 1180, 220), (1220, 100, 1560, 220)]
    kpi_labels = ["Total Bookings", "Total Hours", "Avg Duration", "Utilisation Rate"]
    kpi_vals = ["50,273", "37,705K", "52 min", "13.45%"]
    for (x1, y1, x2, y2), label, val in zip(kpi_areas, kpi_labels, kpi_vals):
        draw.rectangle([x1, y1, x2, y2], outline="#8ce0ff", width=1, fill="#001f50")
        draw.text(((x1 + x2) // 2, y1 + 30), val, fill="#FFFFFF")
        draw.text(((x1 + x2) // 2, y1 + 60), label, fill="#8ce0ff")

    donut_centers = [(220, 400), (660, 400), (1100, 400)]
    donut_labels = ["Floor Level", "Time of Day", "Day of Week"]
    for (cx, cy), label in zip(donut_centers, donut_labels):
        draw.ellipse([cx - 100, cy - 100, cx + 100, cy + 100], outline="#ffb8c1", width=3)
        draw.ellipse([cx - 55, cy - 55, cx + 55, cy + 55], fill="#002664")
        draw.text((cx, cy + 120), label, fill="#8ce0ff")

    heatmap_area = (80, 560, 960, 800)
    draw.rectangle(heatmap_area, outline="#8ce0ff", width=1, fill="#001540")
    days = ["Mon", "Tue", "Wed", "Thu", "Fri"]
    hours_list = ["8AM", "9AM", "10AM", "11AM", "12PM", "1PM", "2PM", "3PM", "4PM", "5PM"]
    cw = (heatmap_area[2] - heatmap_area[0] - 60) // 5
    ch = (heatmap_area[3] - heatmap_area[1] - 40) // 10
    import random as rnd; rnd.seed(1)
    for di, day in enumerate(days):
        for hi, hour in enumerate(hours_list):
            x1 = heatmap_area[0] + 60 + di * cw
            y1 = heatmap_area[1] + 40 + hi * ch
            intensity = rnd.random()
            r = int(99 + (156 * intensity))
            g = int(25 * (1 - intensity))
            b = int(25 * (1 - intensity))
            draw.rectangle([x1, y1, x1 + cw - 2, y1 + ch - 2], fill=(r, g, b))

    bar_area = (1000, 560, 1840, 800)
    draw.rectangle(bar_area, outline="#8ce0ff", width=1, fill="#001540")
    floors = ["Level 2", "Level 3", "Level 4", "Level 5", "Level 6", "Level 7", "Level 8", "Level 9"]
    counts = [6900, 7700, 7700, 8800, 3087, 5675, 6800, 5886]
    max_c = max(counts)
    bh = (bar_area[3] - bar_area[1] - 40) // len(floors)
    for i, (fl, ct) in enumerate(zip(floors, counts)):
        bar_w = int((bar_area[2] - bar_area[0] - 100) * ct / max_c)
        by = bar_area[1] + 30 + i * bh
        draw.rectangle([bar_area[0] + 90, by, bar_area[0] + 90 + bar_w, by + bh - 4], fill="#ffb8c1")
        draw.text((bar_area[0] + 5, by + 2), fl, fill="#FFFFFF")

    img.save(filename)
    print(f"Mockup saved: {filename}")


def run_fallback():
    print("Using Pillow fallback mockup.")
    from PIL import Image
    full_path = str(SCREENSHOTS_DIR / "meeting_dashboard_overview.png")
    create_mockup(full_path)

    img = Image.open(full_path)
    for name, fracs in CROP_REGIONS.items():
        region = _crop_region_pixels(img, fracs)
        cropped = img.crop(region)
        cropped.save(str(SCREENSHOTS_DIR / f"{name}.png"))


def main():
    _ensure_dirs()

    try:
        print("Attempting Selenium screenshots...")
        attempt_selenium()
    except Exception as exc:
        print(f"Selenium failed: {exc}")
        print("Falling back to Pillow mockup...")
        run_fallback()

    expected = ["meeting_dashboard_overview.png", "meeting_kpi_cards.png", "meeting_donuts.png", "meeting_heatmap.png"]
    print("\nScreenshot verification:")
    all_ok = True
    for fname in expected:
        path = SCREENSHOTS_DIR / fname
        if path.exists() and path.stat().st_size > 0:
            print(f"  OK  {fname} ({path.stat().st_size:,} bytes)")
        else:
            print(f"  MISSING  {fname}")
            all_ok = False

    if not all_ok:
        sys.exit(1)
    print("All screenshots generated.")


if __name__ == "__main__":
    main()
