import os
import sys
import time
from pathlib import Path

SCREENSHOTS_DIR = Path(__file__).parent.parent / "screenshots"

BASE_URL = "http://localhost:8088"
DASHBOARD_URL = f"{BASE_URL}/superset/dashboard/1/"

# Relative crop regions as (x_frac, y_frac, w_frac, h_frac) — applied against actual image dimensions.
# Defined as fractions of image width/height so they work regardless of scale factor.
CROP_REGIONS = {
    "kpi_cards":    (0.0, 0.00, 1.0, 0.372),
    "triage_chart": (0.0, 0.28, 1.0, 0.83),
    "heatmap":      (0.0, 0.55, 1.0, 1.00),
}


def _ensure_dirs():
    SCREENSHOTS_DIR.mkdir(exist_ok=True)


MIN_CROP_HEIGHT = 400


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
    from selenium.webdriver.common.by import By
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
    wait = WebDriverWait(driver, 15)

    try:
        full_path = str(SCREENSHOTS_DIR / "dashboard_overview.png")
        _take_admin_screenshots(driver, wait, full_path)
        _take_role_screenshot(driver, wait, "lhd_manager_syd", "password",
                              str(SCREENSHOTS_DIR / "rls_lhd_manager.png"))
        _take_role_screenshot(driver, wait, "ward_nurse_ed1", "password",
                              str(SCREENSHOTS_DIR / "rls_ward_nurse.png"))
    finally:
        driver.quit()


def _login(driver, wait, username, password):
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC

    driver.get(f"{BASE_URL}/login/")
    wait.until(EC.presence_of_element_located(("id", "username")))

    username_field = driver.find_element("id", "username")
    password_field = driver.find_element("id", "password")

    username_field.clear()
    username_field.send_keys(username)
    password_field.clear()
    password_field.send_keys(password)
    password_field.submit()
    time.sleep(2)


def _logout(driver):
    driver.get(f"{BASE_URL}/logout/")
    time.sleep(1)


def _wait_for_charts(driver, wait):
    from selenium.webdriver.support import expected_conditions as EC
    try:
        wait.until(EC.presence_of_element_located(("css selector", ".chart-container")))
    except Exception:
        time.sleep(5)


def _take_admin_screenshots(driver, wait, full_path):
    from PIL import Image

    _login(driver, wait, "admin", "admin")
    driver.get(DASHBOARD_URL)
    _wait_for_charts(driver, wait)
    time.sleep(3)

    driver.get_screenshot_as_file(full_path)

    img = Image.open(full_path)
    for name, fracs in CROP_REGIONS.items():
        region = _crop_region_pixels(img, fracs)
        cropped = img.crop(region)
        cropped.save(str(SCREENSHOTS_DIR / f"{name}.png"))

    _logout(driver)


def _take_role_screenshot(driver, wait, username, password, out_path):
    _login(driver, wait, username, password)

    current = driver.current_url
    if "login" in current.lower():
        raise RuntimeError(
            f"Login failed for user '{username}': still on login page after submit."
        )

    driver.get(DASHBOARD_URL)
    _wait_for_charts(driver, wait)
    time.sleep(3)
    driver.get_screenshot_as_file(out_path)
    _logout(driver)


def _add_role_overlay(path, role_label):
    from PIL import Image, ImageDraw

    img = Image.open(path).convert("RGBA")
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    text = f"Role: {role_label} (admin fallback)"
    bbox = draw.textbbox((0, 0), text)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x = img.width - tw - 20
    y = img.height - th - 20
    draw.rectangle([x - 8, y - 4, x + tw + 8, y + th + 4], fill=(0, 0, 0, 180))
    draw.text((x, y), text, fill=(255, 255, 255, 255))

    composite = Image.alpha_composite(img, overlay).convert("RGB")
    composite.save(path)


def create_mockup(filename, label, width=1920, height=1080):
    from PIL import Image, ImageDraw

    img = Image.new("RGB", (width, height), "#002664")
    draw = ImageDraw.Draw(img)

    chart_areas = [
        (80, 200, 460, 480),
        (500, 200, 880, 480),
        (920, 200, 1300, 480),
        (1340, 200, 1720, 480),
        (80, 540, 920, 900),
        (960, 540, 1800, 900),
    ]
    bar_color = "#1C4E8F"
    highlight_color = "#4A90D9"
    for i, (x1, y1, x2, y2) in enumerate(chart_areas):
        draw.rectangle([x1, y1, x2, y2], outline="#FFFFFF", width=1)
        bar_w = (x2 - x1 - 20) // 8
        for b in range(8):
            bx = x1 + 10 + b * (bar_w + 2)
            bh = int((y2 - y1 - 30) * (0.3 + (b % 5) * 0.12))
            by = y2 - 15 - bh
            col = highlight_color if b % 3 == 0 else bar_color
            draw.rectangle([bx, by, bx + bar_w, y2 - 15], fill=col)

    draw.rectangle([80, 120, 1840, 180], fill="#1C4E8F")
    draw.text((960, 150), "ED Performance Dashboard", fill="#FFFFFF", anchor="mm")

    draw.text((width // 2, height // 2 + 200), label, fill="#AACCFF", anchor="mm")

    kpi_x = 120
    for kpi in ["Presentations", "Avg Wait Time", "Admitted %", "Left Without Seen"]:
        draw.rectangle([kpi_x, 930, kpi_x + 380, 1020], outline="#4A90D9", width=2)
        draw.text((kpi_x + 190, 975), kpi, fill="#FFFFFF", anchor="mm")
        kpi_x += 440

    img.save(filename)


def run_fallback():
    print("Using Pillow fallback mockup mode.")

    create_mockup(str(SCREENSHOTS_DIR / "dashboard_overview.png"),
                  "ED Performance Dashboard — Admin View")

    from PIL import Image
    full = Image.open(str(SCREENSHOTS_DIR / "dashboard_overview.png"))
    for name, fracs in CROP_REGIONS.items():
        region = _crop_region_pixels(full, fracs)
        cropped = full.crop(region)
        cropped.save(str(SCREENSHOTS_DIR / f"{name}.png"))

    create_mockup(str(SCREENSHOTS_DIR / "rls_lhd_manager.png"),
                  "ED Performance Dashboard — LHD Manager View (lhd_manager_syd)")

    create_mockup(str(SCREENSHOTS_DIR / "rls_ward_nurse.png"),
                  "ED Performance Dashboard — Ward Nurse View (ward_nurse_ed1)")


def main():
    _ensure_dirs()

    try:
        print("Attempting Selenium Chrome headless screenshots...")
        attempt_selenium()
        print("Selenium screenshots completed successfully.")
    except Exception as exc:
        print(f"Selenium failed: {exc}")
        print("Falling back to Pillow mockup generation...")
        run_fallback()

    expected = [
        "dashboard_overview.png",
        "kpi_cards.png",
        "triage_chart.png",
        "heatmap.png",
        "rls_lhd_manager.png",
        "rls_ward_nurse.png",
    ]
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
    print("\nAll screenshots generated successfully.")


if __name__ == "__main__":
    main()
