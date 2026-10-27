"""THE NOGGIN TIMES: real-news Shorts in a retro newspaper look (analog / print revival style).

Paper texture + grain, Fraktur masthead, Times-style headlines, typewriter labels, halftone black-and-white photos
with tape corners, red "EXTRA!" stamp, page-turn transitions. Real stories only. Sound: ambient bed + paper rustles + stamp thuds.

Usage:  python3 news4.py days/news_sample3.py out.mp4      (same data format as news3.py)
"""
import math, os, random, subprocess, sys, wave, datetime
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from news2 import read_time, ease, ease_io, load_photo, ambient_bed, load
from mascot import mascot

W, H, FPS = 1080, 1920, 30
FD = os.path.join(HERE, "assets", "fonts")
PAPER = (236, 229, 211); INK = (24, 22, 20); RED = (190, 32, 36); GREY = (95, 90, 82)
OUTRO = 3.4; TURN = 0.55
_fc = {}
def F(name, sz):
    k = (name, sz)
    if k not in _fc:
        fn = {"frak": "KaTeX_Fraktur-Bold.ttf", "head": "texgyretermes-bold.otf", "body": "texgyretermes-regular.otf",
              "ital": "texgyretermes-italic.otf", "boldital": "texgyretermes-bolditalic.otf",
              "type": "texgyrecursor-bold.otf", "typer": "texgyrecursor-regular.otf"}[name]
        _fc[k] = ImageFont.truetype(os.path.join(FD, fn), sz)
    return _fc[k]

def detail_time(it): return max(6.0, min(11.0, 3.2 + 0.28*len(it["detail"].split()) + 0.03*len(it.get("body", "").split())))

def timeline(items):
    t, segs = 0.0, []
    for i, it in enumerate(items):
        s = dict(i=i, start=t); s["explain"] = t + read_time(it["text"]) + (0.6 if i == 0 else 0.3); s["end"] = s["explain"] + detail_time(it)
        segs.append(s); t = s["end"]
    return segs, t + OUTRO

MEAS = ImageDraw.Draw(Image.new("L", (1, 1)))
def wrap(text, f, maxw):
    lines, cur = [], ""
    for w_ in text.split():
        tr = (cur + " " + w_).strip()
        if MEAS.textlength(tr, font=f) <= maxw or not cur: cur = tr
        else: lines.append(cur); cur = w_
    return lines + [cur]

def fit_lines(text, name, maxw, maxh, start, lh=1.08, minsz=40):
    sz = start
    while True:
        f = F(name, sz); ls = wrap(text, f, maxw)
        if len(ls)*sz*lh <= maxh or sz <= minsz: return f, ls, int(sz*lh)
        sz -= 2

# ---------- paper ----------
def make_paper(seed=1):
    rng = np.random.default_rng(seed)
    base = np.ones((H, W, 3))*np.array(PAPER, float)
    n = rng.standard_normal((H//4, W//4)); n = np.array(Image.fromarray(((n - n.min())/(n.max() - n.min())*255).astype(np.uint8)).resize((W, H), Image.BICUBIC), float)/255
    base *= (0.96 + 0.06*n)[..., None]
    fib = Image.new("L", (W, H), 0); d = ImageDraw.Draw(fib); r = random.Random(seed)
    for _ in range(900):
        x, y = r.uniform(0, W), r.uniform(0, H); a = r.uniform(0, math.pi); L = r.uniform(4, 22)
        d.line((x, y, x + L*math.cos(a), y + L*math.sin(a)), fill=r.randint(10, 40), width=1)
    base -= np.array(fib, float)[..., None]*0.35
    yy, xx = np.mgrid[0:H, 0:W]; v = ((xx - W/2)/(W*0.75))**2 + ((yy - H/2)/(H*0.75))**2
    base *= (1 - 0.22*np.clip(v, 0, 1))[..., None]
    fold = np.exp(-((yy - H*0.5)/6.0)**2)*0.05 - np.exp(-((yy - H*0.5 - 9)/10.0)**2)*0.03    # horizontal fold crease
    base *= (1 - fold)[..., None]
    return Image.fromarray(np.clip(base, 0, 255).astype(np.uint8), "RGB").convert("RGBA")

def grain_layers(k=4, seed=3):
    rng = np.random.default_rng(seed); out = []
    for _ in range(k):
        g = rng.integers(0, 2, (H//2, W//2)).astype(np.uint8)*255
        a = (rng.random((H//2, W//2)) < 0.035)*28
        im = Image.merge("RGBA", [Image.fromarray(g)]*3 + [Image.fromarray(a.astype(np.uint8))]).resize((W, H), Image.NEAREST)
        out.append(im)
    return out

# ---------- photo: halftone print ----------
def halftone(photo, size, cell=6):
    w, h = size; g = ImageOps.grayscale(ImageOps.fit(photo, (w, h), Image.LANCZOS))
    g = ImageOps.autocontrast(g, cutoff=1); g = ImageEnhance.Contrast(g).enhance(1.15)
    a = np.array(g, float)/255
    S = 3; big = Image.new("L", (w*S, h*S), 255); d = ImageDraw.Draw(big)
    for y in range(0, h, cell):
        for x in range(0, w, cell):
            off = cell/2 if (y//cell) % 2 else 0
            cx, cy = x + off + cell/2, y + cell/2
            v = a[min(h - 1, int(cy)), min(w - 1, int(cx))]
            r = (1 - v)**0.8*cell*0.78
            if r > 0.25: d.ellipse(((cx - r)*S, (cy - r)*S, (cx + r)*S, (cy + r)*S), fill=0)
    ht = np.array(big.resize((w, h), Image.LANCZOS), float)/255
    a = np.clip(a*0.85 + 0.12, 0, 1)
    mix = 0.3*ht + 0.7*a    # mostly continuous tone + a light dot screen, so it still reads on a phone
    ink = np.array(INK, float); pap = np.array(PAPER, float)*0.97
    rgb = pap[None, None]*mix[..., None] + ink[None, None]*(1 - mix[..., None])
    return Image.fromarray(rgb.astype(np.uint8), "RGB").convert("RGBA")

def tape(w=150, h=46, ang=-35, seed=0):
    r = random.Random(seed); im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    pts = [(0, r.randint(0, 6))] + [(x, r.randint(0, 5)) for x in range(10, w, 14)] + [(w, r.randint(0, 6)), (w, h - r.randint(0, 6))] + \
          [(x, h - r.randint(0, 5)) for x in range(w - 10, 0, -14)] + [(0, h - r.randint(0, 6))]
    d.polygon(pts, fill=(235, 225, 190, 165))
    return im.rotate(ang, expand=True, resample=Image.BICUBIC)

def photo_block(photo, w, h, caption, seed):
    pic = halftone(photo, (w + 60, h + 40))
    blk = Image.new("RGBA", (w + 80, h + 120), (0, 0, 0, 0))
    return pic, blk

def stamp(text, sz=120, col=RED, ang=-12, seed=5):
    f = F("head", sz); tw = MEAS.textlength(text, font=f)
    im = Image.new("RGBA", (int(tw + 80), int(sz*1.5)), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((6, 6, im.width - 6, im.height - 6), 18, outline=col + (255,), width=10)
    d.text((im.width/2, im.height/2 + 4), text, font=f, fill=col + (255,), anchor="mm")
    rng = np.random.default_rng(seed); a = np.array(im); m = rng.random(a.shape[:2]) < 0.18; a[m, 3] = (a[m, 3]*0.25).astype(np.uint8)
    im = Image.fromarray(a).filter(ImageFilter.GaussianBlur(0.6))
    return im.rotate(ang, expand=True, resample=Image.BICUBIC)

def ink_mascot(pose="wave", size=(250, 273)):
    m = mascot(pose, (0, 0)).resize(size, Image.LANCZOS)
    g = ImageOps.grayscale(m.convert("RGB")); g = g.point(lambda v: 30 if v < 120 else (150 if v < 215 else 235))
    rgb = Image.merge("RGB", [g, g, g]).convert("RGBA"); rgb.putalpha(m.getchannel("A")); return rgb

# ---------- static page parts ----------
def masthead(page, issue_no, date_txt):
    d = ImageDraw.Draw(page); M = 50
    d.text((M, 70), f"VOL. I  -  NO. {issue_no}", font=F("type", 26), fill=INK, anchor="lm")
    d.text((W - M, 70), "PRICE: ONE LIKE", font=F("type", 26), fill=INK, anchor="rm")
    d.text((W/2, 70), date_txt.upper(), font=F("typer", 26), fill=INK, anchor="mm")
    d.line((M, 96, W - M, 96), fill=INK, width=2)
    mf = F("frak", 118 if MEAS.textlength("The Noggin Times", font=F("frak", 118)) < W - 90 else 100)
    while MEAS.textlength("The Noggin Times", font=mf) > W - 90: mf = F("frak", mf.size - 4)
    d.text((W/2, 170), "The Noggin Times", font=mf, fill=INK, anchor="mm")
    d.line((M, 246, W - M, 246), fill=INK, width=5); d.line((M, 256, W - M, 256), fill=INK, width=2)
    d.text((W/2, 284), "ALL THE NEWS YOUR BRAIN CAN HOLD", font=F("ital", 30), fill=INK, anchor="mm")
    d.line((M, 310, W - M, 310), fill=INK, width=2)

def footer(page, txt):
    d = ImageDraw.Draw(page); d.line((50, H - 120, W - 50, H - 120), fill=INK, width=2)
    d.text((W/2, H - 84), txt, font=F("type", 28), fill=INK, anchor="mm")

SB_W = 300; MAIN_W = W - 120 - SB_W - 34      # main column / sidebar widths when briefs are shown

def draw_sidebar(page, briefs, y0, y1):
    """'IN BRIEF' column: launches, drops, sport, votes, strikes... each with price/date and a tiny source line."""
    d = ImageDraw.Draw(page); x0 = W - 60 - SB_W
    d.line((x0 - 17, y0, x0 - 17, y1), fill=INK, width=2)
    d.rectangle((x0, y0, x0 + SB_W, y0 + 54), fill=INK)
    d.text((x0 + SB_W/2, y0 + 27), "IN BRIEF", font=F("head", 36), fill=PAPER, anchor="mm")
    y = y0 + 74; gap = 18
    for k, b in enumerate(briefs):
        blk = []
        blk.append(("type", 22, RED, [b["cat"].upper()], 28))
        f, ls, lh = fit_lines(b["title"], "head", SB_W, 140, 33, lh=1.06, minsz=26); blk.append(("head", f.size, INK, ls, lh))
        fb = F("body", 24); blk.append(("body", 24, INK, wrap(b["text"], fb, SB_W), 28))
        if b.get("price"): blk.append(("type", 24, INK, wrap(b["price"], F("type", 24), SB_W), 30))
        src = b["source"]; blk.append(("ital", 19, GREY, wrap(f"Source: {src['outlet']}, {src['date']}", F("ital", 19), SB_W), 23))
        h = sum(len(ls)*lh for _, _, _, ls, lh in blk) + 10
        if y + h > y1: break
        for name, sz, col, ls, lh in blk:
            for l in ls: d.text((x0, y), l, font=F(name, sz), fill=col); y += lh
        y += gap
        if k < len(briefs) - 1 and y + 30 < y1:
            d.line((x0, y - gap/2, x0 + SB_W, y - gap/2), fill=INK, width=1); y += 6

class Story:
    def __init__(self, it, i, n, paper, issue_no, date_txt, briefs=None):
        self.it = it; self.i = i; self.n = n; self.briefs = briefs or []
        self.mw = MAIN_W if self.briefs else W - 120
        self.photo = load_photo(it["photo"]); self.photo2 = load_photo(it["explain_photo"]) if it.get("explain_photo") else None
        page = paper.copy(); masthead(page, issue_no, date_txt)
        footer(page, "CONTINUED ON NEXT PAGE  >>" if i < n - 1 else "FOLLOW FOR TOMORROW'S EDITION")
        d = ImageDraw.Draw(page); M = 60
        d.text((M, 352), f"STORY {i + 1} OF {n}  |  THIS REALLY HAPPENED", font=F("type", 26 if self.briefs else 30), fill=RED, anchor="lm")
        f, ls, lh = fit_lines(it["text"], "head", self.mw, 340, 74 if self.briefs else 88, minsz=48)
        y = 386
        for l in ls: d.text((M, y), l, font=f, fill=INK); y += lh
        self.head_bottom = y + 14
        d.line((M, self.head_bottom, M + self.mw, self.head_bottom), fill=INK, width=2)
        if self.briefs: draw_sidebar(page, self.briefs, 330, H - 140)
        self.page = page
        self.py = self.head_bottom + 30
        self.article = self.article_block(self.mw)
        self.ph_full = (H - 140 - 60) - self.py
        self.ph_small = max(240, (H - 150) - self.py - 50 - self.article.height)
        self.pw = self.mw
        self.ht = halftone(self.photo, (self.pw + 70, self.ph_full + 70))
        self.ht2 = halftone(self.photo2, (self.pw + 70, self.ph_full + 70)) if self.photo2 else None
        self.t1, self.t2 = tape(seed=i*3 + 1), tape(ang=35, seed=i*3 + 2)

    def article_block(self, w):
        it = self.it; src = it["source"]; im = Image.new("RGBA", (w, 1400), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        lead_sz = 40 if self.briefs else 48; llh = int(lead_sz*1.22)
        txt = it["detail"]; cap = txt[0]; rest = txt[1:]
        fb = F("body", lead_sz)
        fd = F("head", int(llh*2*0.98)); bb = MEAS.textbbox((0, 0), cap, font=fd); d.text((-bb[0], -bb[1] + 5), cap, font=fd, fill=INK); cw = bb[2] - bb[0] + 14
        lines, cur = [], ""
        for wd in rest.split(" "):
            maxw = w - cw if len(lines) < 2 else w
            tr = cur + (" " if cur else "") + wd
            if MEAS.textlength(tr, font=fb) <= maxw or not cur: cur = tr
            else: lines.append(cur); cur = wd
        lines.append(cur)
        for k, l in enumerate(lines): d.text((cw if k < 2 else 0, k*llh), l, font=fb, fill=INK)
        y = max(len(lines), 2)*llh + 16
        body = it.get("body")
        if body:   # fine print: the longer article text, set small like a real column
            fs = F("body", 27); blh = 33
            for para in body.split("\n"):
                for l in wrap(para.strip(), fs, w): d.text((0, y), l, font=fs, fill=(45, 42, 38)); y += blh
                y += 6
            y += 8
        d.line((0, y, w, y), fill=INK, width=1); y += 16
        d.text((0, y), f"SOURCE: {src['outlet'].upper()}  -  {src['date'].upper()}", font=F("type", 26 if self.briefs else 30), fill=RED); y += 40
        fi, hl, hlh = fit_lines(f'"{src["headline"]}"', "ital", w, 100, 32 if self.briefs else 36, lh=1.15, minsz=24)
        for l in hl: d.text((0, y), l, font=fi, fill=GREY); y += hlh
        d.text((0, y + 4), src["url"], font=F("typer", 26 if self.briefs else 30), fill=INK)
        return im.crop((0, 0, w, y + 40))

    def render(self, t, s, paper_cache=None):
        page = self.page.copy(); lt = t - s["start"]; dur = s["end"] - s["start"]
        ex = ease_io((t - s["explain"])/0.6) if t >= s["explain"] else 0.0
        ph = int(self.ph_full + (self.ph_small - self.ph_full)*ex)
        src = self.ht2 if (self.ht2 is not None and t >= s["explain"]) else self.ht
        pan = lt/dur
        ox = int(35 + 30*math.sin(pan*math.pi - math.pi/2)); oy = int((self.ph_full + 70 - ph)/2 + 20*pan)
        pic = src.crop((ox, oy, ox + self.pw, oy + ph))
        sh = Image.new("RGBA", (self.pw + 40, ph + 40), (0, 0, 0, 0)); ImageDraw.Draw(sh).rectangle((20, 26, self.pw + 20, ph + 26), fill=(0, 0, 0, 70))
        page.alpha_composite(sh.filter(ImageFilter.GaussianBlur(9)), (60 - 20, self.py - 20))
        page.alpha_composite(pic, (60, self.py))
        d = ImageDraw.Draw(page); d.rectangle((60, self.py, 60 + self.pw - 1, self.py + ph - 1), outline=INK, width=3)
        page.alpha_composite(self.t1, (60 - 55, self.py - 40)); page.alpha_composite(self.t2, (60 + self.pw - self.t2.width + 55, self.py - 40))
        cap = self.it["explain_credit"] if (self.ht2 is not None and t >= s["explain"]) else self.it["credit"]
        d.text((60, self.py + ph + 10), "PHOTO: " + cap, font=F("ital", 21 if self.briefs else 24), fill=GREY)
        if ex > 0:
            a = ease((t - s["explain"] - 0.25)/0.5)
            art = self.article
            if a < 1: art = Image.blend(Image.new("RGBA", art.size, (0, 0, 0, 0)), art, a)
            page.alpha_composite(art, (60, self.py + ph + 46 + int(30*(1 - a))))
        return page

def outro_page(paper, issue_no, date_txt, n):
    page = paper.copy(); masthead(page, issue_no, date_txt); footer(page, "FOLLOW FOR TOMORROW'S EDITION")
    d = ImageDraw.Draw(page); M = 60
    d.text((M, 352), "LETTERS TO THE EDITOR", font=F("type", 30), fill=RED, anchor="lm")
    f, ls, lh = fit_lines("Which story was the craziest?", "head", W - 2*M, 300, 104)
    y = 400
    for l in ls: d.text((M, y), l, font=f, fill=INK); y += lh
    d.line((M, y + 20, W - M, y + 20), fill=INK, width=2)
    nums = ", ".join(str(k + 1) for k in range(n - 1)) + f" or {n}"
    d.text((M, y + 60), f"Write your answer in the comments: {nums}.", font=F("body", 46), fill=INK)
    d.text((M, y + 124), "The best replies make tomorrow's paper.", font=F("ital", 44), fill=GREY)
    return page, y + 230

# ---------- render ----------
def make_video(items, out, wav, hook_txt=None, issue_no=1, date_txt=None, briefs=None):
    segs, total = timeline(items); NF = int(round(total*FPS))
    date_txt = date_txt or datetime.date.today().strftime("%A, %B %d, %Y").replace(" 0", " ")
    paper = make_paper(); grains = grain_layers()
    stories = [Story(it, i, len(items), paper, issue_no, date_txt, briefs) for i, it in enumerate(items)]
    extra = stamp("EXTRA!", 150, ang=-9); hook_line = None
    if hook_txt:
        f = F("type", 40); ls = wrap(hook_txt.upper(), f, 900)
        hw = (MAIN_W - 20) if briefs else 960; f = F("type", 34 if briefs else 40); ls = wrap(hook_txt.upper(), f, hw - 60)
        hook_line = Image.new("RGBA", (hw, 50*len(ls) + 30), (0, 0, 0, 0)); hd = ImageDraw.Draw(hook_line)
        hd.rectangle((0, 0, hook_line.width, hook_line.height), fill=PAPER + (240,)); hd.rectangle((0, 0, hook_line.width - 1, hook_line.height - 1), outline=INK, width=3)
        for k, l in enumerate(ls): hd.text((hw//2, 15 + 25 + k*50), l, font=f, fill=INK, anchor="mm")
    opage, oy = outro_page(paper, issue_no, date_txt, len(items)); editor = ink_mascot(size=(440, 481))
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    rj = random.Random(4); jit = (0, 0); prev_last = None
    def frame_at(t):
        s = next((x for x in segs if t < x["end"]), None)
        if s is None:
            pg = opage.copy(); u = t - segs[-1]["end"]
            e = editor; a = ease(u/0.6)
            pg.alpha_composite(e, (W//2 - e.width//2, oy + int(40*(1 - a)) + 120))
            ImageDraw.Draw(pg).text((W//2, oy + e.height + 170), "- The Editor", font=F("ital", 44), fill=INK, anchor="mm")
            return pg
        pg = stories[s["i"]].render(t, s)
        if s["i"] == 0 and t < 2.4:
            u = t; a = 1 if t < 2.0 else max(0, (2.4 - t)/0.4)
            sc = 1.6 - 0.6*ease(u/0.18) if u < 0.18 else 1.0
            st = extra.resize((int(extra.width*sc), int(extra.height*sc)), Image.LANCZOS) if sc != 1 else extra
            if a < 1: st = Image.blend(Image.new("RGBA", st.size, (0, 0, 0, 0)), st, a)
            cy = stories[0].py + stories[0].ph_full//2 - 120; cx0 = 60 + stories[0].pw//2
            pg.alpha_composite(st, (cx0 - st.width//2, cy - st.height//2))
            if hook_line is not None and t > 0.35:
                hl = hook_line if a >= 1 else Image.blend(Image.new("RGBA", hook_line.size, (0, 0, 0, 0)), hook_line, a)
                pg.alpha_composite(hl, (cx0 - hl.width//2, cy + 140))
        return pg
    for f in range(NF):
        t = f/FPS
        pg = frame_at(t)
        # page turn into the next story / outro
        starts = [x["start"] for x in segs[1:]] + [segs[-1]["end"]]
        tb = next((b for b in starts if b <= t < b + TURN), None)
        if tb is not None:
            old = frame_at(tb - 1/FPS); u = ease_io((t - tb)/TURN)
            base = old.copy(); base = Image.blend(base, Image.new("RGBA", (W, H), (0, 0, 0, 255)), 0.35*u)
            x = int(W*(1 - u)); base.alpha_composite(pg.crop((0, 0, W - x, H)), (x, 0)) if x < W else None
            shd = Image.new("RGBA", (60, H), (0, 0, 0, 0)); sd = np.zeros((H, 60, 4), np.uint8); sd[..., 3] = np.linspace(0, 110, 60)[None, :].astype(np.uint8)[:, ::-1]
            if 0 < x < W: base.alpha_composite(Image.fromarray(sd, "RGBA"), (min(W - 60, x - 60 if x >= 60 else 0), 0))
            pg = base
        if f % 3 == 0: jit = (rj.randint(-2, 2), rj.randint(-2, 2))
        pg.alpha_composite(grains[(f//2) % len(grains)])
        fr = Image.new("RGB", (W, H), PAPER); fr.paste(pg.convert("RGB"), jit)
        if f % 5 == 0: fr = ImageEnhance.Brightness(fr).enhance(1 + rj.uniform(-0.012, 0.012))
        ff.stdin.write(fr.tobytes())
    ff.stdin.close(); ff.wait()
    return segs, total

def make_audio(items, path):
    segs, total = timeline(items); sr = 44100; N = int(sr*(total + 0.5))
    m = ambient_bed(N, sr); fx = np.zeros(N); rng = np.random.default_rng(13)
    def add(sig, t):
        i = int(t*sr); n = min(len(sig), N - i)
        if n > 0 and i >= 0: fx[i:i + n] += sig[:n]
    def tt(dd): return np.arange(int(dd*sr))/sr
    def env(n, dec): return np.exp(-np.arange(n)/(sr*dec))
    def lp(x, k): return np.convolve(x, np.ones(k)/k, mode="same")
    def rustle(t, dd=0.55, a=0.5):     # paper page turn: band-passed noise with crackles
        x = rng.standard_normal(int(dd*sr)); bp = lp(x, 3) - lp(x, 25)
        e = np.sin(np.linspace(0, np.pi, len(x)))**1.5
        cr = (rng.random(len(x)) < 0.004)*rng.standard_normal(len(x))*3
        add(a*(bp*e + lp(cr, 2)*e), t)
    def thud(t, a=0.8):                # rubber stamp / press thud
        x = tt(0.35); add(a*np.sin(2*np.pi*(70 + 60*np.exp(-x*30))*x)*env(len(x), 0.07), t)
        n = rng.standard_normal(int(0.05*sr)); add(0.35*lp(n, 6)*env(len(n), 0.012), t)
    def press(t, dur=1.2):             # soft printing-press roll at the start
        x = tt(dur); n = lp(rng.standard_normal(len(x)), 40); pulse = (np.sin(2*np.pi*7*x) > 0.6)*1.0
        add(0.25*n*(0.4 + 0.6*lp(pulse, 400))*np.minimum(1, (dur - x)*3), t)
    press(0.0, 1.1); thud(0.05, 0.9)
    for s in segs:
        if s["i"]: rustle(s["start"] - 0.05)
        thud(s["explain"] + 0.2, 0.45)
    rustle(segs[-1]["end"] - 0.05)
    g = np.full(N, 0.45); fi = int(0.3*sr); g[:fi] *= np.linspace(0, 1, fi); fo = int(1.5*sr); g[-fo:] *= np.linspace(1, 0, fo)
    out = m*g[:, None] + fx[:, None]; out = out/np.abs(out).max()*0.92
    with wave.open(path, "wb") as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes((out*32767).astype(np.int16).tobytes())

if __name__ == "__main__":
    data, out = sys.argv[1], sys.argv[2]
    mod = load(data); items = mod.ITEMS; assert 2 <= len(items) <= 3
    wav = out + ".wav"; make_audio(items, wav)
    segs, total = make_video(items, out, wav, getattr(mod, "HOOK", None), getattr(mod, "ISSUE", 1), getattr(mod, "DATE", None), getattr(mod, "BRIEFS", None)); os.remove(wav)
    print("total", round(total, 1), "s")
