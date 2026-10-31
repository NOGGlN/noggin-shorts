"""Road Rules quiz ("Who has to wait?"): a top-down illustrated junction, two cars ("You" and "Car") with dotted routes,
a white question card, a calm British voice reading it, a countdown, then the answer with the reason.
Short (9:16): 1 scene, card on top.  Video (16:9): several scenes, card on the left.

spec["scenes"] = [{"type": "crossroads_right" | "roundabout_enter" | "roundabout_2lane_exit" | "left_turn",
                   "place": "Crossroads in Portugal", "lines": ["No signs. No lights.", "You go straight."],
                   "question": "Who has to wait - you or the car?", "answer": "you" | "car",
                   "answer_line": "YOU wait.", "why": "No signs? Traffic from your right goes first."}]
Rules must be real (Portugal by default). The scene type decides the geometry; "answer" decides who stops and who goes first.
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import gcommon as g

PAVE, TILE, ASPH, CURB = (232, 227, 215), (219, 213, 199), (58, 61, 68), (205, 200, 190)
GRASS, GRASS2, LANE = (150, 194, 108), (136, 182, 96), (240, 240, 236)
YOU_C, CAR_C = (233, 86, 58), (246, 246, 244)
RED, GREEN, INKC = (229, 80, 52), (46, 160, 90), (20, 20, 24)
S = 2   # supersampling for the static background

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

def card(sc, w, reveal=0.0, count=None):
    """The question card (white, rounded). reveal 0..1 swaps the comments line for the answer."""
    pad = 44; maxw = w - 2*pad; lab = g.font(g.XB, 40); big = g.font(g.BLACK, 76 if w > 900 else 54); small = g.font(g.XB, 46 if w > 900 else 36)
    rows = [(l, lab, RED) for l in wrap(sc["place"], lab, maxw)]
    for l in sc["lines"]: rows += [(x, big, INKC) for x in wrap(l, big, maxw)]
    rows += [(x, big, RED) for x in wrap(sc["question"], big, maxw)]
    if reveal < 0.5: tail = [(x, small, INKC) for x in wrap("Answer in the comments", small, maxw - 70)]
    else: tail = [(x, big, GREEN) for x in wrap("Answer: " + sc["answer_line"], big, maxw)] + [(x, small, INKC) for x in wrap(sc["why"], small, maxw)]
    rows += [("", None, None)] + tail
    hts = [(f.getbbox("Hg")[3] + 14 if f else 18) for _, f, _ in rows]; ht = sum(hts) + 2*pad
    im = Image.new("RGBA", (w + 40, ht + 40), (0, 0, 0, 0)); sh = Image.new("L", im.size, 0)
    ImageDraw.Draw(sh).rounded_rectangle((20, 26, w + 20, ht + 26), 36, fill=90); sh = sh.filter(ImageFilter.GaussianBlur(14))
    im.putalpha(sh); im = Image.composite(Image.new("RGBA", im.size, (0, 0, 0, 255)), Image.new("RGBA", im.size, (0, 0, 0, 0)), sh)
    d = ImageDraw.Draw(im); d.rounded_rectangle((20, 20, w + 20, ht + 20), 36, fill=(250, 250, 248, 245))
    y = 20 + pad
    for (txt, f, col), hh in zip(rows, hts):
        if f: d.text((20 + pad, y), txt, font=f, fill=col)
        y += hh
    if reveal < 0.5:
        e = g.emoji("👇", 56); last = tail[-1][0]; im.alpha_composite(e, (int(20 + pad + small.getlength(last) + 14), int(y - hts[-1] - 8)))
    if count is not None and reveal < 0.5:                       # countdown badge in the card's corner
        cxr, cyr, r = w + 20 - 70, 20 + 70, 46
        d.ellipse((cxr - r, cyr - r, cxr + r, cyr + r), fill=RED); d.text((cxr, cyr), str(count), font=g.font(g.BLACK, 56), fill=(255, 255, 255), anchor="mm")
    return im

def badge(txt, col):
    f = g.font(g.BLACK, 44); w = int(f.getlength(txt)) + 50
    im = Image.new("RGBA", (w, 74), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, 73), 37, fill=col + (255,)); d.text((w/2, 38), txt, font=f, fill=(255, 255, 255), anchor="mm"); return im

# ------------------------------------------------------------------ build
def build(spec, fmt):
    import tts
    W, H = g.W, g.H; vert = fmt == "short"; scenes = spec["scenes"]
    if vert: scenes = scenes[:1]
    cw = W - 60 if vert else 820; cardpos = (30 - 20, 110 - 20) if vert else (40 - 20, 60 - 20)
    plan, t = [], 0.0; voice = []; sprites = {}
    for i, sc in enumerate(scenes):
        rb = sc["type"].startswith("roundabout")                     # world units are zoomed by Z on screen
        Z = (1.0 if vert else 0.8) if rb else (1.45 if vert else 1.2); WW, HW = W/Z, H/Z
        cx, cy = (WW/2, HW*(0.64 if rb else 0.66)) if vert else (WW*0.71, HW/2)
        draw, you, car, ys, cs = scene_geometry(sc["type"], cx, cy, WW, HW)
        bg = Image.new("RGB", (W*S, H*S), PAVE); d = ImageDraw.Draw(bg); k = S*Z
        for x in np.arange(0, WW, 96): d.line((x*k, 0, x*k, H*S), fill=TILE, width=2*S)
        for y in np.arange(0, HW, 96): d.line((0, y*k, W*S, y*k), fill=TILE, width=2*S)
        draw(d, k); bg = bg.resize((W, H), Image.LANCZOS).convert("RGBA")
        q = sc["place"] + ". " + " ".join(sc["lines"]) + " " + sc["question"].replace(" - ", ", ")
        a1, sr, _ = tts.say_gb(q); a2, _, _ = tts.say_gb("The answer: " + sc["answer_line"] + " " + sc["why"])
        t0 = t; tq = t0 + 0.7; tcount = tq + len(a1)/sr + 0.4; trev = tcount + 4.0; tgo = trev + 0.8
        tend = trev + max(len(a2)/sr + 0.6, 4.6) + (1.6 if i == len(scenes) - 1 else 0.6)
        voice += [(tq, a1), (trev + 0.15, a2)]
        first = car if sc["answer"] == "you" else you            # who goes first
        cardh = card(sc, cw, 1.0).height + cardpos[1] if vert else 0
        if Z not in sprites:
            sprites[Z] = [sp.resize((int(sp.width*Z*0.95), int(sp.height*Z*0.95)), Image.LANCZOS) for sp in (car_sprite(YOU_C, "You"), car_sprite(CAR_C, "Car"))]
        plan.append(dict(Z=Z, cardh=cardh, sc=sc, bg=bg, you=you, car=car, ys=ys, cs=cs, first=first, t0=t0, tq=tq, tcount=tcount, trev=trev, tgo=tgo, t1=tend))
        t = tend
    DUR = t
    cardbottom = {}
    cards = {}
    def frame(tt):
        p = next((p for p in plan if tt < p["t1"]), plan[-1]); lt = tt - p["t0"]; sc = p["sc"]
        im = p["bg"].copy(); Z = p["Z"]; spr_you, spr_car = sprites[Z]
        def at(path, s_):
            x, y, a = path.at(s_); return x*Z, y*Z, a
        def pos(path, stop, is_first):
            arrive = min(1, (tt - p["t0"])/max(0.1, p["tq"] + 2.6 - p["t0"]))
            s = stop*(1 - (1 - arrive)**2.2)                                  # drive in and slow to the stop point
            if tt > p["tgo"]:
                go = tt - p["tgo"] - (0 if is_first else 1.5)
                if go > 0: s = stop + (260*go + 120*go*go)/Z
            return s

        sy, sc_ = pos(p["you"], p["ys"], p["first"] is p["you"]), pos(p["car"], p["cs"], p["first"] is p["car"])
        da = g.ease((lt - 0.8)/0.6)*(1 - g.ease((tt - p["tgo"])/0.5))
        if da > 0.01:
            dotted(im, p["you"], sy, min(p["you"].L, sy + 700), YOU_C, da, Z); dotted(im, p["car"], sc_, min(p["car"].L, sc_ + 700), CAR_C, da, Z)
        for path, s, spr, lab, dk in ((p["you"], sy, spr_you, "You", False), (p["car"], sc_, spr_car, "Car", True)):
            if s < path.L - 5: x, y, ang = at(path, s); place_car(im, spr, x, y, ang, lab, dk, Z)
        if p["trev"] <= tt < p["tgo"] + 1.4:                                 # WAIT / GO badges
            k = g.back((tt - p["trev"])/0.3)
            for path, s, who in ((p["you"], sy, "you"), (p["car"], sc_, "car")):
                x, y, _ = at(path, s); waits = who == sc["answer"]; off = 135*Z/1.9 + 60
                by = y - off if (y - off) > p["cardh"] + 40 else y + off
                bdg = badge("WAITS" if waits else "GOES FIRST", RED if waits else GREEN)
                g.paste(im, bdg, min(max(x, bdg.width/2 + 20), W - bdg.width/2 - 20), by, k)
        rev = 1.0 if tt >= p["trev"] else 0.0
        cnt = None if not (p["tcount"] <= tt < p["trev"]) else 4 - int(tt - p["tcount"])
        key = (id(p), rev, cnt)
        if key not in cards: cards[key] = card(sc, cw, rev, cnt)
        c = cards[key]; slide = g.ease((lt - 0.15)/0.45); cardbottom[id(p)] = cardpos[1] + c.height if vert else 0
        im.alpha_composite(c, (int(cardpos[0]), int(cardpos[1] - (1 - slide)*(c.height + 140)))) if slide > 0 else None
        if tt > DUR - 1.6:
            a = g.ease((tt - (DUR - 1.6))/0.4); im.alpha_composite(Image.new("RGBA", (W, H), (20, 20, 24, int(200*a))))
            g.paste(im, g.T("FOLLOW FOR A NEW ROAD RULE", 64 if vert else 80, g.WHITE, 8, maxw=W - 80), W/2, H/2 - 50, a)
            g.paste(im, g.T("DID YOU GET IT RIGHT?", 52 if vert else 64, g.YEL, 7, maxw=W - 80), W/2, H/2 + 50, a)
        return im
    def audio(path):
        M = g.Mix(DUR, bed=0.05)
        for p in plan:
            M.add(M.whoosh(0.5), p["t0"] + 0.15, 0.5)
            for k in range(4): M.add(M.tick(1500 if k < 3 else 1900), p["tcount"] + k, 0.8)
            M.add(M.ding(1318.5), p["trev"], 0.8)
        for t0, a in voice:                                                   # voice at 24 kHz -> 44.1 kHz
            x = np.interp(np.arange(int(len(a)/24000*g.SR))/g.SR, np.arange(len(a))/24000, a); M.add(x*2.2, t0)
        M.save(path)
    stills = []
    for p in plan: stills += [p["t0"] + 1.2, p["tcount"] + 1.5, p["trev"] + 1.0, p["tgo"] + 1.6]
    stills = stills[:9] + ([DUR - 0.6] if len(stills) < 9 else [])
    return frame, audio, DUR, stills, {"scenes": len(plan)}
