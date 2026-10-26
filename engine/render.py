import math, random, subprocess, sys, os, csv, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy import ndimage
from puzzles import HOLES, SILHOUETTES, ODD

W, H, FPS, DUR = 1080, 1920, 30, 10.0
NF = int(FPS * DUR)
REVEAL = 6.0
FONT = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
DARK = (29, 29, 59)
OUT = "/tmp/noggin_out"
os.makedirs(OUT, exist_ok=True)

PALETTES = [("#ff5f6d", "#ffc371"), ("#7f00ff", "#e100ff"), ("#00c6ff", "#0072ff"),
            ("#f7971e", "#e84a5f"), ("#11998e", "#38ef7d"), ("#fc466b", "#3f5efb"),
            ("#ff0099", "#6a3093"), ("#00b09b", "#96c93d"), ("#8e2de2", "#4a00e0"),
            ("#f12711", "#f5af19"), ("#1fa2ff", "#12d8fa"), ("#ee0979", "#ff6a00")]
BADGE = [(231, 76, 60), (52, 152, 219), (243, 156, 18), (39, 174, 96)]

_fc = {}
def font(sz):
    if sz not in _fc: _fc[sz] = ImageFont.truetype(FONT, sz)
    return _fc[sz]

def hexrgb(h): return tuple(int(h[i:i+2], 16) for i in (1, 3, 5))

def fit(text, maxw, maxh, start, stroke=0):
    sz = start
    d = ImageDraw.Draw(Image.new("L", (1, 1)))
    while sz > 16:
        b = d.multiline_textbbox((0, 0), text, font=font(sz), stroke_width=stroke, align="center", spacing=sz*0.05)
        if b[2]-b[0] <= maxw and b[3]-b[1] <= maxh: return sz
        sz -= 2
    return sz

def text_layer(text, maxw, maxh, start, fill=(255, 255, 255), stroke=0, stroke_fill=DARK):
    sz = fit(text, maxw, maxh, start, stroke)
    d = ImageDraw.Draw(Image.new("L", (1, 1)))
    b = d.multiline_textbbox((0, 0), text, font=font(sz), stroke_width=stroke, align="center", spacing=sz*0.05)
    im = Image.new("RGBA", (int(b[2]-b[0]+4), int(b[3]-b[1]+4)), (0, 0, 0, 0))
    ImageDraw.Draw(im).multiline_text((2-b[0], 2-b[1]), text, font=font(sz), fill=fill, stroke_width=stroke,
                                      stroke_fill=stroke_fill, align="center", spacing=sz*0.05)
    return im

def emoji_img(e, box):
    f = ImageFont.truetype(EMOJI, 109)
    im = Image.new("RGBA", (240, 240), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((120, 120), e, font=f, embedded_color=True, anchor="mm")
    im = im.crop(im.getbbox())
    s = min(box / im.width, box / im.height)
    im = im.resize((round(im.width*s), round(im.height*s)), Image.LANCZOS)
    return im.filter(ImageFilter.UnsharpMask(2, 60, 2))

def paste_center(dst, src, cx, cy):
    dst.alpha_composite(src, (int(cx - src.width/2), int(cy - src.height/2)))

def rounded(size, r, fill):
    im = Image.new("RGBA", size, (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, size[0]-1, size[1]-1), r, fill=fill)
    return im

def with_alpha(im, a):
    if a >= 1: return im
    im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v*a)))
    return im

# ---------------- hole-puzzle art ----------------
CW, CH = 820, 560
def hole_art(kind, p):
    im = Image.new("RGBA", (CW, CH), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    T = (0, 0, 0, 0); cx, cy = CW//2, CH//2
    if kind == "text":
        sz = fit(p, 760, 500, 400)
        d.multiline_text((cx, cy), p, font=font(sz), fill=DARK, anchor="mm", align="center", spacing=sz*0.02)
    elif kind == "button":
        d.ellipse((cx-240, cy-240, cx+240, cy+240), fill=(230, 57, 70))
        d.ellipse((cx-195, cy-195, cx+195, cy+195), outline=(180, 30, 45), width=12)
        pts = [(-62, -62), (62, -62), (-62, 62), (62, 62)] if p == 4 else [(-62, 0), (62, 0)]
        for x, y in pts: d.ellipse((cx+x-36, cy+y-36, cx+x+36, cy+y+36), fill=T)
    elif kind == "donut":
        d.ellipse((cx-250, cy-250, cx+250, cy+250), fill=(214, 156, 92))
        d.ellipse((cx-225, cy-225, cx+225, cy+225), fill=(255, 111, 168))
        d.ellipse((cx-110, cy-110, cx+110, cy+110), fill=(214, 156, 92))
        rnd = random.Random(3)
        cols = [(255, 255, 255), (255, 210, 63), (46, 204, 113), (52, 152, 219), (155, 89, 182)]
        for _ in range(45):
            a = rnd.uniform(0, 2*math.pi); r = rnd.uniform(130, 200); ang = rnd.uniform(0, math.pi)
            x, y = cx + r*math.cos(a), cy + r*math.sin(a)
            d.line((x-14*math.cos(ang), y-14*math.sin(ang), x+14*math.cos(ang), y+14*math.sin(ang)), fill=rnd.choice(cols), width=9)
        d.ellipse((cx-85, cy-85, cx+85, cy+85), fill=T)
    elif kind == "cheese":
        d.polygon([(60, 500), (770, 500), (770, 180), (60, 420)], fill=(255, 205, 60))
        d.line([(60, 420), (770, 180)], fill=(240, 175, 30), width=10)
        for x, y, r in [(250, 440, 28), (420, 385, 38), (600, 430, 30), (650, 300, 40), (480, 460, 22)]:
            d.ellipse((x-r, y-r, x+r, y+r), fill=T)
        for x, y, r in [(300, 505, 42), (775, 340, 38), (110, 410, 30)]:  # edge bites (not holes!)
            d.ellipse((x-r, y-r, x+r, y+r), fill=T)
    elif kind == "glasses":
        col = (44, 62, 80)
        for x in (cx-165, cx+165):
            d.ellipse((x-140, cy-120, x+140, cy+120), fill=col)
            d.ellipse((x-108, cy-90, x+108, cy+90), fill=T)
        d.line((cx-30, cy-40, cx+30, cy-40), fill=col, width=22)
        d.line((cx-300, cy-60, cx-390, cy-130), fill=col, width=20)
        d.line((cx+300, cy-60, cx+390, cy-130), fill=col, width=20)
    elif kind == "pegboard":
        c, r = p
        d.rounded_rectangle((70, 50, 750, 510), 40, fill=(198, 139, 89))
        for i in range(c):
            for j in range(r):
                x = 70 + 680*(i+0.5)/c; y = 50 + 460*(j+0.5)/r
                d.ellipse((x-38, y-38, x+38, y+38), fill=T)
    # find enclosed holes
    ink = np.array(im.getchannel("A")) > 110
    lab, n = ndimage.label(~ink)
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])))
    holes = [k for k in range(1, n+1) if k not in border and (lab == k).sum() > 60]
    reveal = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    hm = np.isin(lab, holes)
    hm = ndimage.binary_dilation(hm, iterations=3)
    col = np.zeros((CH, CW, 4), np.uint8); col[hm] = (255, 210, 0, 255)
    reveal = Image.fromarray(col, "RGBA"); reveal.alpha_composite(im)
    rd = ImageDraw.Draw(reveal)
    # number the holes (left-to-right, top-to-bottom)
    cents = sorted([ndimage.center_of_mass(lab == k) for k in holes], key=lambda c: (round(c[0]/120), c[1]))
    for i, (y, x) in enumerate(cents):
        rd.text((x, y), str(i+1), font=font(40), fill=(255, 255, 255), stroke_width=5, stroke_fill=(200, 30, 60), anchor="mm")
    return im, reveal, len(holes)

# ---------------- cards ----------------
CARD = (900, 660)
def blank_card():
    return rounded(CARD, 56, (255, 255, 255, 255))

def build(kind, idx, item):
    rnd = random.Random(idx * 7 + 1)
    q, a = blank_card(), blank_card()
    if kind == "holes":
        art, rev, n = hole_art(*item)
        paste_center(q, art, 450, 330); paste_center(a, rev, 450, 330)
        pool = [v for v in range(max(0, n-2), n+4) if v != n]
        opts = rnd.sample(pool, 3) + [n]; rnd.shuffle(opts)
        options = [str(o) for o in opts]; correct = opts.index(n)
        banner = f"ANSWER: {n} HOLE{'S' if n != 1 else ''}!"
        question, cat = "HOW MANY HOLES?", "COUNT THE HOLES"
        meta = (item[1] if item[0] == "text" else item[0]).replace("\n", " ") if True else ""
        title_obj = f"{meta}" if item[0] == "text" else {"button": "a button", "donut": "a donut", "cheese": "cheese",
                                                          "glasses": "glasses", "pegboard": "a pegboard"}[item[0]]
        answer = str(n)
    elif kind == "sil":
        e, ans, dis = item
        em = emoji_img(e, 520)
        sil = Image.new("RGBA", em.size, DARK + (255,)); sil.putalpha(em.getchannel("A"))
        paste_center(q, sil, 450, 330); paste_center(a, em, 450, 330)
        opts = dis + [ans]; rnd.shuffle(opts); options = opts; correct = opts.index(ans)
        art_ = "" if ans in ("Scissors",) else ("AN " if ans[0] in "AEIOU" else "A ")
        banner = f"IT'S {art_}{ans.upper()}!"
        question, cat, title_obj, answer = "WHAT IS THIS?", "GUESS THE SHADOW", "", ans
    else:
        items, odd, reason = item
        pos = [(235, 185), (665, 185), (235, 480), (665, 480)]
        for i, ((e, nm), (x, y)) in enumerate(zip(items, pos)):
            em = emoji_img(e, 220)
            for card, hl in ((q, False), (a, True)):
                if hl and i == odd:
                    hb = rounded((300, 280), 40, (46, 204, 113, 255)); paste_center(card, hb, x, y)
                paste_center(card, em if (not hl or i == odd) else with_alpha(em, 0.25), x, y)
                bd = ImageDraw.Draw(card); bx, by = x-130, y-115
                bd.ellipse((bx-28, by-28, bx+28, by+28), fill=BADGE[i])
                bd.text((bx, by+2), "ABCD"[i], font=font(36), fill="white", anchor="mm")
        options = [nm for _, nm in items]; correct = odd
        banner = reason.upper()
        question, cat, title_obj, answer = "WHICH ONE DOESN'T BELONG?", "ODD ONE OUT", "", items[odd][1]
    return dict(q=q, a=a, options=options, correct=correct, banner=banner, question=question, cat=cat,
                title_obj=title_obj, answer=answer)

# ---------------- option tiles ----------------
TW, TH = 440, 170
def tile(i, text, state):
    fill = (46, 204, 113, 255) if state == "right" else (255, 255, 255, 255)
    im = Image.new("RGBA", (TW, TH+12), (0, 0, 0, 0))
    im.alpha_composite(rounded((TW, TH), 44, (0, 0, 0, 70)), (0, 12))
    im.alpha_composite(rounded((TW, TH), 44, fill), (0, 0))
    d = ImageDraw.Draw(im)
    bc = (255, 255, 255) if state == "right" else BADGE[i]
    d.ellipse((24, TH/2-44, 112, TH/2+44), fill=bc)
    if state == "right":
        d.line([(46, TH/2+2), (63, TH/2+20), (92, TH/2-18)], fill=(46, 204, 113), width=12, joint="curve")
    else:
        d.text((68, TH/2+3), "ABCD"[i], font=font(50), fill="white", anchor="mm")
    sz = fit(text, TW-160, TH-40, 58)
    d.text((128 + (TW-150)/2, TH/2+3), text, font=font(sz), fill="white" if state == "right" else DARK, anchor="mm")
    return with_alpha(im, 0.4) if state == "dim" else im

# ---------------- background ----------------
def gradient(c1, c2):
    a, b = np.array(hexrgb(c1), float), np.array(hexrgb(c2), float)
    t = np.linspace(0, 1, H)[:, None, None]
    g = (a*(1-t) + b*t) * np.ones((1, W, 1))
    return Image.fromarray(g.astype(np.uint8), "RGB")

RAYS = Image.new("L", (1200, 1200), 0)
_d = ImageDraw.Draw(RAYS)
for k in range(16):
    a0 = k*2*math.pi/16; a1 = a0 + math.pi/16
    _d.polygon([(600, 600), (600+1000*math.cos(a0), 600+1000*math.sin(a0)), (600+1000*math.cos(a1), 600+1000*math.sin(a1))], fill=34)
RAYS = RAYS.filter(ImageFilter.GaussianBlur(2))

def ease_back(x):
    x = min(max(x, 0), 1); c1 = 1.70158; c3 = c1+1
    return 1 + c3*(x-1)**3 + c1*(x-1)**2

def ease_out(x):
    x = min(max(x, 0), 1); return 1-(1-x)**3

# ---------------- render one video ----------------
def render(job):
    n, kind, item = job
    P = build(kind, n, item)
    c1, c2 = PALETTES[n % len(PALETTES)]
    bg = gradient(c1, c2); white = Image.new("RGB", (W, H), (255, 255, 255))
    accent = hexrgb(c2)

    pill = text_layer(f"#{n:02d}  ·  {P['cat']}", 800, 60, 40)
    pill_bg = rounded((pill.width+60, pill.height+30), 40, (0, 0, 0, 70)); pill_bg.alpha_composite(pill, (30, 15))
    qtxt = text_layer(P["question"], 960, 220, 92, stroke=7)
    shadow = rounded((CARD[0], CARD[1]), 56, (0, 0, 0, 90)).filter(ImageFilter.GaussianBlur(14))
    def card_layer(c):
        L = Image.new("RGBA", (CARD[0]+60, CARD[1]+60), (0, 0, 0, 0))
        L.alpha_composite(shadow, (30, 44)); L.alpha_composite(c, (30, 30)); return L
    cq, ca = card_layer(P["q"]), card_layer(P["a"])
    tiles = [[tile(i, t, s) for s in ("normal", "right", "dim")] for i, t in enumerate(P["options"])]
    banner_t = text_layer(P["banner"], 860, 90, 64, fill=DARK)
    banner = rounded((banner_t.width+80, banner_t.height+50), 60, (255, 210, 0, 255))
    banner.alpha_composite(banner_t, (40, 25))
    foot_q = text_layer("Comment your answer before time runs out!", 980, 60, 44, stroke=4)
    foot_a = text_layer("Did you get it? Follow for more puzzles!", 980, 60, 44, stroke=4)

    CX, CY = 540, 830  # card center
    TPOS = [(85, 1230), (555, 1230), (85, 1430), (555, 1430)]

    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-", "-i", "/tmp/noggin_sfx.wav", "-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
           "-pix_fmt", "yuv420p", "-threads", "2", "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart",
           f"{OUT}/puzzle_{n:02d}.mp4"]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in range(NF):
        t = f / FPS
        rot = RAYS.rotate(t*4, resample=Image.BILINEAR).crop((330, 120, 870, 1080)).resize((W, H), Image.BILINEAR)
        frame = Image.composite(white, bg, rot).convert("RGBA")
        # top pill + question
        paste_center(frame, pill_bg, 540, 130)
        qa = ease_out(t/0.35)
        paste_center(frame, with_alpha(qtxt, qa), 540, 300 - 60*(1-qa))
        # card (pop in, crossfade at reveal)
        s = 0.6 + 0.4*ease_back(t/0.45)
        if t < REVEAL: L = cq
        else:
            k = min((t-REVEAL)/0.3, 1); L = Image.blend(cq, ca, k) if k < 1 else ca
            s *= 1 + 0.06*math.sin(min((t-REVEAL)/0.35, 1)*math.pi)
        if abs(s-1) > 1e-3: L = L.resize((max(1, round(L.width*s)), max(1, round(L.height*s))), Image.BILINEAR)
        paste_center(frame, with_alpha(L, min(t/0.2, 1)), CX, CY)
        # timer
        if 0.4 <= t < REVEAL:
            num = 5 if t < 1 else max(1, 6 - int(t))
            frac = 1.0 if t < 1 else (REVEAL - t)/5
            T = Image.new("RGBA", (190, 190), (0, 0, 0, 0)); td = ImageDraw.Draw(T)
            td.ellipse((5, 5, 185, 185), fill=(255, 255, 255, 255))
            col = (231, 76, 60) if num <= 2 else accent
            td.arc((14, 14, 176, 176), -90, -90 + 360*frac, fill=col, width=16)
            ph = (t % 1) if t >= 1 else 1
            td.text((95, 99), str(num), font=font(int(84*(1 + 0.3*(1-ease_out(ph/0.2))))), fill=col, anchor="mm")
            T = with_alpha(T, min((t-0.4)/0.2, 1))
            paste_center(frame, T, 920, 515)
        # options
        for i, (x, y) in enumerate(TPOS):
            st = 0.35 + 0.1*i; k = ease_out((t-st)/0.3)
            if k <= 0: continue
            if t < REVEAL: im = tiles[i][0]
            else: im = tiles[i][1] if i == P["correct"] else tiles[i][2]
            if t >= REVEAL and i == P["correct"]:
                sc = 1 + 0.08*math.sin(min((t-REVEAL)/0.3, 1)*math.pi)
                im = im.resize((round(im.width*sc), round(im.height*sc)), Image.BILINEAR)
            frame.alpha_composite(with_alpha(im, k), (int(x + TW/2 - im.width/2), int(y + 70*(1-k) + (TH - im.height)/2)))
        # banner + footer
        if t >= REVEAL + 0.15:
            k = ease_back((t-REVEAL-0.15)/0.4); b = banner.resize((max(1, round(banner.width*k)), max(1, round(banner.height*k))), Image.BILINEAR)
            paste_center(frame, b, 540, 1150)
            paste_center(frame, foot_a, 540, 1700)
        else:
            paste_center(frame, with_alpha(foot_q, min(max((t-0.8)/0.3, 0), 1)), 540, 1700)
        # flash on reveal
        rgb = frame.convert("RGB")
        if REVEAL <= t < REVEAL + 0.25:
            rgb = Image.blend(rgb, white, 0.55*(1-(t-REVEAL)/0.25))
        ff.stdin.write(rgb.tobytes())
    ff.stdin.close(); ff.wait()
    return n, kind, P

# ---------------- audio ----------------
def make_sfx():
    sr = 44100; a = np.zeros(int(sr*DUR))
    def add(sig, t):
        i = int(t*sr); a[i:i+len(sig)] += sig[:len(a)-i]
    def env(n, dec): return np.exp(-np.arange(n)/(sr*dec))
    # whoosh/pop at start
    n = int(0.35*sr); tt = np.arange(n)/sr
    add(0.35*np.sin(2*np.pi*(300*tt + 900*tt**2))*env(n, 0.08), 0.02)
    # ticks
    for k, t in enumerate([1, 2, 3, 4, 5]):
        n = int(0.09*sr); tt = np.arange(n)/sr; fr = 1300 if k < 3 else 1700
        noise = np.random.default_rng(k).standard_normal(n)*0.15
        add((0.55*np.sin(2*np.pi*fr*tt) + noise)*env(n, 0.012), t)
        add(0.3*np.sin(2*np.pi*fr*0.75*tt)*env(n, 0.012), t + 0.5)  # "tock"
    # reveal chime (C6 E6 G6 C7)
    for j, fr in enumerate([1046.5, 1318.5, 1568.0, 2093.0]):
        n = int(1.6*sr); tt = np.arange(n)/sr
        add(0.22*(np.sin(2*np.pi*fr*tt) + 0.3*np.sin(2*np.pi*fr*2*tt))*env(n, 0.45), REVEAL + j*0.07)
    a = a / max(1, np.abs(a).max()) * 0.85
    s = (np.stack([a, a], 1)*32767).astype(np.int16)
    with wave.open("/tmp/noggin_sfx.wav", "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes(s.tobytes())

def jobs():
    js = []; h = s = o = 0
    for n in range(1, 51):
        r = (n-1) % 3
        if r == 0 and h < len(HOLES) or (s >= len(SILHOUETTES) and o >= len(ODD)):
            js.append((n, "holes", HOLES[h])); h += 1
        elif r == 1 and s < len(SILHOUETTES) or o >= len(ODD):
            js.append((n, "sil", SILHOUETTES[s])); s += 1
        else:
            js.append((n, "odd", ODD[o])); o += 1
    return js

if __name__ == "__main__":
    make_sfx()
    J = jobs()
    sel = [int(x) for x in sys.argv[1:]] if len(sys.argv) > 1 else None
    if sel: J = [j for j in J if j[0] in sel]
    from multiprocessing import Pool
    with Pool(2) as p:
        for n, kind, P in p.imap_unordered(render, J):
            print("done", n, kind, P["answer"], P["options"], flush=True)
