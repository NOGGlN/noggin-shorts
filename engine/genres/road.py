"""Road Rules quiz ("Who has to wait?"): a top-down illustrated junction, two cars ("You" and "Car") with dotted routes,
a white question card, a calm British voice reading it, a countdown, then the answer with the reason.
Short (9:16): 1 scene, card on top.  Video (16:9): several scenes, card on the left.

spec["scenes"] = [{"type": "crossroads_right" | "roundabout_enter" | "roundabout_2lane_exit" | "left_turn",
                   "place": "Crossroads in Portugal", "lines": ["No signs. No lights.", "You go straight."],
                   "question": "Who has to wait - you or the car?", "answer": "you" | "car",
                   "answer_line": "YOU wait.", "why": "No signs? Traffic from your right goes first."}]
Rules must be real (Portugal by default). The scene type decides the geometry; "answer" decides who stops and who goes first.
"""
import math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import gcommon as g

PAVE, TILE, ASPH, CURB = (232, 227, 215), (219, 213, 199), (58, 61, 68), (205, 200, 190)
GRASS, GRASS2, LANE = (150, 194, 108), (136, 182, 96), (240, 240, 236)
YOU_C, CAR_C = (233, 86, 58), (246, 246, 244)
RED, GREEN, INKC = (229, 80, 52), (46, 160, 90), (20, 20, 24)
S = 2   # supersampling for the static background
SPEED = 1.12  # owner: "talk a bit faster"

# ------------------------------------------------------------------ geometry helpers
def arc(cx, cy, r, a0, a1, n=40):
    return [(cx + r*math.cos(math.radians(a0 + (a1 - a0)*k/n)), cy + r*math.sin(math.radians(a0 + (a1 - a0)*k/n))) for k in range(n + 1)]

class Path:
    def __init__(self, pts):
        self.p = np.array(pts, float); seg = np.linalg.norm(np.diff(self.p, axis=0), axis=1)
        self.cum = np.concatenate([[0], np.cumsum(seg)]); self.L = self.cum[-1]
    def at(self, s):
        s = min(max(s, 0), self.L - 1e-6); i = np.searchsorted(self.cum, s) - 1; i = max(0, min(i, len(self.p) - 2))
        u = (s - self.cum[i])/max(1e-9, self.cum[i + 1] - self.cum[i]); a, b = self.p[i], self.p[i + 1]
        x, y = a + (b - a)*u; ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
        return x, y, ang
    def s_of(self, x, y):                      # arc length of the path point nearest to (x, y)
        best, bs = 1e18, 0
        for k in range(len(self.p) - 1):
            a, b = self.p[k], self.p[k + 1]; d = b - a; L2 = max(1e-9, d @ d)
            u = min(1, max(0, ((np.array([x, y]) - a) @ d)/L2)); q = a + d*u; dist = np.linalg.norm(q - [x, y])
            if dist < best: best, bs = dist, self.cum[k] + u*math.sqrt(L2)
        return bs

def scene_geometry(kind, cx, cy, W, H):
    """-> (draw_fn(dr, scale), you_path, car_path, you_stop_s, car_stop_s)."""
    far = max(W, H) + 400
    if kind in ("crossroads_right", "left_turn"):
        RW = 380; hl = RW/2; ln = RW/4
        def draw(d, k):
            d.rectangle(((cx - hl)*k, -10, (cx + hl)*k, H*k + 10), fill=ASPH); d.rectangle((-10, (cy - hl)*k, W*k + 10, (cy + hl)*k), fill=ASPH)
            for (x0, x1) in ((-50, cx - hl - 20), (cx + hl + 20, W + 50)):                   # centre dashes, horizontal
                x = x0
                while x < x1: d.rectangle((x*k, (cy - 4)*k, min(x + 46, x1)*k, (cy + 4)*k), fill=LANE); x += 86
            for (y0, y1) in ((-50, cy - hl - 20), (cy + hl + 20, H + 50)):
                y = y0
                while y < y1: d.rectangle(((cx - 4)*k, y*k, (cx + 4)*k, min(y + 46, y1)*k), fill=LANE); y += 86
            for sx in (-1, 1):                                                                 # kerbs, paving, grass, trees
                for sy in (-1, 1):
                    x0, y0 = cx + sx*hl, cy + sy*hl
                    gx0, gx1 = sorted((x0, x0 + sx*1400)); gy0, gy1 = sorted((y0, y0 + sy*1400))
                    d.rounded_rectangle((gx0*k, gy0*k, gx1*k, gy1*k), radius=60*k, fill=CURB)
                    d.rounded_rectangle(((gx0 + 12)*k, (gy0 + 12)*k, (gx1 - 12)*k, (gy1 - 12)*k), radius=50*k, fill=PAVE)
                    ex, ey = x0 + sx*70, y0 + sy*70                                            # grass bed near the corner
                    bx0, bx1 = sorted((ex, ex + sx*250)); by0, by1 = sorted((ey, ey + sy*250))
                    d.rounded_rectangle((bx0*k, by0*k, bx1*k, by1*k), radius=50*k, fill=GRASS)
                    tree(d, ex + sx*125, ey + sy*125, 90, k)
        if kind == "left_turn":    # you: from the south turning left (west); car: from the north going straight south
            you = Path([(cx + ln, cy + far), (cx + ln, cy + hl)] + arc(cx - hl, cy + hl, hl + ln, 0, -90)[1:] + [(cx - far, cy - ln)])
            car = Path([(cx - ln, cy - far), (cx - ln, cy + far)])
            return draw, you, car, you.s_of(cx + ln, cy + hl + 95), car.s_of(cx - ln, cy - hl - 110)
        you = Path([(cx + ln, cy + far), (cx + ln, cy - far)])
        car = Path([(cx + far, cy - ln), (cx - far, cy - ln)])
        return draw, you, car, you.s_of(cx + ln, cy + hl + 95), car.s_of(cx + hl + 70, cy - ln)
    # ---- roundabouts (anticlockwise, right-hand traffic)
    R, RI = (480, 200) if kind == "roundabout_2lane_exit" else (440, 210); RW = 330; hl = RW/2
    two = kind == "roundabout_2lane_exit"
    def draw(d, k):
        d.rectangle(((cx - hl)*k, -10, (cx + hl)*k, H*k + 10), fill=ASPH); d.rectangle((-10, (cy - hl)*k, W*k + 10, (cy + hl)*k), fill=ASPH)
        d.ellipse(((cx - R - 14)*k, (cy - R - 14)*k, (cx + R + 14)*k, (cy + R + 14)*k), fill=CURB)
        d.ellipse(((cx - R)*k, (cy - R)*k, (cx + R)*k, (cy + R)*k), fill=ASPH)
        d.rectangle(((cx - hl)*k, -10, (cx + hl)*k, H*k + 10), fill=ASPH); d.rectangle((-10, (cy - hl)*k, W*k + 10, (cy + hl)*k), fill=ASPH)
        for sx in (-1, 1):                                                 # paving corners with rounded fillets
            for sy in (-1, 1):
                x0, y0 = cx + sx*hl, cy + sy*hl
                gx0, gx1 = sorted((x0 + sx*14, x0 + sx*1200)); gy0, gy1 = sorted((y0 + sy*14, y0 + sy*1200))
                corner = Image.new("L", (int((gx1 - gx0)*k), int((gy1 - gy0)*k)), 0); dc = ImageDraw.Draw(corner)
                dc.rectangle((0, 0, corner.width, corner.height), fill=255)
                ccx, ccy = (cx - gx0)*k, (cy - gy0)*k; dc.ellipse((ccx - (R + 14)*k, ccy - (R + 14)*k, ccx + (R + 14)*k, ccy + (R + 14)*k), fill=0)
                d._image.paste(Image.new("RGB", corner.size, CURB), (int(gx0*k), int(gy0*k)), corner)
                corner2 = corner.filter(ImageFilter.MinFilter(int(10*k)*2+1))
                d._image.paste(Image.new("RGB", corner.size, PAVE), (int(gx0*k), int(gy0*k)), corner2)
                tx, ty = cx + sx*(R + 170), cy + sy*(hl + 190)
                tree(d, tx, ty, 90, k)
        for a in range(0, 360, 90):                                       # give-way teeth at each entry (right half of the arm)
            ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
            for j in range(4):
                off = 22 + j*36; px, py = cx + ca*(R + 30) - sa*off, cy + sa*(R + 30) + ca*off
                tri = [(px + ca*18, py + sa*18), (px - ca*12 - sa*12, py - sa*12 + ca*12), (px - ca*12 + sa*12, py - sa*12 - ca*12)]
                d.polygon([(x*k, y*k) for x, y in tri], fill=LANE)
            for j in range(0, 260, 70):                                   # centre dashes on the arms
                p0 = R + 70 + j; d.line(((cx + ca*p0)*k, (cy + sa*p0)*k, (cx + ca*(p0 + 40))*k, (cy + sa*(p0 + 40))*k), fill=LANE, width=int(8*k))
        if two:
            rm = (R + RI)/2
            for a in range(0, 360, 12): d.arc(((cx - rm)*k, (cy - rm)*k, (cx + rm)*k, (cy + rm)*k), a, a + 6, fill=LANE, width=int(7*k))
        d.ellipse(((cx - RI)*k, (cy - RI)*k, (cx + RI)*k, (cy + RI)*k), fill=(196, 186, 170))
        d.ellipse(((cx - RI + 26)*k, (cy - RI + 26)*k, (cx + RI - 26)*k, (cy + RI - 26)*k), fill=GRASS)
        for rr in (RI - 60, RI - 110): d.ellipse(((cx - rr)*k, (cy - rr)*k, (cx + rr)*k, (cy + rr)*k), outline=GRASS2, width=int(6*k))
        rng = np.random.default_rng(3)
        for _ in range(60):
            a, rr = rng.uniform(0, 2*math.pi), rng.uniform(40, RI - 40); x, y = cx + rr*math.cos(a), cy + rr*math.sin(a)
            d.ellipse(((x - 5)*k, (y - 5)*k, (x + 5)*k, (y + 5)*k), fill=[(255, 255, 255), (250, 214, 90), (240, 150, 170)][_ % 3])
        sx, sy = cx - 70, cy - 60                                            # blue roundabout sign
        d.line((sx*k, sy*k, sx*k, (sy + 110)*k), fill=(70, 70, 76), width=int(8*k))
        d.ellipse(((sx - 62)*k, (sy - 62)*k, (sx + 62)*k, (sy + 62)*k), fill=(255, 255, 255))
        d.ellipse(((sx - 55)*k, (sy - 55)*k, (sx + 55)*k, (sy + 55)*k), fill=(32, 92, 200))
        for a0 in (20, 140, 260):
            d.arc(((sx - 33)*k, (sy - 33)*k, (sx + 33)*k, (sy + 33)*k), -a0 - 80, -a0, fill=(255, 255, 255), width=int(9*k))
            ex, ey = sx + 33*math.cos(math.radians(-a0 - 80)), sy + 33*math.sin(math.radians(-a0 - 80))
            d.ellipse(((ex - 9)*k, (ey - 9)*k, (ex + 9)*k, (ey + 9)*k), fill=(255, 255, 255))
    lane_in, lane_out = (R + RI)/2 + (55 if two else 0), (R + RI)/2 - (0 if not two else 55)
    if kind == "roundabout_enter":
        # you: enter from the south (right half of the arm) and leave north; car: already circulating from the west side.
        rr = (R + RI)/2
        you = Path([(cx + hl/2, cy + far), (cx + hl/2, cy + R + 20)] + arc(cx, cy, rr, 70, -90, 40)[3:] + [(cx + hl/2, cy - R - 20), (cx + hl/2, cy - far)])
        # anticlockwise on screen = increasing angle in maths, decreasing in screen coords: west (180) -> south (90) -> east (0)
        car = Path(arc(cx, cy, rr, 225, 90, 30) + arc(cx, cy, rr, 90, 25, 20)[1:] + [(cx + R + 40, cy + hl/2), (cx + far, cy + hl/2)])
        return draw, you, car, you.s_of(cx + hl/2, cy + R + 105), car.s_of(cx + rr*math.cos(math.radians(150)), cy + rr*math.sin(math.radians(150)))
    # two-lane exit: car on the inner lane wants the east exit; you keep going round on the outer lane.
    ro, ri = R - 72, RI + 72
    car = Path(arc(cx, cy, ri, 160, 60, 30) + [(cx + ro*math.cos(math.radians(20)), cy + ro*math.sin(math.radians(20))), (cx + R + 40, cy + hl/2), (cx + far, cy + hl/2)])
    you = Path(arc(cx, cy, ro, 140, -120, 60))
    return draw, you, car, you.s_of(cx + ro*math.cos(math.radians(110)), cy + ro*math.sin(math.radians(110))), car.s_of(cx + ri*math.cos(math.radians(62)), cy + ri*math.sin(math.radians(62)))

def tree(d, x, y, r, k):
    d.ellipse(((x - r + 12)*k, (y - r + 16)*k, (x + r + 12)*k, (y + r + 16)*k), fill=(120, 140, 110))   # shadow
    d.ellipse(((x - r)*k, (y - r)*k, (x + r)*k, (y + r)*k), fill=(70, 140, 70))
    for rr in (r*0.72, r*0.45): d.ellipse(((x - rr)*k, (y - rr)*k, (x + rr)*k, (y + rr)*k), outline=(96, 166, 92), width=int(5*k))

# ------------------------------------------------------------------ sprites
_car_cache = {}
def car_sprite(color, label):
    k = (color, label)
    if k in _car_cache: return _car_cache[k]
    w, h, sc = 120, 230, 3; im = Image.new("RGBA", ((w + 40)*sc, (h + 40)*sc), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    def R(x0, y0, x1, y1, r, f): d.rounded_rectangle(((x0 + 20)*sc, (y0 + 20)*sc, (x1 + 20)*sc, (y1 + 20)*sc), radius=r*sc, fill=f)
    dark = tuple(int(c*0.72) for c in color)
    R(0, 0, w, h, 34, dark); R(4, 4, w - 4, h - 4, 30, color)
    R(14, 42, w - 14, 82, 14, (34, 36, 44)); R(16, 170, w - 16, 200, 12, (34, 36, 44))             # windscreen + rear window
    R(18, 86, w - 18, 166, 16, tuple(min(255, int(c*1.04)) for c in color))                         # roof
    for x in (10, w - 26): R(x, 6, x + 16, 18, 5, (255, 236, 160)); R(x, h - 16, x + 16, h - 7, 4, (210, 50, 40))
    R(-8, 70, 4, 86, 4, dark); R(w - 4, 70, w + 8, 86, 4, dark)                                      # mirrors
    im2 = im.resize((w + 40, h + 40), Image.LANCZOS)
    sh = Image.new("RGBA", im2.size, (0, 0, 0, 0)); sh.putalpha(im2.getchannel("A").point(lambda v: int(v*0.35)).filter(ImageFilter.GaussianBlur(9)))
    out = Image.new("RGBA", (im2.width + 20, im2.height + 20), (0, 0, 0, 0)); out.alpha_composite(sh, (14, 16)); out.alpha_composite(im2, (0, 0))
    _car_cache[k] = out; return out

def place_car(base, spr, x, y, ang, label, dark_text, Z=1.0):
    r = spr.rotate(-(ang + 90), Image.BICUBIC, expand=True)       # sprite faces up (-90 deg); path angle 0 = east
    base.alpha_composite(r, (int(x - r.width/2), int(y - r.height/2)))
    f = g.font(g.XB, int(40*Z)); ImageDraw.Draw(base).text((x, y), label, font=f, anchor="mm", fill=INKC if dark_text else (255, 255, 255),
                                                    stroke_width=int(3*Z), stroke_fill=(255, 255, 255) if dark_text else (120, 40, 25))

def dotted(base, path, s0, s1, color, a=1.0, Z=1.0):
    d = ImageDraw.Draw(base); s = s0 + 150
    while s < s1 - 60:
        x, y, _ = path.at(s); x, y = x*Z, y*Z; r = 9*Z
        d.ellipse((x - r, y - r, x + r, y + r), fill=color + (int(235*a),)); s += 34
    x, y, ang = path.at(s1 - 30); x, y = x*Z, y*Z; ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang)); q = Z
    tri = [(x + ca*30*q, y + sa*30*q), (x - ca*18*q - sa*24*q, y - sa*18*q + ca*24*q), (x - ca*18*q + sa*24*q, y - sa*18*q - ca*24*q)]
    d.polygon(tri, fill=color + (int(235*a),))

def wrap(txt, font, maxw):
    words, lines, cur = txt.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if font.getlength(t) <= maxw or not cur: cur = t
        else: lines.append(cur); cur = w
    return lines + ([cur] if cur else [])

LET = "ABCD"
def card(sc, w, reveal=0.0, count=None):
    """The question card: place label, statement lines, red question, then A-D options.
    reveal: the correct option turns green with a tick, the others fade, and the reason appears."""
    vert = w > 900; pad = 40; maxw = w - 2*pad
    lab = g.font(g.XB, 38 if vert else 32); big = g.font(g.BLACK, 66 if vert else 48); opt = g.font(g.XB, 48 if vert else 36)
    small = g.font(g.XB, 42 if vert else 32)
    rows = [("t", l, lab, RED) for l in wrap(sc["place"], lab, maxw)]
    for l in sc["lines"]: rows += [("t", x, big, INKC) for x in wrap(l, big, maxw)]
    rows += [("t", x, big, RED) for x in wrap(sc["question"], big, maxw)]
    rows.append(("gap", "", None, None))
    for j, o in enumerate(sc["options"]):
        ls = wrap(o, opt, maxw - 90)
        for q, l in enumerate(ls): rows.append(("o", (j, q, l), opt, None))
    if reveal >= 0.5: rows += [("gap", "", None, None)] + [("t", x, small, (60, 60, 66)) for x in wrap(sc["why"], small, maxw)]
    else: rows += [("gap", "", None, None), ("c", "Comment A, B, C or D", small, INKC)]
    def hh(r):
        if r[0] == "gap": return 14
        if r[0] == "o": return r[2].getbbox("Hg")[3] + (26 if r[1][1] == 0 else 12)
        return r[2].getbbox("Hg")[3] + 12
    ht = sum(hh(r) for r in rows) + 2*pad
    im = Image.new("RGBA", (w + 40, ht + 40), (0, 0, 0, 0)); sh = Image.new("L", im.size, 0)
    ImageDraw.Draw(sh).rounded_rectangle((20, 26, w + 20, ht + 26), 36, fill=90); sh = sh.filter(ImageFilter.GaussianBlur(14))
    im = Image.composite(Image.new("RGBA", im.size, (0, 0, 0, 255)), Image.new("RGBA", im.size, (0, 0, 0, 0)), sh)
    d = ImageDraw.Draw(im); d.rounded_rectangle((20, 20, w + 20, ht + 20), 36, fill=(250, 250, 248, 245))
    y = 20 + pad; x0 = 20 + pad
    for r in rows:
        h = hh(r)
        if r[0] in ("t", "c"):
            d.text((x0, y), r[1], font=r[2], fill=r[3])
            if r[0] == "c": im.alpha_composite(g.emoji("👇", 50), (int(x0 + r[2].getlength(r[1]) + 12), int(y - 6)))
        elif r[0] == "o":
            j, q, l = r[1]; ok = j == sc["correct"]; fade = reveal >= 0.5 and not ok
            col = (175, 175, 180) if fade else (GREEN if reveal >= 0.5 and ok else INKC)
            if q == 0:
                if reveal >= 0.5 and ok:
                    d.rounded_rectangle((x0 - 14, y - 10, w + 20 - pad + 14, y + r[2].getbbox("Hg")[3] + 12), 18, fill=(222, 244, 228))
                rr = 30; bx, by = x0 + rr, y + r[2].getbbox("Hg")[3]/2 + 2
                d.ellipse((bx - rr, by - rr, bx + rr, by + rr), fill=(GREEN if reveal >= 0.5 and ok else ((205, 205, 210) if fade else RED)))
                if reveal >= 0.5 and ok: d.line([(bx - 13, by + 1), (bx - 3, by + 11), (bx + 14, by - 10)], fill=(255, 255, 255), width=7, joint="curve")
                else: d.text((bx, by), LET[j], font=g.font(g.BLACK, 34 if vert else 28), fill=(255, 255, 255), anchor="mm")
            d.text((x0 + 80, y), l, font=r[2], fill=col)
        y += h
    if count is not None and reveal < 0.5:                       # countdown badge in the card's corner
        cxr, cyr, r = w + 20 - 66, 20 + 66, 44
        d.ellipse((cxr - r, cyr - r, cxr + r, cyr + r), fill=RED); d.text((cxr, cyr), str(count), font=g.font(g.BLACK, 54), fill=(255, 255, 255), anchor="mm")
    return im

def badge(txt, col):
    f = g.font(g.BLACK, 44); w = int(f.getlength(txt)) + 50
    im = Image.new("RGBA", (w, 74), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, 73), 37, fill=col + (255,)); d.text((w/2, 38), txt, font=f, fill=(255, 255, 255), anchor="mm"); return im


# ------------------------------------------------------------------ "around the world" comparison
ISO = {"Portugal": "PT", "Spain": "ES", "France": "FR", "Germany": "DE", "Italy": "IT", "UK": "GB", "USA": "US", "Japan": "JP",
       "Australia": "AU", "Brazil": "BR", "Canada": "CA", "Netherlands": "NL", "Belgium": "BE", "Poland": "PL", "Ireland": "IE",
       "India": "IN", "Switzerland": "CH", "Austria": "AT", "Mexico": "MX", "China": "CN", "South Korea": "KR"}
SAY = {"UK": "the U K", "USA": "the U S A", "Netherlands": "the Netherlands"}
def compare_vo(cmp):
    same = [SAY.get(c, c) for c in cmp.get("same", [])]
    out = ""
    if same: out = "Same rule in " + (", ".join(same[:-1]) + " and " + same[-1] if len(same) > 1 else same[0]) + ". "
    for k, (c, note) in enumerate(cmp.get("different", [])):
        out += ("But in " if k == 0 else "In ") + SAY.get(c, c) + ", " + note[0].lower() + note[1:] + " "
    return out.strip()

def compare_panel(cmp, w):
    """White card: 'Around the world' with flags. Same rule (green) / different (red) + a short note each."""
    vert = w > 900; pad = 44; lab = g.font(g.XB, 40 if vert else 34); head = g.font(g.BLACK, 60 if vert else 46)
    name = g.font(g.BLACK, 46 if vert else 36); note = g.font(g.XB, 40 if vert else 32); fs = 64 if vert else 50
    rows = []                                                      # (kind, payload, height)
    rows.append(("text", ("Around the world", lab, RED), 56)); rows.append(("text", ("Same rule", head, GREEN), 80))
    same = cmp.get("same", []); per = 2
    for k in range(0, len(same), per): rows.append(("flags", same[k:k + per], fs + 24))
    if cmp.get("different"):
        rows.append(("gap", None, 16)); rows.append(("text", ("Different", head, RED), 80))
        for c, nt in cmp["different"]:
            lines = wrap(nt, note, w - 2*pad - fs - 30)
            rows.append(("diff", (c, lines), max(fs, 54 + 48*len(lines)) + 22))
    ht = sum(r[2] for r in rows) + 2*pad
    im = Image.new("RGBA", (w + 40, ht + 40), (0, 0, 0, 0)); sh = Image.new("L", im.size, 0)
    ImageDraw.Draw(sh).rounded_rectangle((20, 26, w + 20, ht + 26), 36, fill=90); sh = sh.filter(ImageFilter.GaussianBlur(14))
    im = Image.composite(Image.new("RGBA", im.size, (0, 0, 0, 255)), Image.new("RGBA", im.size, (0, 0, 0, 0)), sh)
    d = ImageDraw.Draw(im); d.rounded_rectangle((20, 20, w + 20, ht + 20), 36, fill=(250, 250, 248, 245)); y = 20 + pad; x0 = 20 + pad
    for kind, pl, hh in rows:
        if kind == "text": d.text((x0, y), pl[0], font=pl[1], fill=pl[2])
        elif kind == "flags":
            x = x0
            for c in pl:
                im.alpha_composite(g.emoji(g.flag(ISO[c]), fs), (int(x), int(y))); d.text((x + fs + 16, y + fs/2), c, font=name, fill=INKC, anchor="lm")
                x += (w - 2*pad)/per
        elif kind == "diff":
            c, lines = pl; im.alpha_composite(g.emoji(g.flag(ISO[c]), fs), (int(x0), int(y)))
            d.text((x0 + fs + 22, y), c, font=name, fill=INKC)
            for j, l in enumerate(lines): d.text((x0 + fs + 22, y + 54 + 48*j), l, font=note, fill=(70, 70, 76))
        y += hh
    return im


# ------------------------------------------------------------------ actors (2-3 vehicles) and signs
LABELS = {"you": "You", "car": "Car", "car2": "Car 2", "amb": "Ambulance"}
def scene_actors(kind, cx, cy, W, H):
    """-> (draw_fn, {name: (path, stop_s)}). Names: you, car, car2, amb."""
    base = {"crossroads_three": "crossroads_right", "crossroads_giveway": "crossroads_right",
            "crossroads_stop_right": "crossroads_right", "ambulance_left": "crossroads_right"}.get(kind, kind)
    draw0, you, car, ys, cs = scene_geometry(base, cx, cy, W, H)
    hl, ln, far = 190, 95, max(W, H) + 400
    left = Path([(cx - far, cy + ln), (cx + far, cy + ln)]); lstop = left.s_of(cx - hl - 60, cy + ln)   # from your left, eastbound
    actors, signs = {"you": (you, ys), "car": (car, cs)}, []
    if kind == "crossroads_three": actors["car2"] = (left, lstop)
    elif kind == "ambulance_left": actors = {"you": (you, ys), "amb": (left, lstop)}
    elif kind == "crossroads_giveway": actors = {"you": (you, ys), "car": (left, lstop)}; signs.append(("giveway", cx + hl + 75, cy + hl + 95))
    elif kind == "crossroads_stop_right": signs.append(("stop", cx + hl + 95, cy - hl - 75))
    def draw(d, k):
        draw0(d, k)
        for sg in signs: road_sign(d, *sg, k)
    return draw, actors

def road_sign(d, kind, x, y, k):
    d.ellipse(((x - 9)*k, (y + 46)*k, (x + 9)*k, (y + 58)*k), fill=(150, 145, 135))               # pole foot / shadow
    d.line((x*k, (y + 10)*k, x*k, (y + 52)*k), fill=(90, 90, 96), width=int(8*k))
    if kind == "giveway":
        r = 58; pts = [(x - r, y - r*0.6), (x + r, y - r*0.6), (x, y + r*0.95)]
        d.polygon([(a*k, b*k) for a, b in pts], fill=(214, 40, 40))
        r2 = 34; pts2 = [(x - r2, y - r2*0.55 + 4), (x + r2, y - r2*0.55 + 4), (x, y + r2*0.95 + 2)]
        d.polygon([(a*k, b*k) for a, b in pts2], fill=(255, 255, 255))
    else:
        r = 54; pts = [(x + r*math.cos(math.radians(22.5 + 45*j)), y + r*math.sin(math.radians(22.5 + 45*j))) for j in range(8)]
        d.polygon([(a*k, b*k) for a, b in pts], fill=(255, 255, 255))
        pts = [(x + (r - 6)*math.cos(math.radians(22.5 + 45*j)), y + (r - 6)*math.sin(math.radians(22.5 + 45*j))) for j in range(8)]
        d.polygon([(a*k, b*k) for a, b in pts], fill=(204, 30, 36))
        d.text((x*k, y*k), "STOP", font=g.font(g.BLACK, int(30*k)), fill=(255, 255, 255), anchor="mm")

def amb_sprite():
    base = car_sprite((248, 248, 246), "amb").copy(); d = ImageDraw.Draw(base); w, h = base.size
    for yy in (0.36, 0.62): d.rectangle((24, int(h*yy), w - 44, int(h*yy) + 14), fill=(214, 40, 40))
    d.rounded_rectangle((w*0.28, h*0.30, w*0.62, h*0.36), 6, fill=(60, 110, 230))                    # light bar
    return base

# ------------------------------------------------------------------ build
def build(spec, fmt):
    import tts
    W, H = g.W, g.H; vert = fmt == "short"; scenes = spec["scenes"]
    if vert: scenes = scenes[:1]
    cw = W - 60 if vert else 820; cardpos = (30 - 20, 100 - 20) if vert else (40 - 20, 40 - 20)
    plan, t = [], 0.0; voice = []; sprites = {}
    for i, sc in enumerate(scenes):
        rb = sc["type"].startswith("roundabout")                     # world units are zoomed by Z on screen
        Z = (1.0 if vert else 0.8) if rb else (1.3 if vert else 1.15); WW, HW = W/Z, H/Z
        cx, cy = (WW/2, HW*(0.66 if rb else 0.70)) if vert else (WW*0.71, HW/2)
        draw, actors = scene_actors(sc["type"], cx, cy, WW, HW)
        order = sc.get("order") or (["car", "you"] if sc.get("answer") == "you" else ["you", "car"])
        bg = Image.new("RGB", (W*S, H*S), PAVE); d = ImageDraw.Draw(bg); k = S*Z
        for x in np.arange(0, WW, 96): d.line((x*k, 0, x*k, H*S), fill=TILE, width=2*S)
        for y in np.arange(0, HW, 96): d.line((0, y*k, W*S, y*k), fill=TILE, width=2*S)
        draw(d, k); bg = bg.resize((W, H), Image.LANCZOS).convert("RGBA")
        opts = " ".join(f"{LET[j]}: {o.rstrip('.')}." for j, o in enumerate(sc["options"]))
        q = sc["place"] + ". " + " ".join(sc["lines"]) + " " + sc["question"].replace(" - ", ", ") + " " + opts
        a1, sr, _ = tts.say_gb(q, speed=SPEED)
        a2, _, _ = tts.say_gb(f"The answer is {LET[sc['correct']]}. " + sc["why"], speed=SPEED)
        t0 = t; tq = t0 + 0.6; tcount = tq + len(a1)/sr + 0.3; trev = tcount + 5.0; tgo = trev + 1.6
        tcmp = None; cmp = sc.get("compare")
        tgone = tgo + 1.9*len(order) + 1.2
        if cmp:
            tcmp = max(trev + 0.15 + len(a2)/sr + 0.5, tgone - 1.0)
            a3, _, _ = tts.say_gb(compare_vo(cmp), speed=SPEED); voice.append((tcmp + 0.5, a3))
            tend = tcmp + 0.5 + len(a3)/sr + 1.0 + (1.6 if i == len(scenes) - 1 else 0.4)
        else:
            tend = max(trev + len(a2)/sr + 0.6, tgone) + (1.6 if i == len(scenes) - 1 else 0.6)
        voice += [(tq, a1), (trev + 0.15, a2)]
        cardh = card(sc, cw, 1.0).height + cardpos[1] if vert else 0
        if Z not in sprites:
            sprites[Z] = {n: sp.resize((int(sp.width*Z*0.95), int(sp.height*Z*0.95)), Image.LANCZOS)
                          for n, sp in (("you", car_sprite(YOU_C, "You")), ("car", car_sprite(CAR_C, "Car")),
                                        ("car2", car_sprite((70, 120, 210), "Car 2")), ("amb", amb_sprite()))}
        plan.append(dict(tcmp=tcmp, Z=Z, cardh=cardh, sc=sc, bg=bg, actors=actors, order=order, t0=t0, tq=tq, tcount=tcount,
                         trev=trev, tgo=tgo, t1=tend))
        t = tend
    DUR = t; cards = {}
    ORD = ["1ST", "2ND", "3RD"]; OCOL = [GREEN, (230, 150, 30), RED]
    def frame(tt):
        p = next((p for p in plan if tt < p["t1"]), plan[-1]); lt = tt - p["t0"]; sc = p["sc"]
        im = p["bg"].copy(); Z = p["Z"]; spr = sprites[Z]
        def at(path, s_):
            x, y, a = path.at(s_); return x*Z, y*Z, a
        def pos(name, path, stop):
            arrive = min(1, (tt - p["t0"])/max(0.1, p["tq"] + 2.4 - p["t0"]))
            s = stop*(1 - (1 - arrive)**2.2)
            if tt > p["tgo"]:
                go = tt - p["tgo"] - 1.9*p["order"].index(name)
                if go > 0: s = stop + (260*go + 140*go*go)/Z
            return s
        S_ = {n: pos(n, pa, st) for n, (pa, st) in p["actors"].items()}
        da = g.ease((lt - 0.8)/0.6)*(1 - g.ease((tt - p["tgo"])/0.5))
        if da > 0.01:
            for n, (pa, st) in p["actors"].items():
                dotted(im, pa, S_[n], min(pa.L, S_[n] + 700), YOU_C if n == "you" else (70, 120, 210) if n == "car2" else CAR_C, da, Z)
        for n, (pa, st) in p["actors"].items():
            s_ = S_[n]
            if s_ < pa.L - 5:
                x, y, ang = at(pa, s_); place_car(im, spr[n], x, y, ang, sc.get("labels", {}).get(n, LABELS[n]), n in ("car", "amb"), Z)
                if n == "amb" and int(tt*6) % 2 == 0:                           # flashing blue lights
                    ImageDraw.Draw(im).ellipse((x - 26*Z, y - 26*Z, x + 26*Z, y + 26*Z), outline=(60, 120, 255, 230), width=int(6*Z))
        if p["trev"] <= tt < p["tgo"] + 1.9*len(p["order"]) + 0.6:            # 1ST / 2ND / 3RD badges
            kk = g.back((tt - p["trev"])/0.3)
            for n, (pa, st) in p["actors"].items():
                if n not in p["order"]: continue
                j = p["order"].index(n); x, y, _ = at(pa, S_[n]); off = 120*Z/1.3 + 50
                by = y - off if (y - off) > p["cardh"] + 40 else y + off
                bdg = badge(ORD[j] if len(p["order"]) > 2 or j else "GOES 1ST", OCOL[j] if j < 3 else RED)
                if len(p["order"]) == 2 and j == 1: bdg = badge("WAITS", RED)
                g.paste(im, bdg, min(max(x, bdg.width/2 + 20), W - bdg.width/2 - 20), by, kk)
        rev = 1.0 if tt >= p["trev"] else 0.0
        cnt = None if not (p["tcount"] <= tt < p["trev"]) else 5 - int(tt - p["tcount"])
        key = (id(p), rev, cnt)
        if key not in cards: cards[key] = card(sc, cw, rev, cnt)
        c = cards[key]; slide = g.ease((lt - 0.15)/0.45)
        if p["tcmp"] is not None and tt >= p["tcmp"]:
            u = g.ease((tt - p["tcmp"])/0.45); slide = 1 - u
            ck = ("cmp", id(p))
            if ck not in cards: cards[ck] = compare_panel(sc["compare"], cw)
            pc = cards[ck]; im.alpha_composite(pc, (int(cardpos[0]), int(cardpos[1] - (1 - u)*(pc.height + 140))))
        if slide > 0.001: im.alpha_composite(c, (int(cardpos[0]), int(cardpos[1] - (1 - slide)*(c.height + 140))))
        if tt > DUR - 1.6:
            a = g.ease((tt - (DUR - 1.6))/0.4); im.alpha_composite(Image.new("RGBA", (W, H), (20, 20, 24, int(200*a))))
            g.paste(im, g.T("FOLLOW FOR A NEW ROAD RULE", 64 if vert else 80, g.WHITE, 8, maxw=W - 80), W/2, H/2 - 50, a)
            g.paste(im, g.T("DID YOU GET IT RIGHT?", 52 if vert else 64, g.YEL, 7, maxw=W - 80), W/2, H/2 + 50, a)
        return im
    def audio(path):
        M = g.Mix(DUR, bed=0.05)
        for p in plan:
            M.add(M.whoosh(0.5), p["t0"] + 0.15, 0.5)
            for k in range(5): M.add(M.tick(1500 if k < 4 else 1900), p["tcount"] + k, 0.8)
            M.add(M.ding(1318.5), p["trev"], 0.8)
            if any(n == "amb" for n in p["actors"]):                          # soft two-tone siren
                y = np.arange(int(3.0*g.SR))/g.SR; f = np.where((y*2.5) % 1 < 0.5, 880, 660)
                M.add(0.06*np.sin(2*np.pi*np.cumsum(f)/g.SR)*np.minimum(1, y/0.5), p["t0"] + 0.2)
        for t0, a in voice:
            x = np.interp(np.arange(int(len(a)/24000*g.SR))/g.SR, np.arange(len(a))/24000, a); M.add(x*2.2, t0)
        M.save(path)
    stills = []
    for p in plan: stills += [p["t0"] + 1.2, p["tcount"] + 1.5, p["trev"] + 1.0, p["tgo"] + 1.8] + ([p["tcmp"] + 1.5] if p["tcmp"] else [])
    stills = stills[:9]
    return frame, audio, DUR, stills, {"scenes": len(plan)}
