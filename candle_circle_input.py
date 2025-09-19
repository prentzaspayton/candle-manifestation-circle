# candle_circle_input.py
# Type/paste your message line-by-line; press Enter on an empty line to finish.

import math
import textwrap
import argparse
import sys

def make_canvas(w, h, fill=" "):
    return [[fill for _ in range(w)] for _ in range(h)]

def put_str(canvas, row, col, s):
    h, w = len(canvas), len(canvas[0])
    if 0 <= row < h:
        for i, ch in enumerate(s):
            c = col + i
            if 0 <= c < w:
                canvas[row][c] = ch

def draw_candle_ellipse(canvas, cx, cy, rx, ry, count=40, skip_boxes=None, glyph="🕯"):
    h, w = len(canvas), len(canvas[0])
    used = set()
    for k in range(count):
        t = 2 * math.pi * (k / count)
        x = cx + rx * math.cos(t)
        y = cy + ry * math.sin(t)
        col = int(round(x))
        row = int(round(y))
        key = (row, col)
        if key in used:
            continue
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

def render_candle_circle(lines, pad=3, line_gap=1, rx=None, ry=None, density=40, extra_pairs=True):
    longest = max((len(s) for s in lines), default=0)
    inner_w = longest + 2 * pad
    text_h = len(lines) + max(0, (len(lines) - 1) * line_gap)
    inner_h = text_h + 4

    W = max(inner_w + 10, 30)
    H = max(inner_h + 8, 17)

    cx = W // 2
    cy = H // 2

    rx = rx if rx is not None else max(inner_w // 2 + 4, 12)
    ry = ry if ry is not None else max(inner_h // 2 + 3, 7)

    canvas = make_canvas(W, H, " ")

    # place text
    skip_boxes = []
    start_row = cy - (text_h // 2)
    row = start_row
    for s in lines:
        col = cx - (len(s) // 2)
        put_str(canvas, row, col, s)
        skip_boxes.append((row, row, col, col + len(s) - 1))
        row += 1 + line_gap

    # candles around
    draw_candle_ellipse(canvas, cx, cy, rx, ry, count=density, skip_boxes=skip_boxes, glyph="🕯")

    # optional accent pairs like your mockup (top/bottom pairs)
    if extra_pairs:
        top_r = max(0, cy - ry)
        bot_r = min(H - 1, cy + ry)
        put_str(canvas, top_r, max(0, cx - 6), "🕯")
        put_str(canvas, top_r, min(W - 1, cx + 4), "🕯")
        put_str(canvas, bot_r, max(0, cx - 6), "🕯")
        put_str(canvas, bot_r, min(W - 1, cx + 4), "🕯")

    return "\n".join("".join(row) for row in canvas)

def get_lines_interactive(wrap_width=None):
    print("Enter your message lines (press Enter on a blank line to finish).")
    print("Tip: paste multi-line text directly. For auto-wrapping, paste a paragraph then press Enter,")
    print("     then type: /wrap <width> to wrap last paragraph (e.g., /wrap 20).")
    print()

    lines = []
    paragraph_buffer = []

    while True:
        try:
            s = input()
        except EOFError:
            break

        if s.strip().startswith("/wrap"):
            parts = s.split()
            if len(parts) == 2 and parts[1].isdigit():
                width = int(parts[1])
                if paragraph_buffer:
                    paragraph = " ".join(paragraph_buffer).strip()
                    wrapped = textwrap.wrap(paragraph, width=width)
                    # replace the buffered lines with wrapped ones
                    lines = lines + wrapped
                    paragraph_buffer = []
                    print(f"(wrapped to width {width})")
                else:
                    print("(no paragraph to wrap)")
            else:
                print("Usage: /wrap <width>")
            continue

        if s == "":
            # blank line: if there is a pending paragraph buffer, flush it as-is
            if paragraph_buffer:
                paragraph = " ".join(paragraph_buffer).strip()
                if wrap_width:
                    lines += textwrap.wrap(paragraph, width=wrap_width)
                else:
                    lines.append(paragraph)
                paragraph_buffer = []
            else:
                # consecutive blank line ends input
                break
        else:
            # accumulate paragraph lines; user can choose to wrap later
            paragraph_buffer.append(s)

    # final flush if needed
    if paragraph_buffer:
        paragraph = " ".join(paragraph_buffer).strip()
        if wrap_width:
            lines += textwrap.wrap(paragraph, width=wrap_width)
        else:
            lines.append(paragraph)

    # strip accidental empty strings
    return [ln for ln in lines if ln is not None]

def main():
    ap = argparse.ArgumentParser(description="Render a candle prayer circle around your text.")
    ap.add_argument("--pad", type=int, default=3, help="horizontal padding inside the circle")
    ap.add_argument("--gap", type=int, default=1, help="blank rows between lines")
    ap.add_argument("--rx", type=int, default=None, help="ellipse horizontal radius (auto if omitted)")
    ap.add_argument("--ry", type=int, default=None, help="ellipse vertical radius (auto if omitted)")
    ap.add_argument("--density", type=int, default=40, help="number of candles around the ellipse")
    ap.add_argument("--wrap", type=int, default=None, help="auto-wrap paragraph width")
    ap.add_argument("--no-accents", action="store_true", help="disable extra top/bottom candle pairs")
    args = ap.parse_args()

    print("🕯  Candle Circle — start typing your message below 🕯")
    lines = get_lines_interactive(wrap_width=args.wrap)

    art = render_candle_circle(
        lines=lines,
        pad=args.pad,
        line_gap=args.gap,
        rx=args.rx,
        ry=args.ry,
        density=args.density,
        extra_pairs=not args.no_accents,
    )
    print("\n" + art)

if __name__ == "__main__":
    main()
