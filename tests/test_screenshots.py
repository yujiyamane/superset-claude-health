import os
import pytest
from PIL import Image

SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "..", "screenshots")

REQUIRED_FILES = [
    "dashboard_overview.png",
    "kpi_cards.png",
    "triage_chart.png",
    "heatmap.png",
    "rls_lhd_manager.png",
    "rls_ward_nurse.png",
    "rls_demo.gif",
    "mcp_interaction.png",
]

def test_all_screenshots_exist():
    for f in REQUIRED_FILES:
        path = os.path.join(SCREENSHOT_DIR, f)
        assert os.path.exists(path), f"Missing: {f}"

def test_png_files_are_valid_images():
    for f in REQUIRED_FILES:
        if not f.endswith(".png"):
            continue
        path = os.path.join(SCREENSHOT_DIR, f)
        img = Image.open(path)
        assert img.size[0] >= 800, f"{f} width too small: {img.size[0]}"
        assert img.size[1] >= 400, f"{f} height too small: {img.size[1]}"

def test_gif_is_animated():
    path = os.path.join(SCREENSHOT_DIR, "rls_demo.gif")
    img = Image.open(path)
    assert hasattr(img, "n_frames") and img.n_frames > 1, "GIF is not animated"

def test_gif_file_size_under_5mb():
    path = os.path.join(SCREENSHOT_DIR, "rls_demo.gif")
    size_mb = os.path.getsize(path) / (1024 * 1024)
    assert size_mb < 5, f"GIF too large: {size_mb:.1f}MB"

def test_readme_references_screenshots():
    readme_path = os.path.join(os.path.dirname(__file__), "..", "README.md")
    with open(readme_path, encoding="utf-8") as f:
        content = f.read()
    for f in REQUIRED_FILES:
        assert f in content, f"README.md does not reference {f}"
