import os
import time
import glob
from pathlib import Path
from PIL import Image, ImageDraw
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

SUPERSET_URL = "http://localhost:8088"
DASHBOARD_URL = "http://localhost:8088/superset/dashboard/1/"
SCREENSHOTS_DIR = Path(__file__).parent.parent / "screenshots"
OUTPUT_GIF = SCREENSHOTS_DIR / "rls_demo.gif"
FRAME_DIR = SCREENSHOTS_DIR / "rls_frames"


def build_driver():
    options = Options()
    options.add_argument("--window-size=1280,720")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    try:
        driver = webdriver.Chrome(options=options)
        return driver
    except Exception:
        options.add_argument("--headless=new")
        driver = webdriver.Chrome(options=options)
        return driver


def login(driver, username, password):
    driver.get(f"{SUPERSET_URL}/login/")
    wait = WebDriverWait(driver, 15)
    wait.until(EC.presence_of_element_located((By.ID, "username")))
    driver.find_element(By.ID, "username").clear()
    driver.find_element(By.ID, "username").send_keys(username)
    driver.find_element(By.ID, "password").clear()
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.CSS_SELECTOR, "[type=submit]").click()
    wait.until(EC.url_contains("/superset/"))


def load_dashboard(driver):
    driver.get(DASHBOARD_URL)
    wait = WebDriverWait(driver, 15)
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".chart-container")))
    except Exception:
        pass
    time.sleep(3)


def logout(driver):
    driver.get(f"{SUPERSET_URL}/logout/")
    time.sleep(1)


def add_overlay(img, text):
    img = img.convert("RGBA")
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rectangle([(0, img.height - 60), (img.width, img.height)], fill=(0, 0, 0, 180))
    draw.text((20, img.height - 40), text, fill=(255, 255, 255, 255))
    return Image.alpha_composite(img, overlay).convert("RGB")


def capture_frames(driver, label, frame_count, frame_dir, frame_index_start):
    paths = []
    for i in range(frame_count):
        raw_path = frame_dir / f"frame_{frame_index_start + i:04d}_raw.png"
        out_path = frame_dir / f"frame_{frame_index_start + i:04d}.png"
        driver.save_screenshot(str(raw_path))
        img = Image.open(str(raw_path))
        img = img.resize((1280, 720), Image.LANCZOS)
        img = add_overlay(img, label)
        img.save(str(out_path))
        raw_path.unlink()
        paths.append(str(out_path))
        time.sleep(0.15)
    return paths


def frames_to_gif(frame_paths, output_path):
    imgs = [Image.open(f) for f in frame_paths]
    imgs[0].save(
        str(output_path),
        save_all=True,
        append_images=imgs[1:],
        duration=200,
        loop=0,
        optimize=True,
    )
    for img in imgs:
        img.close()

    size = os.path.getsize(str(output_path))
    if size > 5 * 1024 * 1024:
        resized_paths = []
        for path in frame_paths:
            img = Image.open(path)
            img = img.resize((960, 540), Image.LANCZOS)
            resized_path = path.replace(".png", "_sm.png")
            img.save(resized_path)
            resized_paths.append(resized_path)
        imgs = [Image.open(f) for f in resized_paths]
        imgs[0].save(
            str(output_path),
            save_all=True,
            append_images=imgs[1:],
            duration=200,
            loop=0,
            optimize=True,
        )
        for img in imgs:
            img.close()
        for p in resized_paths:
            os.unlink(p)


def main():
    FRAME_DIR.mkdir(parents=True, exist_ok=True)

    roles = [
        ("admin", "admin", "Role: Admin — All LHDs visible"),
        ("lhd_manager_syd", "password", "Role: LHD Manager — Sydney LHD only"),
        ("ward_nurse_ed1", "password", "Role: Ward Nurse — ED Ward 1 only"),
    ]

    driver = build_driver()
    all_frames = []
    frame_idx = 0

    try:
        for username, password, label in roles:
            login(driver, username, password)
            load_dashboard(driver)
            frames = capture_frames(driver, label, 15, FRAME_DIR, frame_idx)
            all_frames.extend(frames)
            frame_idx += 15
            logout(driver)
    finally:
        driver.quit()

    frames_to_gif(all_frames, OUTPUT_GIF)

    for f in all_frames:
        if os.path.exists(f):
            os.unlink(f)

    for leftover in glob.glob(str(FRAME_DIR / "*.png")):
        os.unlink(leftover)

    try:
        FRAME_DIR.rmdir()
    except OSError:
        pass

    size_mb = os.path.getsize(str(OUTPUT_GIF)) / (1024 * 1024)
    img = Image.open(str(OUTPUT_GIF))
    print(f"GIF created: {OUTPUT_GIF}")
    print(f"Frames: {img.n_frames}, Size: {size_mb:.2f}MB, Dimensions: {img.size}")
    img.close()


if __name__ == "__main__":
    main()
