from PIL import Image, ImageDraw, ImageFont
import os

OUTPUT_PATH = "screenshots/mcp_interaction.png"
WIDTH = 1920
HEIGHT = 1080

BG_COLOR = "#1e1e1e"
TITLEBAR_BG = "#2d2d2d"
TOOLBOX_BG = "#252525"
COLOR_BLUE = "#146cfd"
COLOR_WHITE = "#d4d4d4"
COLOR_GREY = "#888888"
COLOR_TEAL = "#2e808e"
COLOR_LINENUM = "#555555"
COLOR_TITLE = "#ffffff"

FONT_SIZE = 14
LINE_HEIGHT = 22
PAD_LEFT = 60
PAD_RIGHT = 60
PAD_TOP = 80
PAD_BOTTOM = 80
LINENUM_WIDTH = 50
TITLEBAR_HEIGHT = 40


def get_font(size):
    font_paths = [
        "C:/Windows/Fonts/consola.ttf",
        "C:/Windows/Fonts/cour.ttf",
    ]
    for path in font_paths:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def hex_to_rgb(hex_color):
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def draw_image():
    img = Image.new("RGB", (WIDTH, HEIGHT), hex_to_rgb(BG_COLOR))
    draw = ImageDraw.Draw(img)

    font = get_font(FONT_SIZE)
    font_title = get_font(FONT_SIZE - 1)
    font_bold = get_font(FONT_SIZE + 1)

    draw.rectangle([(0, 0), (WIDTH, TITLEBAR_HEIGHT)], fill=hex_to_rgb(TITLEBAR_BG))
    title_text = "Claude Code — Superset MCP Integration"
    draw.text(
        (WIDTH // 2, TITLEBAR_HEIGHT // 2),
        title_text,
        font=font_bold,
        fill=hex_to_rgb(COLOR_TITLE),
        anchor="mm"
    )

    content_x = PAD_LEFT + LINENUM_WIDTH
    y = TITLEBAR_HEIGHT + PAD_TOP

    conversation = [
        ("human_label",  "Human:"),
        ("human_text",   "Create a bar chart of ED presentations by hospital from the"),
        ("human_text",   "       healthcare_db dataset in Superset"),
        ("blank",        ""),
        ("claude_label", "Claude:"),
        ("claude_text",  "I'll create that chart via the Superset MCP connection."),
        ("blank",        ""),
        ("tool_header",  "[Calling superset:create_chart]"),
        ("tool_body",    '  tool: "create_chart"'),
        ("tool_body",    '  params: {'),
        ("tool_body",    '    "chart_type": "bar",'),
        ("tool_body",    '    "title": "ED Presentations by Hospital",'),
        ("tool_body",    '    "dataset": "healthcare_db.fact_ed_visits",'),
        ("tool_body",    '    "x_axis": "hospital_name",'),
        ("tool_body",    '    "metric": "COUNT(*)"'),
        ("tool_body",    '  }'),
        ("tool_close",   ""),
        ("blank",        ""),
        ("success",      '✓ Chart "ED Presentations by Hospital" created (ID: 15)'),
        ("success",      '✓ Added to dashboard "ED Performance Overview"'),
        ("blank",        ""),
        ("claude_text",  "The chart shows presentations across 10 hospitals, with"),
        ("claude_text",  "Royal Prince Alfred leading at 28,450 presentations."),
    ]

    tool_start_y = None
    tool_end_y = None
    for item in conversation:
        kind, _ = item
        if kind == "tool_header":
            tool_start_y = y
        if kind == "tool_close":
            tool_end_y = y

    y_cursor = TITLEBAR_HEIGHT + PAD_TOP
    line_number = 1
    in_tool_block = False

    for kind, text in conversation:
        if kind == "tool_header":
            in_tool_block = True
        if kind == "tool_close":
            in_tool_block = False
            continue

        if in_tool_block or kind == "tool_header":
            box_x1 = PAD_LEFT + LINENUM_WIDTH - 10
            box_x2 = WIDTH - PAD_RIGHT
            draw.rectangle(
                [(box_x1, y_cursor - 2), (box_x2, y_cursor + LINE_HEIGHT - 4)],
                fill=hex_to_rgb(TOOLBOX_BG)
            )

        if kind == "blank":
            draw.text(
                (PAD_LEFT, y_cursor),
                f"{line_number:>3}",
                font=font,
                fill=hex_to_rgb(COLOR_LINENUM)
            )
            y_cursor += LINE_HEIGHT
            line_number += 1
            continue

        draw.text(
            (PAD_LEFT, y_cursor),
            f"{line_number:>3}",
            font=font,
            fill=hex_to_rgb(COLOR_LINENUM)
        )

        text_x = PAD_LEFT + LINENUM_WIDTH

        if kind == "human_label":
            draw.text((text_x, y_cursor), text, font=font_bold, fill=hex_to_rgb(COLOR_BLUE))
        elif kind == "claude_label":
            draw.text((text_x, y_cursor), text, font=font_bold, fill=hex_to_rgb(COLOR_WHITE))
        elif kind == "human_text":
            draw.text((text_x, y_cursor), text, font=font, fill=hex_to_rgb(COLOR_BLUE))
        elif kind == "claude_text":
            draw.text((text_x, y_cursor), text, font=font, fill=hex_to_rgb(COLOR_WHITE))
        elif kind == "tool_header":
            draw.text((text_x, y_cursor), text, font=font_bold, fill=hex_to_rgb(COLOR_GREY))
        elif kind == "tool_body":
            draw.text((text_x, y_cursor), text, font=font, fill=hex_to_rgb(COLOR_GREY))
        elif kind == "success":
            draw.text((text_x, y_cursor), text, font=font, fill=hex_to_rgb(COLOR_TEAL))

        y_cursor += LINE_HEIGHT
        line_number += 1

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    img.save(OUTPUT_PATH)
    print(f"Saved: {OUTPUT_PATH} ({WIDTH}x{HEIGHT})")


if __name__ == "__main__":
    draw_image()
