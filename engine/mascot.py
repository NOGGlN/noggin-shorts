"""Noggin: the channel mascot - a cheeky pink brain. Original design, drawn procedurally."""
import math, random
from PIL import Image, ImageDraw, ImageFilter

PINK = (255, 133, 175); PINK_D = (226, 86, 140); OUTL = (60, 20, 50); SKIN_SH = (240, 110, 158)
LUMPS = [(-118, -30, 92), (-62, -108, 92), (20, -126, 92), (100, -96, 90), (138, -14, 86), (0, -10, 140),
         (-96, 70, 88), (96, 70, 88), (0, 96, 104)]
_cache = {}

def _draw(pose, look, blink):
    S = 2; Wc, Hc = 640, 700; cx, cy = 320, 330
    im = Image.new("RGBA", (Wc*S//2*2, Hc*S//2*2), (0, 0, 0, 0)); im = Image.new("RGBA", (Wc*S, Hc*S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    def P(x, y): return ((cx + x)*S, (cy + y)*S)
    def circ(x, y, r, **kw):
        (a, b) = P(x, y); d.ellipse((a - r*S, b - r*S, a + r*S, b + r*S), **kw)
    def line(pts, w, fill):
        d.line([P(*p) for p in pts], fill=fill, width=w*S, joint="curve")
        for p in (pts[0], pts[-1]): circ(*p, w/2, fill=fill)
    # legs / feet
    for sx in (-1, 1):
        line([(sx*48, 160), (sx*54, 214)], 22, OUTL)
        a, b = P(sx*62, 226); d.ellipse((a - 46*S, b - 24*S, a + 46*S, b + 24*S), fill=OUTL)
    # lower arms (behind body)
    if pose in ("idle", "throw"):
        line([(-140, 50), (-196, 128)], 22, OUTL); circ(-198, 132, 26, fill=PINK, outline=OUTL, width=6*S)
    if pose == "idle":
        line([(140, 50), (196, 128)], 22, OUTL); circ(198, 132, 26, fill=PINK, outline=OUTL, width=6*S)
    # body: outline pass then fill pass
    for x, y, r in LUMPS: circ(x, y, r + 9, fill=OUTL)
    for x, y, r in LUMPS: circ(x, y, r, fill=PINK)
    def raised(sx, hx, hy):
        line([(sx*150, 30), (hx, hy)], 22, OUTL); circ(hx, hy, 27, fill=PINK, outline=OUTL, width=6*S)
    if pose == "throw": raised(1, 236, -150)
    if pose in ("laugh", "wave"): raised(-1, -250, -110); raised(1, 250, -110)
    if pose == "shock": raised(-1, -235, -40); raised(1, 235, -40)
    # brain folds
    for (x, y, r, a0, a1) in [(-70, -100, 46, 200, 330), (40, -118, 44, 190, 320), (120, -40, 40, 250, 20),
                              (-130, -10, 40, 120, 250), (0, -150, 30, 60, 160)]:
        a, b = P(x, y); d.arc((a - r*S, b - r*S, a + r*S, b + r*S), a0, a1, fill=PINK_D, width=9*S)
    line([(0, -205), (0, -150)], 8, PINK_D)
    # cheeks
    for sx in (-1, 1): circ(sx*110, 70, 26, fill=(255, 160, 190))
    # eyebrows (smug)
    ey = 0
    if pose == "shock":
        line([(-100, -64), (-36, -74)], 13, OUTL); line([(36, -74), (100, -64)], 13, OUTL)
    else:
        line([(-104, -60), (-30, -42)], 13, OUTL); line([(30, -50), (104, -66)], 13, OUTL)
    # eyes
    for sx in (-1, 1):
        ex, eyy = sx*62, 0
        if pose == "laugh":
            line([(ex - 34, eyy + 10), (ex, eyy - 18), (ex + 34, eyy + 10)], 12, OUTL)
        elif blink:
            line([(ex - 36, eyy), (ex + 36, eyy)], 12, OUTL)
        else:
            r = 52 if pose == "shock" else 46
            circ(ex, eyy, r, fill="white", outline=OUTL, width=7*S)
            pr = 15 if pose == "shock" else 21
            circ(ex + look[0]*18, eyy + look[1]*18, pr, fill=OUTL)
            circ(ex + look[0]*18 - 6, eyy + look[1]*18 - 7, 6, fill="white")
    # mouth
    if pose == "laugh":
        a, b = P(0, 92); d.chord((a - 80*S, b - 52*S, a + 80*S, b + 64*S), 0, 180, fill=OUTL)
        d.rectangle((a - 62*S, b, a + 62*S, b + 14*S), fill="white")
        a2, b2 = P(0, 140); d.ellipse((a2 - 34*S, b2 - 18*S, a2 + 34*S, b2 + 14*S), fill=(255, 90, 110))
    elif pose == "shock":
        circ(0, 100, 30, fill=OUTL); circ(0, 108, 16, fill=(255, 90, 110))
    else:  # smug lopsided grin
        a, b = P(4, 78)
        d.chord((a - 76*S, b - 40*S, a + 76*S, b + 48*S), 10, 170, fill=OUTL)
        d.polygon([P(-58, 84), P(62, 84), P(56, 94), P(-52, 94)], fill="white")
    if pose == "throw":  # tomato in raised hand, drawn over arm
        t = tomato(84)
        im.alpha_composite(t.resize((t.width*S, t.height*S)), (int((cx + 246)*S - t.width*S/2), int((cy - 190)*S - t.height*S/2)))
        circ(236, -150, 22, fill=PINK, outline=OUTL, width=6*S)
    im = im.resize((Wc//2, Hc//2), Image.LANCZOS)  # final ~320x350
    return im  # fixed 320x350 canvas; feet bottom at y~290

def mascot(pose="idle", look=(0, -1), blink=False):
    k = (pose, look, blink)
    if k not in _cache: _cache[k] = _draw(pose, look, blink)
    return _cache[k]

def tomato(size):
    S = 4; r = size*S/2
    im = Image.new("RGBA", (int(size*S*1.1), int(size*S*1.1)), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    c = im.width/2
    d.ellipse((c - r, c - r*0.9, c + r, c + r*0.95), fill=(225, 40, 40), outline=(120, 10, 20), width=int(3*S))
    d.ellipse((c - r*0.55, c - r*0.6, c - r*0.15, c - r*0.25), fill=(255, 140, 130))
    for k in range(5):
        a = -math.pi/2 + k*2*math.pi/5
        d.line((c, c - r*0.8, c + math.cos(a)*r*0.45, c - r*0.8 + math.sin(a)*r*0.3), fill=(40, 150, 50), width=int(4*S))
    d.ellipse((c - 5*S, c - r*0.8 - 5*S, c + 5*S, c - r*0.8 + 5*S), fill=(30, 120, 40))
    return im.resize((im.width//S, im.height//S), Image.LANCZOS)

def splat(seed, size=360):
    r = random.Random(seed); S = 2; N = size*S
    m = Image.new("L", (N, int(N*1.5)), 0); d = ImageDraw.Draw(m); c = N/2
    d.ellipse((c - N*0.26, c - N*0.24, c + N*0.26, c + N*0.24), fill=255)
    for _ in range(14):
        a = r.uniform(0, 2*math.pi); dist = r.uniform(0.2, 0.42)*N; rr = r.uniform(0.04, 0.1)*N
        x, y = c + math.cos(a)*dist, c + math.sin(a)*dist
        d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=255)
        d.line((c, c, x, y), fill=255, width=int(rr*1.1))
    drips = []
    for _ in range(4):  # drips (extended later by animation)
        x = c + r.uniform(-0.2, 0.2)*N; w = r.uniform(0.03, 0.06)*N
        drips.append((x/S, w/S))
    m = m.filter(ImageFilter.GaussianBlur(3)).point(lambda v: 255 if v > 128 else 0)
    col = Image.new("RGBA", m.size, (214, 32, 38, 255))
    inner = m.filter(ImageFilter.MinFilter(9))
    hi = Image.new("RGBA", m.size, (240, 70, 60, 255))
    col.paste(hi, (0, 0), inner)
    col.putalpha(m)
    sd = ImageDraw.Draw(col)
    for _ in range(9):
        x, y = c + r.uniform(-0.18, 0.18)*N, c + r.uniform(-0.15, 0.15)*N
        sd.ellipse((x - 9, y - 6, x + 9, y + 6), fill=(255, 220, 120))
    col = col.resize((N//S, int(N*1.5)//S), Image.LANCZOS)
    return col, drips

def bubble(text, font_fn, tail="down"):
    f = font_fn(46); dd = ImageDraw.Draw(Image.new("L", (1, 1)))
    b = dd.textbbox((0, 0), text, font=f); tw, th = b[2]-b[0], b[3]-b[1]
    pw, ph = tw + 64, th + 48
    if tail in ("sideL", "sideR"):
        im = Image.new("RGBA", (pw + 50, ph + 6), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        ox = 44 if tail == "sideL" else 0; my = ph/2
        if tail == "sideL": d.polygon([(0, my + 10), (ox + 8, my - 18), (ox + 8, my + 18)], fill=OUTL)
        else: d.polygon([(pw + 50, my + 10), (pw - 8, my - 18), (pw - 8, my + 18)], fill=OUTL)
        d.rounded_rectangle((ox, 0, ox + pw, ph), 32, fill="white", outline=OUTL, width=6)
        if tail == "sideL": d.polygon([(9, my + 7), (ox + 12, my - 11), (ox + 12, my + 11)], fill="white")
        else: d.polygon([(pw + 41, my + 7), (pw - 12, my - 11), (pw - 12, my + 11)], fill="white")
        d.text((ox + pw/2, ph/2 + 2), text, font=f, fill=OUTL, anchor="mm")
        return im
    im = Image.new("RGBA", (pw + 12, ph + 44), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    tx = pw*0.3 if tail == "left" else pw*0.7 if tail == "right" else pw/2
    d.polygon([(tx - 22, ph - 4), (tx + 22, ph - 4), (tx - 6 if tail != "right" else tx + 6, ph + 40)], fill=OUTL)
    d.rounded_rectangle((0, 0, pw, ph), 32, fill="white", outline=OUTL, width=6)
    d.polygon([(tx - 14, ph - 8), (tx + 14, ph - 8), (tx - 4 if tail != "right" else tx + 4, ph + 28)], fill="white")
    d.text((pw/2, ph/2 + 2), text, font=f, fill=OUTL, anchor="mm")
    return im

def logo(path, font_fn, size=1000):
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for i in range(size//2, 0, -2):  # radial purple gradient
        t = i/(size/2); c = (int(140 + 70*(1-t)), int(40 + 40*(1-t)), int(200 + 40*(1-t)))
        d.ellipse((size/2 - i, size/2 - i, size/2 + i, size/2 + i), fill=c)
    d.ellipse((10, 10, size - 10, size - 10), outline="white", width=22)
    m = mascot("idle", (0.4, -0.3)); s = size*0.66/m.height; m = m.resize((int(m.width*s), int(m.height*s)), Image.LANCZOS)
    im.alpha_composite(m, (int(size/2 - m.width/2), int(size*0.12)))
    f = font_fn(int(size*0.13))
    d.text((size/2, size*0.86), "NOGGIN", font=f, fill="white", anchor="mm", stroke_width=int(size*0.014), stroke_fill=OUTL)
    im.save(path)
