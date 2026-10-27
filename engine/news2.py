"""Noggin "REAL OR FAKE?" news Shorts, v2 (modern look, real photos, music bed, no ticks).

Each video shows 3 headlines over a real photo. Reading time grows with headline length, then a 3-second
TRUE / FAKE vote with a soft riser, then the reveal. REAL stories show the source article card
(outlet, date, the article's headline, site). FAKE ones show what is actually true.

Usage:  python3 news2.py days/news_sample2.py out.mp4
The data module defines:
  ITEMS = [dict(text, photo, credit, real, source=dict(outlet, date, headline, url) | fix=str, fix_photo=, fix_credit=,
                explain_photo=, explain_credit=), ...]
  MUSIC = (path, start_seconds)
Rules: real stories only from trusted outlets, checked on the day; no crime, deaths, disasters or politics.
Photos only from free-license libraries (Wikimedia Commons / NASA), credited in the description. Never news photos.
"""
import importlib.util, math, os, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from mascot import mascot

W, H, FPS = 1080, 1920, 30
GF = "/usr/share/fonts/truetype/google-fonts/"
GREEN, RED, ACC, WHITE = (46, 213, 115), (255, 71, 87), (255, 196, 0), (255, 255, 255)
MUTED = (170, 172, 190)
VOTE, REVEAL, EXPLAIN = 3.0, 1.4, 4.6
OUTRO = 2.8
_fc = {}
def F(sz, w="Bold"):
    k = (sz, w)
    if k not in _fc: _fc[k] = ImageFont.truetype(GF + f"Poppins-{w}.ttf", sz)
    return _fc[k]

def read_time(text):
    """~3.3 words/second plus 1.5s to settle, kept between 3.5s and 8s."""
    return max(3.5, min(8.0, 1.5 + 0.3*len(text.split())))

def timeline(items):
    t, segs = 0.0, []
    for i, it in enumerate(items):
        s = dict(i=i, start=t); s["vote"] = t + read_time(it["text"]); s["reveal"] = s["vote"] + VOTE
        s["explain"] = s["reveal"] + REVEAL; s["end"] = s["explain"] + EXPLAIN
        segs.append(s); t = s["end"]
    return segs, t + OUTRO

def ease(u): u = max(0.0, min(1.0, u)); return 1 - (1 - u)**3
def ease_io(u): u = max(0.0, min(1.0, u)); return u*u*(3 - 2*u)

def wrap_lines(text, f, maxw):
    meas = ImageDraw.Draw(Image.new("L", (1, 1))); lines, cur = [], ""
    for w_ in text.split():
        tr = (cur + " " + w_).strip()
        if meas.textlength(tr, font=f) <= maxw or not cur: cur = tr
        else: lines.append(cur); cur = w_
    return lines + [cur]

def text_block(text, maxw, maxh, start, w="Bold", fill=WHITE, align="left", spacing=1.15, minsz=30):
    sz = start
    while True:
        f = F(sz, w); lines = wrap_lines(text, f, maxw); lh = int(sz*spacing)
        if len(lines)*lh <= maxh or sz <= minsz: break
        sz -= 2
    meas = ImageDraw.Draw(Image.new("L", (1, 1)))
    wid = int(max(meas.textlength(l, font=f) for l in lines)) + 6
    im = Image.new("RGBA", (wid if align != "left" else maxw, len(lines)*lh + int(sz*0.3)), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for k, l in enumerate(lines):
        x = 0 if align == "left" else (im.width - meas.textlength(l, font=f))/2
        d.text((x, k*lh), l, font=f, fill=fill)
    return im

def shadowed(im, r=18, a=150):
    pad = r*2; sh = Image.new("RGBA", (im.width + pad*2, im.height + pad*2), (0, 0, 0, 0))
    m = im.getchannel("A").point(lambda v: a if v else 0); sh.paste((0, 0, 0, 255), (pad, pad + 8), m)
    sh = sh.filter(ImageFilter.GaussianBlur(r)); sh.alpha_composite(im, (pad, pad)); return sh

def rr_mask(size, r):
    m = Image.new("L", size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), r, fill=255); return m

def cover(img, size):
    return ImageOps.fit(img, size, Image.LANCZOS, centering=(0.5, 0.5))

def load_photo(path):
    im = Image.open(os.path.join(HERE, path))
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA"); bg = Image.new("RGB", im.size, (8, 10, 20)); bg.paste(im, (0, 0), im); im = bg
    return im.convert("RGB")

def background(photo):
    b = cover(photo, (W//6, H//6)).filter(ImageFilter.GaussianBlur(6)).resize((W, H), Image.BICUBIC)
    b = Image.blend(b, Image.new("RGB", (W, H), (6, 7, 14)), 0.72).convert("RGBA")
    g = np.zeros((H, W, 4), np.uint8); g[..., 3] = (np.linspace(40, 230, H)[:, None]).astype(np.uint8)
    b.alpha_composite(Image.fromarray(g, "RGBA")); return b

PW, PH, PX, PY = 960, 800, 60, 300   # photo card
def photo_card(photo, credit, zoom):
    s = 1 + 0.06*zoom; big = cover(photo, (int(PW*s), int(PH*s)))
    ox, oy = (big.width - PW)//2, (big.height - PH)//2
    card = big.crop((ox, oy, ox + PW, oy + PH)).convert("RGBA")
    g = np.zeros((PH, PW, 4), np.uint8); g[..., 3] = (np.clip(np.linspace(-200, 200, PH), 0, 200)[:, None]).astype(np.uint8)
    card.alpha_composite(Image.fromarray(g, "RGBA"))
    d = ImageDraw.Draw(card); d.text((PW - 24, PH - 22), credit, font=F(22, "Medium"), fill=(230, 230, 235, 210), anchor="rs")
    card.putalpha(rr_mask((PW, PH), 44)); return card

def chip(txt, bg, fg=WHITE, sz=30, padx=24, pady=12, w="Bold"):
    meas = ImageDraw.Draw(Image.new("L", (1, 1))); tw = meas.textlength(txt, font=F(sz, w))
    im = Image.new("RGBA", (int(tw + padx*2), sz + pady*2 + 6), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, im.width - 1, im.height - 1), im.height//2, fill=bg)
    d.text((im.width/2, im.height/2), txt, font=F(sz, w), fill=fg, anchor="mm"); return im

def vote_pill(label, col, state, u=0.0):
    """state: idle / win / lose"""
    bw, bh = 450, 150; im = Image.new("RGBA", (bw, bh), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if state == "idle":
        d.rounded_rectangle((0, 0, bw - 1, bh - 1), 75, fill=(255, 255, 255, 22), outline=col + (255,), width=5); fg = col
    elif state == "win":
        d.rounded_rectangle((0, 0, bw - 1, bh - 1), 75, fill=col + (255,)); fg = WHITE
    else:
        d.rounded_rectangle((0, 0, bw - 1, bh - 1), 75, fill=(255, 255, 255, 12), outline=(255, 255, 255, 50), width=3); fg = (120, 122, 140)
    d.text((bw/2, bh/2 + 2), label, font=F(64), fill=fg, anchor="mm"); return im

def ring(k, u, col=WHITE):
    s = 220; im = Image.new("RGBA", (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse((8, 8, s - 8, s - 8), fill=(8, 9, 16, 170), outline=(255, 255, 255, 40), width=8)
    d.arc((8, 8, s - 8, s - 8), -90, -90 + 360*(1 - u), fill=col, width=8)
    d.text((s/2, s/2 + 4), str(k), font=F(110, "Medium"), fill=WHITE, anchor="mm"); return im

def source_card(src):
    cw = 960; head = text_block(f'"{src["headline"]}"', cw - 96, 220, 46, w="Medium", fill=(225, 226, 235))
    ch = 270 + head.height
    im = Image.new("RGBA", (cw, ch), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, cw - 1, ch - 1), 40, fill=(18, 20, 32, 235), outline=(255, 255, 255, 40), width=2)
    d.rounded_rectangle((48, 44, 48 + 14, 44 + 120), 7, fill=GREEN)
    d.text((88, 40), "VERIFIED SOURCE", font=F(28, "Bold"), fill=GREEN)
    d.text((88, 72), src["outlet"], font=F(56, "Bold"), fill=WHITE)
    d.text((88, 160), src["date"], font=F(30, "Regular"), fill=MUTED, anchor="lm")
    im.alpha_composite(head, (48, 210))
    d.text((48, 222 + head.height), src["url"], font=F(30, "Medium"), fill=(110, 170, 255))
    return im

def truth_card(fix, photo=None, credit=""):
    cw = 960; body = text_block(fix, cw - 96 - (300 if photo else 0), 330, 48, w="Medium", fill=(230, 231, 240))
    ch = max(150 + body.height, 380 if photo else 0)
    im = Image.new("RGBA", (cw, ch), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, cw - 1, ch - 1), 40, fill=(18, 20, 32, 235), outline=(255, 255, 255, 40), width=2)
    d.rounded_rectangle((48, 44, 62, 100), 7, fill=RED)
    d.text((88, 40), "THE REAL STORY", font=F(28, "Bold"), fill=RED)
    im.alpha_composite(body, (48, 110))
    if photo is not None:
        p = cover(photo, (270, ch - 60)).convert("RGBA"); pd = ImageDraw.Draw(p)
        pd.text((p.width - 10, p.height - 10), credit, font=F(16, "Medium"), fill=(230, 230, 235), anchor="rs")
        p.putalpha(rr_mask(p.size, 28)); im.alpha_composite(p, (cw - 300, 30))
    return im

def big_verdict(real):
    col = GREEN if real else RED; txt = "TRUE" if real else "FAKE"
    im = Image.new("RGBA", (900, 260), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.text((450, 130), txt, font=F(210, "Bold"), fill=col, anchor="mm")
    return shadowed(im, 24, 170)

def make_video(items, out, wav):
    segs, total = timeline(items); NF = int(round(total*FPS))
    logo = mascot("idle", (0.3, -0.3)).resize((96, 105), Image.LANCZOS)
    brand = Image.new("RGBA", (W, 200), (0, 0, 0, 0)); d = ImageDraw.Draw(brand)
    brand.alpha_composite(logo, (52, 70)); d.text((160, 122), "NOGGIN", font=F(40, "Bold"), fill=WHITE, anchor="lm")
    d.text((160 + d.textlength("NOGGIN", font=F(40, "Bold")) + 12, 122), "NEWS", font=F(40, "Light"), fill=WHITE, anchor="lm")
    rof = chip("REAL OR FAKE?", ACC, (15, 15, 20), 30)
    nreal = sum(it["real"] for it in items)
    hook = text_block(f"{nreal} are real. {len(items) - nreal} is fake. Spot it.", 960, 70, 44, w="Medium", fill=(235, 235, 245), align="center")
    o1 = text_block("How many did you get?", 960, 120, 86, align="center"); o2 = text_block("Comment your score", 960, 70, 50, w="Medium", fill=ACC, align="center")
    for s in segs:
        it = items[s["i"]]
        s["photo"] = load_photo(it["photo"]); s["bg"] = background(s["photo"])
        if it.get("explain_photo"): s["photo2"] = load_photo(it["explain_photo"]); s["bg2"] = background(s["photo2"])
        s["head"] = text_block(it["text"], 940, 420, 76)
        s["count"] = chip(f"{s['i'] + 1} / {len(items)}", (10, 10, 18, 190), WHITE, 30)
        s["verdict"] = big_verdict(it["real"])
        s["card"] = source_card(it["source"]) if it["real"] else truth_card(it["fix"], load_photo(it["fix_photo"]) if it.get("fix_photo") else None, it.get("fix_credit", ""))
        s["pills"] = {st: (vote_pill("TRUE", GREEN, st), vote_pill("FAKE", RED, st)) for st in ("idle", "win", "lose")}
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in range(NF):
        t = f/FPS
        s = next((x for x in segs if t < x["end"]), None)
        if s is None:  # outro
            u = t - segs[-1]["end"]; fr = segs[-1].get("bg2", segs[-1]["bg"]).copy()
            fr.alpha_composite(brand, (0, 0)); fr.alpha_composite(rof, (W - rof.width - 52, 98))
            a = ease(u/0.5); fr.alpha_composite(o1, ((W - o1.width)//2, int(820 - 40*(1 - a))))
            fr.alpha_composite(o2, ((W - o2.width)//2, 960))
            m = mascot("wave", (0, 0)).resize((288, 315), Image.LANCZOS); fr.alpha_composite(m, (W//2 - 144, 1150 + int(10*math.sin(t*5))))
            ff.stdin.write(fr.convert("RGB").tobytes()); continue
        it = items[s["i"]]; lt = t - s["start"]
        two = "photo2" in s and t >= s["explain"]
        fr = (s["bg2"] if two else s["bg"]).copy()
        fr.alpha_composite(brand, (0, 0)); fr.alpha_composite(rof, (W - rof.width - 52, 98))
        # transition in (slide + fade)
        tin = ease(lt/0.45) if s["i"] else 1.0
        dx = int((1 - tin)*120)
        # photo card with slow zoom; crossfade to explain photo
        zoom = min(1.0, lt/(s["end"] - s["start"]))
        card = photo_card(s["photo"], it["credit"], zoom)
        if "photo2" in s and t >= s["explain"] - 0.4:
            c2 = photo_card(s["photo2"], it["explain_credit"], (t - s["explain"])/EXPLAIN)
            card = Image.blend(card, c2, ease_io((t - s["explain"] + 0.4)/0.6))
        # after reveal, photo shrinks up to make room for the card
        ex = ease_io((t - s["explain"])/0.5) if t >= s["explain"] else 0.0
        sc = 1 - 0.36*ex
        cimg = card if sc > 0.995 else card.resize((int(PW*sc), int(PH*sc)), Image.LANCZOS)
        if tin < 1: cimg = Image.blend(Image.new("RGBA", cimg.size, (0, 0, 0, 0)), cimg, tin)
        cx = (W - cimg.width)//2 + dx; cy = PY
        fr.alpha_composite(cimg, (cx, cy))
        fr.alpha_composite(s["count"], (cx + 28, cy + 28))
        # headline
        hy = cy + cimg.height + 50
        head = s["head"] if tin >= 1 else Image.blend(Image.new("RGBA", s["head"].size, (0, 0, 0, 0)), s["head"], tin)
        fr.alpha_composite(head, (70 + dx, hy)); d = ImageDraw.Draw(fr)
        bar_y = hy + s["head"].height + 26
        if s["i"] == 0 and t < 3.2:
            hk = s.get("_hook") or hook; a = min(1, (3.2 - t)*2.5)
            fr.alpha_composite(Image.blend(Image.new("RGBA", hk.size, (0, 0, 0, 0)), hk, a), ((W - hk.width)//2, cy - 66))
        if t < s["vote"]:  # reading bar
            u = lt/(s["vote"] - s["start"])
            d.rounded_rectangle((70, bar_y, 1010, bar_y + 8), 4, fill=(255, 255, 255, 40))
            d.rounded_rectangle((70, bar_y, 70 + max(8, int(940*u)), bar_y + 8), 4, fill=ACC)
            d.text((70, bar_y + 30), "READ IT", font=F(28, "Medium"), fill=MUTED)
        # vote
        if s["vote"] <= t < s["explain"]:
            st = "idle" if t < s["reveal"] else None
            if st: pt, pf = s["pills"]["idle"]
            else: pt, pf = (s["pills"]["win"][0], s["pills"]["lose"][1]) if it["real"] else (s["pills"]["lose"][0], s["pills"]["win"][1])
            a = ease((t - s["vote"])/0.35); py = int(bar_y + 40 + 40*(1 - a))
            for img, x in ((pt, 70), (pf, W - 70 - 450)):
                fr.alpha_composite(Image.blend(Image.new("RGBA", img.size, (0, 0, 0, 0)), img, a) if a < 1 else img, (x, py))
            if t < s["reveal"]:
                k = 3 - int(t - s["vote"]); u = (t - s["vote"]) % 1
                r = ring(k, u); fr.alpha_composite(r, ((W - r.width)//2, cy + cimg.height//2 - r.height//2))
        # reveal flash + verdict
        if s["reveal"] <= t < s["explain"] + 0.3:
            u = t - s["reveal"]; col = GREEN if it["real"] else RED
            fl = max(0, 0.35 - u*0.7)
            if fl > 0: fr.alpha_composite(Image.new("RGBA", (W, H), col + (int(255*fl),)))
            sc2 = 1.25 - 0.25*ease(u/0.3); v = s["verdict"].resize((int(s["verdict"].width*sc2), int(s["verdict"].height*sc2)), Image.LANCZOS)
            fade = 1 if t < s["explain"] else max(0, 1 - (t - s["explain"])/0.3)
            if fade < 1: v = Image.blend(Image.new("RGBA", v.size, (0, 0, 0, 0)), v, fade)
            fr.alpha_composite(v, ((W - v.width)//2, cy + PH//2 - v.height//2))
        # explain card
        if t >= s["explain"]:
            u = ease((t - s["explain"] - 0.15)/0.5); c = s["card"]
            y = int(bar_y + 20 + 80*(1 - u))
            fr.alpha_composite(Image.blend(Image.new("RGBA", c.size, (0, 0, 0, 0)), c, u) if u < 1 else c, ((W - c.width)//2, y))
        # fade to next
        if s["end"] - t < 0.25 and s["i"] < len(segs) - 1:
            fr.alpha_composite(Image.new("RGBA", (W, H), (6, 7, 14, int(255*(1 - (s["end"] - t)/0.25)*0.8))))
        ff.stdin.write(fr.convert("RGB").tobytes())
    ff.stdin.close(); ff.wait()
    return segs, total

def make_audio(items, music, path):
    """Music bed from the given track plus soft cinematic hits. No ticks, no cartoon sounds."""
    segs, total = timeline(items); sr = 44100; N = int(sr*(total + 0.5))
    mpath, mstart = music
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(mstart), "-t", str(total + 1), "-i", os.path.join(HERE, mpath),
                          "-ac", "2", "-ar", str(sr), "-f", "s16le", "-"], capture_output=True, check=True).stdout
    mus = np.frombuffer(raw, np.int16).reshape(-1, 2).astype(float)/32768
    m = np.zeros((N, 2)); m[:min(N, len(mus))] = mus[:N]
    fx = np.zeros(N); rng = np.random.default_rng(7)
    def add(sig, t):
        i = int(t*sr); n = min(len(sig), N - i)
        if n > 0 and i >= 0: fx[i:i + n] += sig[:n]
    def tt(d): return np.arange(int(d*sr))/sr
    def env(n, dec): return np.exp(-np.arange(n)/(sr*dec))
    def lp(x, k): return np.convolve(x, np.ones(k)/k, mode="same")
    def whoosh(t, d=0.5, a=0.35):
        x = rng.standard_normal(int(d*sr)); e = np.sin(np.linspace(0, np.pi, len(x)))**2; add(a*lp(x, 14)*e, t)
    def sub_hit(t, a=0.9):
        x = tt(0.9); f = 38 + 50*np.exp(-x*10); add(a*np.sin(2*np.pi*np.cumsum(f)/sr)*env(len(x), 0.28), t)
        n = rng.standard_normal(int(0.12*sr)); add(0.25*lp(n, 3)*env(len(n), 0.03), t)
    def riser(t, d):
        x = tt(d); n = rng.standard_normal(len(x)); u = x/d
        sig = 0.22*u**2*lp(n, max(2, 20)) + 0.08*u**2*np.sin(2*np.pi*(180*x + 260*x**2/d))
        add(sig, t)
    def bell(t, notes, a=0.16):
        for j, fr in enumerate(notes):
            x = tt(1.6); add(a*(np.sin(2*np.pi*fr*x) + 0.25*np.sin(2*np.pi*fr*2.01*x))*env(len(x), 0.5)*np.minimum(1, x*200), t + j*0.07)
    def glitch(t):
        for j in range(5):
            n = rng.standard_normal(int(0.04*sr)); add(0.18*n*env(len(n), 0.02), t + j*0.05)
        x = tt(0.5); add(0.3*np.sign(np.sin(2*np.pi*55*x))*env(len(x), 0.15)*0.5, t)
    sub_hit(0.0, 0.7)
    for s in segs:
        it = items[s["i"]]
        if s["i"]: whoosh(s["start"] - 0.15, 0.5, 0.4)
        whoosh(s["vote"], 0.35, 0.25); riser(s["vote"], VOTE)
        sub_hit(s["reveal"])
        if it["real"]: bell(s["reveal"] + 0.02, [659.3, 987.8, 1318.5])
        else: glitch(s["reveal"] + 0.02)
        whoosh(s["explain"] + 0.1, 0.45, 0.28)
    sub_hit(segs[-1]["end"], 0.6)
    # duck the music while reading less, drop it during the riser, pump it back on the reveal
    g = np.full(N, 0.55)
    for s in segs:
        a, b = int(s["vote"]*sr), int(s["reveal"]*sr); g[a:b] = np.linspace(0.5, 0.18, b - a)
        c = int((s["reveal"] + 0.6)*sr); g[b:c] = np.linspace(0.25, 0.55, c - b)
    fade_in = int(0.4*sr); g[:fade_in] *= np.linspace(0, 1, fade_in)
    fo = int(1.5*sr); g[-fo:] *= np.linspace(1, 0, fo)
    k = int(0.05*sr); g = np.convolve(g, np.ones(k)/k, mode="same")
    out = m*g[:, None] + fx[:, None]
    out = out/np.abs(out).max()*0.92
    st = (out*32767).astype(np.int16)
    with wave.open(path, "wb") as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes(st.tobytes())

def load(path):
    spec = importlib.util.spec_from_file_location("news_day", path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

if __name__ == "__main__":
    data, out = sys.argv[1], sys.argv[2]
    mod = load(data); items = mod.ITEMS
    for it in items:
        assert ("source" in it) == it["real"] and ("fix" in it) == (not it["real"]), it
    wav = out + ".wav"; make_audio(items, mod.MUSIC, wav); segs, total = make_video(items, out, wav); os.remove(wav)
    print("total", round(total, 1), "s")
    for s in segs: print(s["i"] + 1, "read", round(s["vote"] - s["start"], 1), "s", items[s["i"]]["text"], "->", "REAL" if items[s["i"]]["real"] else "FAKE")
