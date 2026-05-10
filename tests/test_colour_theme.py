import re
import pytest
import sys
sys.path.insert(0, "superset")
from color_theme import PALETTE, CHART_SEQUENCE, HEATMAP_SCALE, SUPERSET_THEME

HEX_PATTERN = re.compile(r"^#[0-9a-fA-F]{6}$")

def test_all_palette_values_are_valid_hex():
    for name, color in PALETTE.items():
        assert HEX_PATTERN.match(color), f"{name}: {color} is not valid hex"

def test_chart_sequence_has_5_colors():
    assert len(CHART_SEQUENCE) == 5

def test_chart_sequence_all_from_palette():
    palette_values = set(PALETTE.values())
    for color in CHART_SEQUENCE:
        assert color in palette_values

def test_no_duplicate_colors_in_palette():
    values = list(PALETTE.values())
    assert len(values) == len(set(values))

def test_heatmap_scale_bounds():
    assert HEATMAP_SCALE[0][0] == 0.0
    assert HEATMAP_SCALE[-1][0] == 1.0

def test_alert_is_red_dominant():
    r = int(PALETTE["alert"][1:3], 16)
    g = int(PALETTE["alert"][3:5], 16)
    b = int(PALETTE["alert"][5:7], 16)
    assert r > g and r > b

def test_superset_theme_has_required_keys():
    assert "colors" in SUPERSET_THEME
    assert "primary" in SUPERSET_THEME["colors"]
    assert "error" in SUPERSET_THEME["colors"]

def test_superset_theme_primary_matches_palette():
    assert SUPERSET_THEME["colors"]["primary"]["base"] == PALETTE["primary"]
