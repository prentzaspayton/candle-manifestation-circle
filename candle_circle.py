# candle_circle.py
# Render your text inside a "circle" (ellipse) of candle emojis.

import math

def make_canvas(w, h, fill=" "):
    return [[fill for _ in range(w)] for _ in range(h)]

def put_str(canvas, row, col, s):
    h, w = len(canvas), len(canvas[0])
    if 0 <= row < h:
        for i, ch in enumerate(s):
            c = col + i
            if 0 <= c < w:
                canvas[row][c] = ch

def draw_candle_ellipse(canvas, cx, cy, rx, ry, count=36, skip_boxes=None, glyph="🕯"):
    """
    Places 'count' candles on an ellipse centered at (cx, cy) with radii rx, ry.
    skip_boxes: list of (r0, r1, c0, c1) boxes where candles should not be drawn (keeps text clear).
    """
    h, w = len(canvas), len(canvas[0])
    used = set()
    for k in range(count):
        t = 2 * math.pi * (k / count)
        # ellipse parametric
        x = cx + rx * math.cos(t)
        y = cy + ry * math.sin(t)
        # best-effort emoji width handling: emojis can render ~2 columns wide
        col = int(round(x))
        row = int(round(y))

        # de-duplicate nearby points
        key = (row, col)
        if key in used:
            continue

        # skip if candle would overlap text area boxes
        blocked = False
        if skip_boxes:
            for (r0, r1, c0, c1) in skip_boxes:
                if r0 <= row <= r1 and c0 <= col <= c1:
                    blocked = True
                    break
        if blocked:
            continue

        if 0 <= row < h and 0 <= col < w:
            canvas[row][col] = glyph
            used.add(key)

def render_candle_circle(lines, pad=3, line_gap=1, rx=None, ry=None, density=40):
    """
    lines: list of text lines (strings).
    pad:   horizontal padding on each side of the longest line.
    line_gap: blank rows between text lines.
    rx, ry: ellipse radii (auto if None).
    density: number of candles on the ellipse.
    """
    longest = max((len(s) for s in lines), default=0)
    inner_w = longest + 2 * pad

    # Text block height = number of lines + gaps between them
    text_h = len(lines) + (len(lines) - 1) * line_gap
    # Add vertical padding inside the circle
    inner_h = text_h + 4

    # Canvas size
    W = max(inner_w + 10, 30)   # a little buffer
    H = max(inner_h + 6, 15)

    # Center for ellipse and text
    cx = W // 2
    cy = H // 2

    # Auto radii if not provided
    rx = rx if rx is not None else max(inner_w // 2 + 4, 10)
    ry = ry if ry is not None else max(inner_h // 2 + 3, 6)

    canvas = make_canvas(W, H, " ")

    # Compute text rows & skip boxes to keep candles out of text
    text_rows = []
    start_row = cy - (text_h // 2)
    current_row = start_row
    skip_boxes = []
    for i, s in enumerate(lines):
        # center each line
        col = cx - (len(s) // 2)
        put_str(canvas, current_row, col, s)
        # remember a small box around the text to avoid candles overlapping
        skip_boxes.append((current_row, current_row, col, col + len(s) - 1))
        current_row += 1 + line_gap

    # Draw ellipse of candles, skipping the text boxes
    draw_candle_ellipse(canvas, cx, cy, rx, ry, count=density, skip_boxes=skip_boxes, glyph="🕯")

    # Optional: add a few “accent” candles near top/bottom to mimic your layout
    # Top pair
    put_str(canvas, cy - ry, cx - 6, "🕯")
    put_str(canvas, cy - ry, cx + 4, "🕯")
    # Bottom pair
    put_str(canvas, cy + ry, cx - 6, "🕯")
    put_str(canvas, cy + ry, cx + 4, "🕯")

    # Join lines
    return "\n".join("".join(row) for row in canvas)

if __name__ == "__main__":
    lines = [
        "enough",
        "time to read",
        "all the books",
        "i want to read",
        "in 2022",
    ]

    art = render_candle_circle(lines, pad=3, line_gap=1, rx=None, ry=None, density=34)
    print(art)
