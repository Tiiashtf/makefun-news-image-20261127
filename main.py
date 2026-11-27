#!/usr/bin/env python3
"""The World Today - 27 November 2026.

A newspaper front page that sums up Friday 27 November 2026 in one
image. Pure Python 3.13 standard library: a small pixel canvas, a
hand-authored 5x7 dot-matrix face, and its own PNG writer. No network,
no input files, no timestamps: every run writes the exact same bytes.

Run:  MAKEFUN_OUTPUT_DIR=out python3 main.py
Writes: <output dir>/entry.png  (1024x1024, under 1 MiB)
"""

import os
import struct
import zlib

W, H = 1024, 1024

PAPER = (248, 243, 230)   # warm newsprint
INK = (22, 22, 22)       # headline black
RED = (176, 32, 40)      # masthead / kicker red
BLUE = (28, 76, 132)     # secondary blue
GREY = (120, 116, 106)   # muted grey
DUSK = (232, 176, 96)    # evening sky
DUSK2 = (214, 128, 64)   # deeper dusk
SKY = (168, 196, 216)    # pale sky
DARK = (52, 52, 58)      # skyline silhouette
ORANGE = (232, 120, 32)  # explosion
YELLOW = (244, 196, 64)  # explosion core
SMOKE = (150, 146, 138)  # smoke grey
GREEN = (46, 110, 62)    # chart green

# 5x7 dot-matrix face, hand-authored. '#' is ink, '.' is blank.
FONT = {
    'A': (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    'C': (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    'D': ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    'E': ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    'F': ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    'G': (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'I': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    'J': ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    'K': ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
}

FONT.update({
    'N': ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    'O': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'P': ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    'Q': (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    'R': ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    'S': (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    'T': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    'U': ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'V': ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'W': ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    'X': ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    'Y': ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    'Z': ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    '0': (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    '1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    '2': (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    '3': ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    '4': ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    '5': ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    '6': (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    '7': ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    '8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    '9': (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    ' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    '.': (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ',': (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    "'": (".#...", ".#...", ".....", ".....", ".....", ".....", "....."),
    '"': ("#.#..", "#.#..", ".....", ".....", ".....", ".....", "....."),
    '-': (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    ':': (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    '/': ("....#", "....#", "...#.", "...#.", "..#..", ".#...", "#...."),
    '(': ("...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"),
    ')': ("##...", "..#..", "...#.", "...#.", "...#.", "..#..", "##..."),
    '!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    '?': (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    '+': (".....", "..#..", "..#..", ".###.", "..#..", "..#..", "....."),
    '|': ("..#..", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
})


class Canvas:
    """A plain RGB pixel buffer with tiny drawing helpers."""

    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg * (w * h))

    def put(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def fill(self, x0, y0, x1, y1, color):
        x0 = max(0, x0)
        y0 = max(0, y0)
        x1 = min(self.w, x1)
        y1 = min(self.h, y1)
        for y in range(y0, y1):
            i = (y * self.w + x0) * 3
            self.px[i:(y * self.w + x1) * 3] = bytes(color) * (x1 - x0)

    def hline(self, x0, x1, y, color, thick=1):
        for t in range(thick):
            self.fill(x0, y + t, x1, y + t + 1, color)

    def vline(self, x, y0, y1, color, thick=1):
        for t in range(thick):
            self.fill(x + t, y0, x + t + 1, y1, color)

    def box(self, x0, y0, x1, y1, color, thick=1):
        self.hline(x0, x1, y0, color, thick)
        self.hline(x0, x1, y1 - thick, color, thick)
        self.vline(x0, y0, y1, color, thick)
        self.vline(x1 - thick, y0, y1, color, thick)

    def line(self, x0, y0, x1, y1, color):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.put(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, color):
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                    self.put(x, y, color)

    def burst(self, cx, cy, r1, r2, spikes, color):
        # A starburst: alternating long and short spikes from the centre.
        import math
        pts = []
        for i in range(spikes * 2):
            ang = math.pi * i / spikes
            r = r1 if i % 2 == 0 else r2
            pts.append((cx + int(r * math.cos(ang)),
                        cy + int(r * math.sin(ang))))
        for i in range(len(pts)):
            x0, y0 = pts[i]
            x1, y1 = pts[(i + 1) % len(pts)]
            self.line(x0, y0, x1, y1, color)
        # Fill the middle by drawing lines from the centre out.
        for i in range(len(pts)):
            self.line(cx, cy, pts[i][0], pts[i][1], color)


def text_w(s, scale):
    """Pixel width of a string at a scale (5px glyph + 1px gap, scaled)."""
    return len(s) * 6 * scale - scale


def draw_text(cv, x, y, s, scale, color):
    """Draw a string; returns the x just past its end."""
    cx = x
    for ch in s:
        glyph = FONT.get(ch)
        if glyph is None:
            cx += 6 * scale
            continue
        for row, bits in enumerate(glyph):
            for col, bit in enumerate(bits):
                if bit == '#':
                    cv.fill(cx + col * scale, y + row * scale,
                            cx + col * scale + scale,
                            y + row * scale + scale, color)
        cx += 6 * scale
    return cx


def draw_wrapped(cv, x, y, text, scale, color, width, line_gap=6):
    """Word-wrap a paragraph; returns the y just past its last line."""
    words = text.split(' ')
    lines = []
    cur = ''
    for word in words:
        trial = word if not cur else cur + ' ' + word
        if text_w(trial, scale) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    for line in lines:
        draw_text(cv, x, y, line, scale, color)
        y += 7 * scale + line_gap
    return y


def draw_wrapped_segments(cv, x, y, segments, scale, width, line_gap=6):
    """Wrap a paragraph whose lead segment has its own colour.

    segments: list of (text, color). Only the first segment is coloured
    differently; the rest share the second colour.
    """
    words = []
    for text, color in segments:
        for word in text.split(' '):
            words.append((word, color))
    lines = []
    cur = []
    cur_w = 0
    for word, color in words:
        add = text_w(word, scale) + (text_w(' ', scale) if cur else 0)
        if cur and cur_w + add > width:
            lines.append(cur)
            cur = [(word, color)]
            cur_w = text_w(word, scale)
        else:
            cur.append((word, color))
            cur_w += add
    if cur:
        lines.append(cur)
    for line in lines:
        cx = x
        for i, (word, color) in enumerate(line):
            if i:
                cx += text_w(' ', scale)
            cx = draw_text(cv, cx, y, word, scale, color)
        y += 7 * scale + line_gap
    return y


def png_bytes(cv):
    """Encode the canvas as a PNG (filter 0 scanlines, zlib)."""
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        raw.extend(cv.px[y * cv.w * 3:(y + 1) * cv.w * 3])
    comp = zlib.compress(bytes(raw), 9)

    def chunk(kind, data):
        out = struct.pack('>I', len(data)) + kind + data
        return out + struct.pack('>I', zlib.crc32(kind + data) & 0xffffffff)

    ihdr = struct.pack('>IIBBBBB', cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr)
            + chunk(b'IDAT', comp) + chunk(b'IEND', b''))


def dashed(cv, x0, y0, x1, y1, color, dash=9, gap=6):
    """A dashed straight line (for the map arrow)."""
    import math
    length = math.hypot(x1 - x0, y1 - y0)
    if length == 0:
        return
    steps = int(length / (dash + gap)) + 1
    for i in range(steps):
        t0 = i * (dash + gap) / length
        t1 = min(1.0, t0 + dash / length)
        cv.line(int(x0 + (x1 - x0) * t0), int(y0 + (y1 - y0) * t0),
                int(x0 + (x1 - x0) * t1), int(y0 + (y1 - y0) * t1), color)


def draw_lead_panel(cv, x0, y0, x1, y1):
    """Dusk sky over Kuwait City: skyline, explosion, drone."""
    cv.fill(x0, y0, x1, y1, DUSK)
    cv.fill(x0, y0 + 150, x1, y1, DUSK2)
    # Skyline silhouettes.
    for bx, bw, bh in ((664, 42, 96), (712, 30, 128), (748, 52, 84),
                       (806, 36, 140), (848, 60, 100), (914, 34, 122),
                       (954, 30, 88)):
        cv.fill(bx, y1 - bh, bx + bw, y1, DARK)
        for wy in range(y1 - bh + 12, y1 - 8, 18):
            for wx in range(bx + 8, bx + bw - 6, 14):
                cv.fill(wx, wy, wx + 4, wy + 5, YELLOW)
    # Explosion burst over the skyline.
    cv.burst(770, y1 - 150, 52, 24, 9, ORANGE)
    cv.burst(770, y1 - 150, 30, 14, 9, YELLOW)
    # Smoke rising from it.
    cv.disc(742, y1 - 196, 16, SMOKE)
    cv.disc(766, y1 - 214, 20, SMOKE)
    cv.disc(796, y1 - 200, 14, SMOKE)
    # A drone in the sky.
    dx, dy = 890, y0 + 62
    cv.fill(dx - 10, dy - 5, dx + 10, dy + 5, INK)
    cv.line(dx - 10, dy, dx - 26, dy - 12, INK)
    cv.line(dx + 10, dy, dx + 26, dy - 12, INK)
    cv.line(dx - 10, dy, dx - 26, dy + 12, INK)
    cv.line(dx + 10, dy, dx + 26, dy + 12, INK)
    for rx, ry in ((dx - 26, dy - 12), (dx + 26, dy - 12),
                   (dx - 26, dy + 12), (dx + 26, dy + 12)):
        cv.hline(rx - 12, rx + 12, ry, INK, 2)
    cv.disc(dx, dy, 3, RED)
    cv.box(x0, y0, x1, y1, INK, 2)


def draw_map_panel(cv, x0, y0, x1, y1):
    """A schematic map: the Gulf, Kuwait, Iran, the drone's path."""
    SAND = (238, 224, 182)
    SEA = (170, 198, 220)
    cv.fill(x0, y0, x1, y1, SAND)
    cv.fill(x0, y0 + 58, x1, y1, SEA)
    cv.hline(x0, x1, y0 + 58, INK, 2)
    draw_text(cv, x0 + 16, y0 + 84, "THE GULF", 2, BLUE)
    draw_text(cv, x0 + 330, y0 + 14, "IRAN", 2, INK)
    dashed(cv, x0 + 330, y0 + 34, x0 + 250, y0 + 78, RED)
    cv.line(x0 + 250, y0 + 78, x0 + 262, y0 + 70, RED)
    cv.line(x0 + 250, y0 + 78, x0 + 262, y0 + 86, RED)
    cv.disc(x0 + 248, y0 + 80, 7, RED)
    cv.disc(x0 + 248, y0 + 80, 3, PAPER)
    draw_text(cv, x0 + 264, y0 + 72, "KUWAIT", 2, INK)
    cv.box(x0, y0, x1, y1, INK, 2)


def draw_gaza_strip(cv, x0, y0, x1, y1):
    """Gaza skyline at night with smoke columns."""
    cv.fill(x0, y0, x1, y1, SKY)
    for bx, bw, bh in ((x0 + 8, 40, 52), (x0 + 56, 30, 78),
                       (x0 + 94, 48, 60), (x0 + 150, 34, 88),
                       (x0 + 190, 26, 56)):
        cv.fill(bx, y1 - bh, bx + bw, y1, DARK)
    cv.disc(x0 + 70, y1 - 84, 10, SMOKE)
    cv.disc(x0 + 66, y1 - 102, 13, SMOKE)
    cv.disc(x0 + 74, y1 - 120, 10, SMOKE)
    cv.disc(x0 + 168, y1 - 94, 10, SMOKE)
    cv.disc(x0 + 164, y1 - 112, 13, SMOKE)
    cv.burst(x0 + 120, y1 - 70, 15, 7, 7, ORANGE)
    cv.burst(x0 + 120, y1 - 70, 8, 4, 7, YELLOW)
    cv.box(x0, y0, x1, y1, INK, 2)


def draw_chessboard(cv, x0, y0, sq=9):
    for r in range(8):
        for c in range(8):
            if (r + c) % 2 == 0:
                cv.fill(x0 + c * sq, y0 + r * sq,
                        x0 + (c + 1) * sq, y0 + (r + 1) * sq, INK)
    # A white king on a dark square and a black king on a light one.
    cv.disc(x0 + 5 * sq + 4, y0 + 7 * sq + 4, 5, PAPER)
    cv.disc(x0 + 5 * sq + 4, y0 + 7 * sq + 4, 3, INK)
    cv.disc(x0 + 2 * sq + 4, y0 + 1 * sq + 4, 5, INK)
    cv.disc(x0 + 2 * sq + 4, y0 + 1 * sq + 4, 3, PAPER)
    cv.box(x0, y0, x0 + 8 * sq, y0 + 8 * sq, INK, 1)


def draw_bars(cv, x0, y_base, heights, color):
    for i, h in enumerate(heights):
        bx = x0 + i * 22
        cv.fill(bx, y_base - h, bx + 16, y_base, color)
    cv.hline(x0 - 6, x0 + len(heights) * 22, y_base, INK, 2)


def build():
    cv = Canvas(W, H, PAPER)
    cv.box(16, 16, 1008, 1008, INK, 2)
    cv.box(24, 24, 1000, 1000, INK, 1)

    # Masthead.
    title = "THE WORLD TODAY"
    draw_text(cv, (W - text_w(title, 7)) // 2, 40, title, 7, INK)
    cv.hline(40, 984, 100, INK, 2)
    date = "FRIDAY 27 NOVEMBER 2026"
    draw_text(cv, (W - text_w(date, 3)) // 2, 112, date, 3, RED)
    cv.hline(40, 984, 142, INK, 3)

    # Lead story: drone strike in Kuwait.
    draw_text(cv, 40, 158, "MIDDLE EAST", 2, RED)
    draw_text(cv, 40, 184, "DRONE STRIKE IN KUWAIT", 4, INK)
    draw_text(cv, 40, 220, "KILLS TWO ITALIANS", 4, INK)
    draw_wrapped(cv, 40, 272,
                 "KUWAIT SAYS AN IRANIAN DRONE HIT A WORK SITE. "
                 "TWO ITALIAN WORKERS WERE KILLED, OFFICIALS SAID. "
                 "TEHRAN DENIES ANY ROLE.",
                 2, INK, 600)
    draw_map_panel(cv, 40, 344, 640, 470)
    draw_lead_panel(cv, 664, 156, 984, 470)

    cv.hline(40, 984, 488, INK, 2)

    # Second story: Gaza.
    draw_text(cv, 40, 504, "GAZA", 2, RED)
    draw_text(cv, 40, 530, "HAMAS WEIGHS REPLY AS", 3, INK)
    draw_text(cv, 40, 556, "ISRAEL KILLS 10 IN GAZA", 3, INK)
    draw_wrapped(cv, 40, 592,
                 "REUTERS: HAMAS CONSIDERS ITS ANSWER AFTER ISRAELI "
                 "STRIKES KILL 10 PEOPLE IN GAZA.",
                 2, INK, 700)
    draw_gaza_strip(cv, 760, 504, 984, 640)

    cv.hline(40, 984, 656, INK, 2)

    # Third row: chess and UK migration.
    draw_text(cv, 40, 672, "SPORT", 2, RED)
    draw_chessboard(cv, 420, 672)
    draw_text(cv, 40, 698, "GUKESH, SINDAROV DRAW", 2, INK)
    draw_text(cv, 40, 722, "MARATHON GAME 3", 2, INK)
    draw_wrapped(cv, 40, 750,
                 "WORLD CHESS TITLE LEVEL AFTER THREE GAMES.",
                 2, INK, 456)
    cv.vline(512, 672, 800, INK, 1)
    draw_text(cv, 528, 672, "BRITAIN", 2, RED)
    draw_text(cv, 528, 698, "UK NET MIGRATION", 2, INK)
    draw_text(cv, 528, 722, "LOWEST SINCE 1997", 2, INK)
    draw_text(cv, 528, 750, "LOWEST IN NEARLY 30 YEARS.", 2, INK)
    draw_bars(cv, 896, 740, (60, 48, 36, 24), GREEN)

    cv.hline(40, 984, 816, INK, 2)

    # Briefs.
    draw_text(cv, 40, 830, "IN BRIEF", 2, RED)
    cv.hline(40, 984, 852, INK, 1)
    briefs = [
        (("DEPARDIEU TO STAND TRIAL", RED),
         ("- FRENCH COURT ORDERS TRIAL OVER ALLEGED 2018 RAPE.", INK)),
        (("TRUMP SEEKS PROBE OF 'FAKE' GDP", RED),
         ("- AFTER GROWTH REVISED UP TO 4.3 PER CENT.", INK)),
        (("FCC CLEARS SPACEX FOR 1M SATELLITES", RED),
         ("- DATA CENTRES IN ORBIT.", INK)),
        (("NZ FINAL VOTE COUNT TODAY", RED),
         ("- COALITION HOLDS SLIM 67-SEAT EDGE.", INK)),
        (("BLACK FRIDAY", RED),
         ("- SHOPPERS WARNED OF 'BLACK NOVEMBER' PRICE TRICKS.", INK)),
        (("INDIA TOP COURT", RED),
         ("- PMLA ATTACHMENT NEEDS JUDICIAL MEMBER ON BENCH.", INK)),
    ]
    positions = [(40, 864), (40, 900), (40, 936),
                 (528, 864), (528, 900), (528, 936)]
    for (lead, rest), (bx, by) in zip(briefs, positions):
        draw_wrapped_segments(cv, bx, by, [lead, rest], 2, 456)

    cv.hline(40, 984, 974, INK, 1)
    foot = "ALL STORIES FIRST REPORTED 27 NOVEMBER 2026 | NYT | BBC | REUTERS | AP"
    draw_text(cv, (W - text_w(foot, 2)) // 2, 984, foot, 2, GREY)
    return cv


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    # Clear only the contents of the output dir, never the dir itself.
    for name in os.listdir(outdir):
        path = os.path.join(outdir, name)
        if os.path.isfile(path) or os.path.islink(path):
            os.remove(path)
        elif os.path.isdir(path):
            import shutil
            shutil.rmtree(path)
    data = png_bytes(build())
    with open(os.path.join(outdir, "entry.png"), "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()
