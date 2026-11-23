#!/usr/bin/env python3
"""News image for Monday 23 November 2026 -- one image, the whole day.

make.fun bounty news-image-20261123 ($100, top 50 share).
Pure Python standard library only (no Pillow, no network, no randomness,
no timestamps): the program draws a 1024x1024 newspaper front page with a
hand-rolled 5x7 bitmap font and writes a deterministic PNG to
/output/entry.png. Running it twice produces byte-identical output.

Today's news, researched from live sources on 23 Nov 2026 (morning WIB):
  1. COP31 COLLAPSES -- climate talks in Antalya, Turkey, broke down in
     overtime on Sunday 22 Nov, the longest COP ever, with no final deal:
     the EU walked out rather than endorse a text that never mentioned
     fossil fuels; Saudi Arabia and other oil producers blocked the
     phase-out language; the $120bn adaptation-finance target was dropped.
  2. GULF WAR ESCALATES -- Iran hit US bases in Bahrain (al-Riffa and
     Awali, Patriot radars targeted) with missiles and drones on Saturday
     night, a civilian industrial facility caught fire on Sitra Island,
     two people were injured, and tankers kept being struck in the
     Strait of Hormuz (about 25 tanker incidents in a week).
  3. UKRAINE -- a Russian drone flattened a section of a five-storey
     apartment block in Dymer, Kyiv region, on 22 Nov: 4 killed, about
     14 missing under the rubble; 186 drones were launched overnight and
     Russia fired 165 missiles in the week, Zelenskyy said.
  4. AI ON TRIAL -- nations agreed at the UN to keep negotiating rules
     for lethal AI systems, and South Korea's education minister resigned
     over an AI-driven exam-cheating scandal.
  5. WORLD IN BRIEF -- Indonesian factory fire leaves 50 missing;
     24 civilians killed in South Sudan; Nepal's PM Balendra Shah meets
     Modi in Delhi; Mexico captures FBI most-wanted cartel boss
     "El Chapo Isidro" after firefights that killed 11 in Sinaloa.
"""

import math
import os
import struct
import sys
import zlib

W = 1024
H = 1024
OUT = "/output/entry.png"

# ---------------------------------------------------------------- palette
PAPER = (247, 243, 232)
INK = (18, 20, 26)
NAVY = (20, 36, 62)
NAVY2 = (28, 52, 88)
GOLD = (212, 164, 65)
GOLD2 = (232, 196, 110)
WHITE = (250, 248, 242)
GREY = (120, 118, 110)
DUSK_TOP = (43, 27, 74)
DUSK_MID = (150, 74, 52)
DUSK_BOT = (232, 163, 76)
SEA = (16, 58, 74)
SEA2 = (24, 84, 100)
NIGHT = (32, 42, 66)
TEAL = (46, 120, 128)

# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows of 5 cells, "#" = on, "." = off.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    "-": (".....", ".....", ".....", ".####", ".....", ".....", "....."),
    ":": (".....", ".##..", ".....", ".##..", ".....", ".##..", "....."),
    ";": (".....", ".##..", ".....", ".##..", ".##..", ".#...", "....."),
    "'": ("..#..", "..#..", ".....", ".....", ".....", ".....", "....."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "%": ("#...#", "#..#.", "...#.", "..#..", ".#...", "#..#.", "#...#"),
    "&": (".##..", "#..#.", "#..#.", ".#...", "#.#.#", "#..#.", ".##.#"),
    "+": (".....", "..#..", "..#..", ".###.", "..#..", "..#..", "....."),
    "=": (".....", ".....", ".####", ".....", ".####", ".....", "....."),
    "*": (".....", ".#.#.", "..#..", ".###.", "..#..", ".#.#.", "....."),
}


def text_width(s, scale):
    """Width in pixels of string s at the given scale."""
    if not s:
        return 0
    return len(s) * 6 * scale - scale


# ------------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w=W, h=H, bg=PAPER):
        self.w = w
        self.h = h
        self.rows = [bytearray(bytes(bg) * w) for _ in range(h)]

    def rect(self, x, y, w, h, color):
        if w <= 0 or h <= 0:
            return
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        pat = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            row = self.rows[yy]
            row[x0 * 3:x1 * 3] = pat

    def px(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            row = self.rows[y]
            row[x * 3:x * 3 + 3] = bytes(color)

    def line(self, x0, y0, x1, y1, color, thick=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        half = thick // 2
        while True:
            self.rect(x0 - half, y0 - half, thick, thick, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            dx = int(math.sqrt(max(0, r * r - dy * dy)))
            self.rect(cx - dx, cy + dy, 2 * dx + 1, 1, color)

    def ring(self, cx, cy, r, color, thick=3):
        for dy in range(-r, r + 1):
            dx = int(math.sqrt(max(0, r * r - dy * dy)))
            dx2 = int(math.sqrt(max(0, (r - thick) * (r - thick) - dy * dy))) \
                if abs(dy) < r - thick else 0
            self.rect(cx - dx, cy + dy, dx - dx2, 1, color)
            self.rect(cx + dx2 + 1, cy + dy, dx - dx2, 1, color)

    def ellipse(self, cx, cy, rx, ry, color):
        for dy in range(-ry, ry + 1):
            t = 1.0 - (dy * dy) / float(ry * ry)
            dx = int(rx * math.sqrt(max(0.0, t)))
            self.rect(cx - dx, cy + dy, 2 * dx + 1, 1, color)

    def poly(self, pts, color):
        """Scanline-filled polygon, pts = [(x, y), ...]."""
        if len(pts) < 3:
            return
        ys = [p[1] for p in pts]
        for y in range(max(0, min(ys)), min(self.h, max(ys) + 1)):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / float(y1 - y0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.rect(int(xs[i]), y, int(xs[i + 1]) - int(xs[i]) + 1, 1, color)

    def vgrad(self, x, y, w, h, top, bot):
        for i in range(h):
            t = i / float(max(1, h - 1))
            c = tuple(int(top[k] + (bot[k] - top[k]) * t) for k in range(3))
            self.rect(x, y + i, w, 1, c)

    def text(self, x, y, s, scale, color):
        cx = x
        for ch in s.upper():
            glyph = FONT.get(ch, FONT[" "])
            for r in range(7):
                row = glyph[r]
                for c in range(5):
                    if row[c] == "1":
                        self.rect(cx + c * scale, y + r * scale,
                                  scale, scale, color)
            cx += 6 * scale
        return cx

    def text_center(self, y, s, scale, color, x0=0, x1=W):
        w = text_width(s, scale)
        self.text(x0 + (x1 - x0 - w) // 2, y, s, scale, color)

    def wrapped(self, x, y, s, scale, color, max_w, line_h=None):
        """Word-wrap text; returns y just below the last line."""
        if line_h is None:
            line_h = 7 * scale + 5
        words = s.split(" ")
        lines = []
        cur = ""
        for wd in words:
            trial = (cur + " " + wd).strip()
            if text_width(trial, scale) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        for ln in lines:
            self.text(x, y, ln, scale, color)
            y += line_h
        return y


# ------------------------------------------------------------------- people
def person(cv, x, y, s, color):
    """Simple walking silhouette, s = height in px."""
    head_r = max(2, s // 7)
    cv.circle(x, y - s + head_r, head_r, color)
    cv.rect(x - s // 8, y - s + 2 * head_r, s // 4, s // 2, color)
    cv.line(x - s // 8, y - s // 3, x - s // 4, y, color, thick=max(2, s // 12))
    cv.line(x + s // 8, y - s // 3, x + s // 4, y, color, thick=max(2, s // 12))


def burst(cv, cx, cy, r, color):
    """Starburst explosion."""
    for k in range(12):
        ang = k * math.pi / 6.0
        x1 = cx + int(r * math.cos(ang))
        y1 = cy + int(r * math.sin(ang))
        x2 = cx + int(r * 0.45 * math.cos(ang + 0.26))
        y2 = cy + int(r * 0.45 * math.sin(ang + 0.26))
        cv.poly([(cx, cy), (x1, y1), (x2, y2)], color)
    cv.circle(cx, cy, r // 3, color)


# ------------------------------------------------------------------- drawing
def draw_header(cv):
    cv.rect(0, 0, W, 112, NAVY)
    cv.rect(0, 108, W, 4, GOLD)
    cv.text_center(16, "THE WORLD TODAY", 6, WHITE)
    cv.text_center(72, "MONDAY 23 NOVEMBER 2026", 3, GOLD2)
    cv.text(24, 76, "NO. 327", 2, GOLD2)


def draw_hero(cv):
    x0, y0, x1, y1 = 24, 124, 1000, 500
    w, h = x1 - x0, y1 - y0
    # Dusk sky over Antalya: violet dusk melting into scorched orange.
    for i in range(h - 64):
        t = i / float(max(1, h - 65))
        if t < 0.55:
            u = t / 0.55
            c = tuple(int(DUSK_TOP[k] + (DUSK_MID[k] - DUSK_TOP[k]) * u)
                      for k in range(3))
        else:
            u = (t - 0.55) / 0.45
            c = tuple(int(DUSK_MID[k] + (DUSK_BOT[k] - DUSK_MID[k]) * u)
                      for k in range(3))
        cv.rect(x0, y0 + i, w, 1, c)
    # Low scorched sun.
    cv.circle(830, 210, 46, (240, 196, 110))
    cv.circle(830, 210, 34, (248, 220, 150))
    # Cracked globe, centre-left.
    gx, gy, gr = 300, 290, 108
    cv.circle(gx, gy, gr, (46, 111, 176))
    cv.circle(gx, gy, gr - 6, (58, 128, 190))
    # Continents as green blobs.
    cv.ellipse(gx - 42, gy - 34, 44, 26, (62, 142, 77))
    cv.ellipse(gx + 38, gy + 8, 40, 30, (62, 142, 77))
    cv.ellipse(gx - 8, gy + 52, 34, 20, (52, 128, 70))
    cv.ellipse(gx + 58, gy - 48, 24, 16, (62, 142, 77))
    # The crack: a jagged black fault across the globe.
    crack = [(gx - 96, gy - 52), (gx - 58, gy - 18), (gx - 30, gy - 44),
             (gx + 4, gy - 6), (gx + 34, gy - 30), (gx + 62, gy + 6),
             (gx + 96, gy - 14)]
    for a, b in zip(crack, crack[1:]):
        cv.line(a[0], a[1], b[0], b[1], (12, 12, 14), thick=7)
    cv.line(gx - 40, gy + 58, gx - 12, gy + 88, (12, 12, 14), thick=5)
    cv.line(gx - 12, gy + 88, gx + 22, gy + 70, (12, 12, 14), thick=5)
    # Oil derricks and smokestacks on the right, silhouetted.
    for bx, bh in ((640, 150), (700, 180), (760, 140)):
        cv.rect(bx, 436 - bh, 14, bh, (24, 20, 28))
        cv.rect(bx - 8, 436 - bh, 30, 10, (24, 20, 28))
        cv.circle(bx + 7, 436 - bh - 16, 12, (90, 84, 88))
        cv.circle(bx + 18, 436 - bh - 30, 15, (110, 104, 106))
    cv.poly([(820, 436), (860, 300), (880, 300), (920, 436)], (24, 20, 28))
    cv.circle(872, 292, 10, (90, 84, 88))
    cv.circle(886, 276, 13, (110, 104, 106))
    # Ground line and delegates walking away from the summit.
    cv.rect(x0, 400, w, 36, (16, 16, 22))
    for px in (110, 168, 226, 700, 758):
        person(cv, px, 434, 34, (216, 196, 160))
    # Headline band (bottom strip of the hero panel).
    cv.rect(x0, 436, w, 64, (10, 10, 14))
    cv.rect(x0, 436, w, 3, GOLD)
    cv.text(x0 + 20, 448, "COP31 COLLAPSES", 4, WHITE)
    cv.text(x0 + 20, 478, "NO FOSSIL-FUEL DEAL - LONGEST CLIMATE SUMMIT ENDS EMPTY IN ANTALYA",
            2, GOLD2)
    # Border.
    cv.rect(x0, y0, w, 3, INK)
    cv.rect(x0, y1 - 3, w, 3, INK)
    cv.rect(x0, y0, 3, h, INK)
    cv.rect(x1 - 3, y0, 3, h, INK)


def cell_frame(cv, x, y, w, h):
    cv.rect(x, y, w, h, WHITE)
    cv.rect(x, y, w, 3, INK)
    cv.rect(x, y + h - 3, w, 3, INK)
    cv.rect(x, y, 3, h, INK)
    cv.rect(x + w - 3, y, 3, h, INK)


def draw_gulf(cv, x, y, w, h):
    cell_frame(cv, x, y, w, h)
    cv.rect(x + 3, y + 3, w - 6, 34, (122, 30, 24))
    cv.text(x + 12, y + 9, "GULF WAR ESCALATES", 3, WHITE)
    # Sea, tanker, missiles.
    ix, iy, iw, ih = x + 3, y + 40, 168, h - 43
    cv.vgrad(ix, iy, iw, ih, (20, 70, 88), (10, 34, 48))
    cv.rect(ix, iy + ih - 26, iw, 26, (8, 26, 38))
    # Tanker hull and containers.
    cv.poly([(ix + 12, iy + ih - 26), (ix + 156, iy + ih - 26),
             (ix + 146, iy + ih - 12), (ix + 22, iy + ih - 12)], (12, 12, 14))
    cv.rect(ix + 30, iy + ih - 52, 96, 26, (150, 60, 44))
    cv.rect(ix + 34, iy + ih - 48, 26, 18, (200, 130, 60))
    cv.rect(ix + 66, iy + ih - 48, 26, 18, (90, 140, 90))
    cv.rect(ix + 98, iy + ih - 48, 26, 18, (200, 130, 60))
    cv.rect(ix + 132, iy + ih - 66, 6, 40, (12, 12, 14))
    # Missile streaks and explosion over the tanker.
    cv.line(ix + 20, iy + 8, ix + 90, iy + 70, (255, 170, 60), thick=3)
    cv.line(ix + 60, iy + 4, ix + 120, iy + 64, (255, 200, 110), thick=3)
    burst(cv, ix + 128, iy + 44, 22, (255, 190, 70))
    burst(cv, ix + 128, iy + 44, 12, (255, 120, 40))
    tx = x + 182
    cv.wrapped(tx, y + 48, "IRAN HITS US BASES IN BAHRAIN - MISSILES AND DRONES AT AL-RIFFA AND AWALI.",
               2, INK, w - 194, line_h=19)
    cv.wrapped(tx, y + 124, "CIVILIAN PLANT BURNS ON SITRA ISLAND; TANKERS STRUCK IN THE STRAIT OF HORMUZ.",
               2, (90, 30, 24), w - 194, line_h=19)


def draw_ukraine(cv, x, y, w, h):
    cell_frame(cv, x, y, w, h)
    cv.rect(x + 3, y + 3, w - 6, 34, NAVY2)
    cv.text(x + 12, y + 9, "KYIV REGION HIT", 3, WHITE)
    ix, iy, iw, ih = x + 3, y + 40, 168, h - 43
    cv.vgrad(ix, iy, iw, ih, NIGHT, (70, 76, 96))
    cv.circle(ix + 132, iy + 26, 16, (232, 220, 180))
    # Apartment block, right section collapsed.
    cv.rect(ix + 22, iy + 52, 60, ih - 52, (150, 148, 142))
    cv.poly([(ix + 82, iy + 52), (ix + 146, iy + 52), (ix + 146, iy + 96),
             (ix + 128, iy + 78), (ix + 110, iy + 100), (ix + 96, iy + 82),
             (ix + 82, iy + 100)], (120, 116, 110))
    for wy in (iy + 64, iy + 84, iy + 104):
        for wx in (ix + 30, ix + 48, ix + 66):
            cv.rect(wx, wy, 10, 12, (255, 210, 90))
    cv.rect(ix + 96, iy + 110, 34, 10, (255, 150, 60))
    # Drone overhead.
    cv.line(ix + 96, iy + 18, ix + 124, iy + 30, (220, 220, 220), thick=2)
    cv.line(ix + 124, iy + 18, ix + 96, iy + 30, (220, 220, 220), thick=2)
    cv.circle(ix + 110, iy + 24, 4, (220, 220, 220))
    tx = x + 182
    cv.wrapped(tx, y + 48, "DRONE FLATTENS A FLAT BLOCK IN DYMER: 4 KILLED, 14 MISSING UNDER THE RUBBLE.",
               2, INK, w - 194, line_h=19)
    cv.wrapped(tx, y + 124, "186 DRONES IN ONE NIGHT; 165 MISSILES IN THE WEEK, ZELENSKYY SAYS.",
               2, (40, 60, 110), w - 194, line_h=19)


def draw_ai(cv, x, y, w, h):
    cell_frame(cv, x, y, w, h)
    cv.rect(x + 3, y + 3, w - 6, 34, (74, 32, 96))
    cv.text(x + 12, y + 9, "AI ON TRIAL", 3, WHITE)
    ix, iy, iw, ih = x + 3, y + 40, 168, h - 43
    cv.vgrad(ix, iy, iw, ih, (52, 26, 78), (24, 16, 44))
    # Robot head.
    cv.rect(ix + 44, iy + 34, 80, 66, (200, 200, 210))
    cv.rect(ix + 44, iy + 34, 80, 10, (150, 150, 165))
    cv.rect(ix + 58, iy + 56, 18, 14, (40, 180, 200))
    cv.rect(ix + 92, iy + 56, 18, 14, (40, 180, 200))
    cv.rect(ix + 62, iy + 82, 44, 5, (60, 60, 70))
    cv.rect(ix + 80, iy + 24, 8, 10, (200, 200, 210))
    cv.circle(ix + 84, iy + 20, 6, (255, 80, 80))
    # Binary rain dots.
    for dx, dy in ((18, 20), (30, 90), (140, 24), (148, 100), (24, 130), (142, 130)):
        cv.circle(ix + dx, iy + dy, 3, (120, 220, 200))
    # Gavel / scales hint: a small chip.
    cv.rect(ix + 52, iy + 112, 64, 26, (30, 30, 40))
    cv.rect(ix + 60, iy + 118, 48, 14, (212, 164, 65))
    tx = x + 182
    cv.wrapped(tx, y + 48, "UN AGREES TO KEEP NEGOTIATING RULES FOR LETHAL AI SYSTEMS.",
               2, INK, w - 194, line_h=19)
    cv.wrapped(tx, y + 105, "SOUTH KOREA'S EDUCATION MINISTER QUITS OVER AI EXAM-CHEATING SCANDAL.",
               2, (74, 32, 96), w - 194, line_h=19)


def draw_brief(cv, x, y, w, h):
    cell_frame(cv, x, y, w, h)
    cv.rect(x + 3, y + 3, w - 6, 34, (30, 90, 70))
    cv.text(x + 12, y + 9, "WORLD IN BRIEF", 3, WHITE)
    items = [
        ("INDONESIA FACTORY FIRE: 50 MISSING", (122, 30, 24)),
        ("SOUTH SUDAN: 24 CIVILIANS KILLED", INK),
        ("NEPAL PM MEETS MODI IN DELHI", INK),
        ("MEXICO NABS CARTEL BOSS EL CHAPO ISIDRO", (40, 60, 110)),
    ]
    yy = y + 48
    for txt, col in items:
        cv.circle(x + 18, yy + 6, 4, GOLD)
        yy = cv.wrapped(x + 32, yy, txt, 2, col, w - 44, line_h=19)
        yy += 8


def draw_footer(cv):
    cv.rect(0, 948, W, 76, NAVY)
    cv.rect(0, 948, W, 4, GOLD)
    cv.text_center(966, "COP31 FAILS  *  GULF BURNS  *  KYIV HIT  *  AI RECKONING",
                   2, WHITE)
    cv.text_center(992, "ONE IMAGE - THE WORLD OF MONDAY 23 NOVEMBER 2026",
                   2, GOLD2)


def build():
    cv = Canvas()
    cv.rect(0, 0, W, H, PAPER)
    draw_header(cv)
    draw_hero(cv)
    gy1, gy2 = 516, 732
    gw, gh = 482, 200
    draw_gulf(cv, 24, gy1, gw, gh)
    draw_ukraine(cv, 518, gy1, gw, gh)
    draw_ai(cv, 24, gy2, gw, gh)
    draw_brief(cv, 518, gy2, gw, gh)
    draw_footer(cv)
    # Outer frame.
    cv.rect(0, 0, W, 8, INK)
    cv.rect(0, H - 8, W, 8, INK)
    cv.rect(0, 0, 8, H, INK)
    cv.rect(W - 8, 0, 8, H, INK)
    return cv


# ---------------------------------------------------------------------- PNG
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(cv, path):
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    raw = bytearray()
    for row in cv.rows:
        raw.append(0)
        raw += row
    data = b"\x89PNG\r\n\x1a\n"
    data += _chunk(b"IHDR", ihdr)
    data += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    data += _chunk(b"IEND", b"")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)
    return len(data)


def main():
    cv = build()
    size = write_png(cv, OUT)
    print("wrote %s (%d bytes, %dx%d)" % (OUT, size, W, H))
    return 0


if __name__ == "__main__":
    sys.exit(main())
