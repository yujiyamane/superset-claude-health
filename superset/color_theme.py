PALETTE = {
    "primary":   "#002664",
    "secondary": "#146cfd",
    "teal":      "#2e808e",
    "baby_blue": "#8ce0ff",
    "soft_pink": "#ffb8c1",
    "alert":     "#630019",
    "neutral":   "#d1eeea",
}

CHART_SEQUENCE = ["#002664", "#146cfd", "#2e808e", "#8ce0ff", "#ffb8c1"]

HEATMAP_SCALE = [
    [0.0, "#d1eeea"],
    [0.5, "#2e808e"],
    [1.0, "#002664"],
]

SUPERSET_THEME = {
    "colors": {
        "primary": {"base": "#002664"},
        "secondary": {"base": "#146cfd"},
        "grayscale": {
            "base": "#002664",
            "light1": "#d1eeea",
            "light2": "#8ce0ff",
            "light3": "#f5f5f5",
            "light4": "#ffffff",
            "light5": "#ffffff",
            "dark1": "#002664",
            "dark2": "#146cfd",
        },
        "error": {"base": "#630019"},
        "warning": {"base": "#ffb8c1"},
        "alert": {"base": "#630019"},
        "success": {"base": "#2e808e"},
        "info": {"base": "#146cfd"},
    },
    "opacity": {"low": 0.1, "mediumLow": 0.35, "mediumHigh": 0.7, "high": 1},
}
