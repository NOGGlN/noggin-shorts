"""Noggin "REAL OR FAKE?" news Shorts.

Each video shows 3 headlines. Viewers get reading time that grows with the headline length, then a 3-second
TRUE / FAKE vote, then the reveal. REAL stories show the source article card (outlet, date, headline, link).
FAKE ones show what is actually true.

Usage:  python3 news.py days/news_sample.py out.mp4
The data module defines ITEMS = [dict(text, emoji, real, source=dict(outlet, date, headline, url) | fix=str), ...]
Rules: real stories only from trusted outlets (AP, Reuters, BBC, Al Jazeera, Fox News, The Guardian, NYT, NASA...),
checked on the day. No crime, deaths, disasters or politics. Never use news photos or video, only Noggin art.
"""
import importlib.util, math, os, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from render import font, text_layer, emoji_img, rounded, paste_center, gradient, with_alpha, DARK
from mascot import mascot, bubble, OUTL

W, H, FPS = 1080, 1920, 30
GREEN, RED, YEL = (39, 196, 104), (232, 57, 70), (255, 210, 0)
VOTE, REVEAL, EXPLAIN_REAL, EXPLAIN_FAKE, OUTRO = 3.0, 1.3, 4.5, 3.4, 2.6

def wrap(text, maxw, maxh, start, fill=DARK, stroke=0, min_size=34):
    """Word-wrap text into lines and shrink the font until the block fits maxw x maxh."""
    meas = ImageDraw.Draw(Image.new("L", (1, 1)))
    sz = start
    while True:
        f = font(sz); lines, cur = [], ""
        for w_ in text.split():
            trial = (cur + " " + w_).strip()
            if meas.textlength(trial, font=f) <= maxw or not cur: cur = trial
            else: lines.append(cur); cur = w_
        lines.append(cur); block = "\n".join(lines)
        b = meas.multiline_textbbox((0, 0), block, font=f, align="center", spacing=sz*0.18, stroke_width=stroke)
        if (b[2] - b[0] <= maxw and b[3] - b[1] <= maxh) or sz <= min_size: break
        sz -= 2
    im = Image.new("RGBA", (int(b[2] - b[0] + 4), int(b[3] - b[1] + 4)), (0, 0, 0, 0))
    ImageDraw.Draw(im).multiline_text((2 - b[0], 2 - b[1]), block, font=f, fill=fill, align="center", spacing=sz*0.18,
                                      stroke_width=stroke, stroke_fill=DARK)
    return im

def read_time(text):
    """Reading time grows with headline length: ~3.3 words/second plus 1.5s to settle, kept between 3.5s and 8s."""
    return max(3.5, min(8.0, 1.5 + 0.3*len(text.split())))

def timeline(items):
    t, segs = 0.0, []
    for i, it in enumerate(items):
        s = dict(i=i, start=t); s["vote"] = t + read_time(it["text"]); s["reveal"] = s["vote"] + VOTE
        s["explain"] = s["reveal"] + REVEAL; s["end"] = s["explain"] + (EXPLAIN_REAL if it["real"] else EXPLAIN_FAKE)
        segs.append(s); t = s["end"]
    return segs, t + OUTRO

def ease(u): u = max(0.0, min(1.0, u)); return 1 - (1 - u)**3
def pop_scale(u):  # 0 -> overshoot -> 1
    u = max(0.0, min(1.0, u)); return 1 + 0.25*math.sin(u*math.pi) if u < 1 else 1.0

def scaled(im, s):
    if abs(s - 1) < 0.01: return im
    return im.resize((max(1, int(im.width*s)), max(1, int(im.height*s))), Image.LANCZOS)

def check_mark(size, col):
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0)); d = ImageDraw.Draw(im); w = size//7
    d.line([(size*0.18, size*0.55), (size*0.42, size*0.78), (size*0.84, size*0.25)], fill=col, width=w, joint="curve"); return im

def cross_mark(size, col):
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0)); d = ImageDraw.Draw(im); w = size//7
    d.line([(size*0.22, size*0.22), (size*0.78, size*0.78)], fill=col, width=w)
    d.line([(size*0.78, size*0.22), (size*0.22, size*0.78)], fill=col, width=w); return im

def button(label, col, mark, state):
    """state: normal / right / dim"""
    bw, bh = 440, 170
    c = col if state != "dim" else (120, 120, 140)
    im = Image.new("RGBA", (bw + 20, bh + 26), (0, 0, 0, 0))
    im.alpha_composite(rounded((bw, bh), 60, (0, 0, 0, 90)), (10, 22))
    im.alpha_composite(rounded((bw, bh), 60, c + (255,)), (10, 6))
    if state == "right":
        ImageDraw.Draw(im).rounded_rectangle((4, 0, bw + 15, bh + 12), 64, outline=(255, 255, 255), width=10)
    im.alpha_composite(mark(100, (255, 255, 255)), (40, 6 + bh//2 - 50))
    paste_center(im, text_layer(label, 260, 110, 96), 10 + bw//2 + 50, 6 + bh//2)
    return im

def headline_card(it):
    cw = 940; tl = wrap(it["text"], cw - 110, 430, 84)
    ch = max(360, tl.height + 150)
    card = Image.new("RGBA", (cw + 20, ch + 30), (0, 0, 0, 0))
    card.alpha_composite(rounded((cw, ch), 56, (0, 0, 0, 80)), (10, 24))
    card.alpha_composite(rounded((cw, ch), 56, (255, 255, 255, 255)), (10, 4))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle((60, 34, 330, 92), 28, fill=RED)
    d.text((195, 64), "HEADLINE", font=font(38), fill="white", anchor="mm")
    paste_center(card, tl, 10 + cw//2, 4 + 70 + (ch - 70)//2)
    return card

def stamp(word, col):
    tl = text_layer(word, 700, 230, 200, fill=col, stroke=0)
    im = Image.new("RGBA", (tl.width + 120, tl.height + 90), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((8, 8, im.width - 8, im.height - 8), 40, fill=(255, 255, 255, 235), outline=col, width=16)
    paste_center(im, tl, im.width//2, im.height//2)
    return im.rotate(-9, resample=Image.BICUBIC, expand=True)

def source_panel(src):
    pw = 960; head = wrap(f'"{src["headline"]}"', pw - 110, 230, 52)
    ph = 330 + head.height
    im = Image.new("RGBA", (pw + 20, ph + 30), (0, 0, 0, 0))
    im.alpha_composite(rounded((pw, ph), 48, (0, 0, 0, 90)), (10, 24))
    im.alpha_composite(rounded((pw, ph), 48, (255, 255, 255, 255)), (10, 4))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((10, 4, 10 + pw, 104), 48, fill=GREEN); d.rectangle((10, 60, 10 + pw, 104), fill=GREEN)
    im.alpha_composite(check_mark(70, (255, 255, 255)), (50, 20))
    d.text((140, 55), "REAL NEWS  -  SOURCE", font=font(48), fill="white", anchor="lm")
    d.text((60, 160), src["outlet"], font=font(68), fill=DARK, anchor="lm")
    d.text((60, 225), src["date"], font=font(40), fill=(120, 120, 140), anchor="lm")
    im.alpha_composite(head, (10 + pw//2 - head.width//2, 270))
    y = 280 + head.height + 25
    d.text((60, y), src["url"], font=font(36), fill=(30, 110, 230), anchor="lm")
    d.line((60, y + 26, 60 + d.textlength(src["url"], font=font(36)), y + 26), fill=(30, 110, 230), width=3)
    return im

def fake_panel(fix):
    pw = 960; body = wrap(fix, pw - 110, 300, 62); ph = 170 + body.height
    im = Image.new("RGBA", (pw + 20, ph + 30), (0, 0, 0, 0))
    im.alpha_composite(rounded((pw, ph), 48, (0, 0, 0, 90)), (10, 24))
    im.alpha_composite(rounded((pw, ph), 48, (255, 255, 255, 255)), (10, 4))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((10, 4, 10 + pw, 104), 48, fill=RED); d.rectangle((10, 60, 10 + pw, 104), fill=RED)
    im.alpha_composite(cross_mark(70, (255, 255, 255)), (50, 20))
    d.text((140, 55), "NOGGIN MADE THAT UP", font=font(48), fill="white", anchor="lm")
    paste_center(im, body, 10 + pw//2, 104 + (ph - 100)//2)
    return im

def make_video(items, out, wav):
    segs, total = timeline(items); NF = int(round(total*FPS))
    bg = gradient("#1b1446", "#4a1491").convert("RGBA")
    title = text_layer("REAL OR FAKE?", 900, 150, 130, fill=YEL, stroke=10)
    nreal = sum(it["real"] for it in items)
    hook = text_layer(f"{nreal} are REAL.  {len(items) - nreal} is FAKE.  Can you tell?", 900, 80, 54, stroke=6)
    outro1 = text_layer("How many did you get?", 960, 140, 100, stroke=9)
    outro2 = text_layer("Comment 0, 1, 2 or 3", 900, 100, 80, fill=YEL, stroke=8)
    ticker_t = "BREAKING  /  REAL OR FAKE?  /  NOGGIN NEWS  /  ONLY TRUSTED SOURCES  /  "
    tick_im = Image.new("RGBA", (int(ImageDraw.Draw(Image.new("L", (1, 1))).textlength(ticker_t, font=font(44))) + 2, 70), (0, 0, 0, 0))
    ImageDraw.Draw(tick_im).text((0, 35), ticker_t, font=font(44), fill="white", anchor="lm")
    for s in segs:
        it = items[s["i"]]
        s["card"] = headline_card(it); s["emoji"] = emoji_img(it["emoji"], 150)
        s["count"] = text_layer(f"{s['i'] + 1} / {len(items)}", 300, 70, 56, stroke=5)
        s["btn"] = {st: (button("TRUE", GREEN, check_mark, st), button("FAKE", RED, cross_mark, st)) for st in ("normal", "right", "dim")}
        s["stamp"] = stamp("TRUE!" if it["real"] else "FAKE!", GREEN if it["real"] else RED)
        s["panel"] = source_panel(it["source"]) if it["real"] else fake_panel(it["fix"])
        s["panel_lbl"] = text_layer("It's REAL! Here's the article:" if it["real"] else "FAKE! Here's the truth:", 960, 80, 60,
                                    fill=GREEN if it["real"] else (255, 120, 130), stroke=6)
    nums = {k: text_layer(str(k), 200, 170, 150, stroke=0, fill=DARK) for k in (1, 2, 3)}
    bub = {k: bubble(k, font, "sideR") for k in ("read fast!", "pick one!", "NO WAY!", "gotcha!", "follow me!")}
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", out]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in range(NF):
        t = f/FPS; fr = bg.copy(); d = ImageDraw.Draw(fr)
        # ticker bar
        d.rectangle((0, 70, W, 150), fill=RED); d.rectangle((0, 70, 300, 150), fill=(150, 20, 35))
        off = -int(t*160) % tick_im.width
        for x0 in (300 - off, 300 - off + tick_im.width, 300 - off + 2*tick_im.width):
            fr.alpha_composite(tick_im, (x0, 75))
        d.rectangle((0, 70, 300, 150), fill=(150, 20, 35)); d.text((150, 110), "NOGGIN NEWS", font=font(40), fill="white", anchor="mm")
        paste_center(fr, title, W//2, 260)
        s = next((x for x in segs if t < x["end"]), None)
        if s is None:  # outro
            u = t - segs[-1]["end"]
            paste_center(fr, scaled(outro1, pop_scale(u*3)), W//2, 760); paste_center(fr, outro2, W//2, 900)
            m = scaled(mascot("wave", (0, 0), blink=(int(t*10) % 30 == 0)), 1.6); paste_center(fr, m, W//2, 1350 + 12*math.sin(t*6))
            fr.alpha_composite(bub["follow me!"], (W//2 - bub["follow me!"].width - 160, 1120))
            ff.stdin.write(fr.convert("RGB").tobytes()); continue
        it = items[s["i"]]; lt = t - s["start"]
        paste_center(fr, s["count"], W//2, 375)
        if s["i"] == 0 and t < 3.0: paste_center(fr, with_alpha(hook, min(1, (3.0 - t)*2)), W//2, 450)
        slide = 0 if s["i"] == 0 else (1 - ease(lt/0.35))*W
        top = 650 if t < s["explain"] else 650 - 310*ease((t - s["explain"])/0.4)
        cy = top + s["card"].height//2; ey = top - 85
        if t < s["explain"]: paste_center(fr, s["emoji"], W//2 + slide, ey + 6*math.sin(t*4))
        paste_center(fr, s["card"], W//2 + slide, cy)
        # read progress bar
        if t < s["vote"]:
            u = lt/(s["vote"] - s["start"]); y = cy + s["card"].height//2 + 60
            d.rounded_rectangle((140, y, 940, y + 36), 18, fill=(255, 255, 255, 60))
            d.rounded_rectangle((140, y, 140 + max(36, int(800*u)), y + 36), 18, fill=YEL)
            d.text((W//2, y + 80), "READ IT...", font=font(48), fill="white", anchor="mm")
        # buttons + countdown
        if s["vote"] <= t < s["explain"]:
            st = "normal" if t < s["reveal"] else "reveal"
            if st == "normal": bt, bf = s["btn"]["normal"]
            else:
                bt = s["btn"]["right" if it["real"] else "dim"][0]; bf = s["btn"]["dim" if it["real"] else "right"][1]
            pulse = (1 + (0.04*math.sin(t*12) if st == "normal" else 0))*pop_scale((t - s["vote"])/0.3)*min(1, 0.3 + (t - s["vote"])/0.15)
            by = cy + s["card"].height//2 + 130
            paste_center(fr, scaled(bt, pulse), 290, by); paste_center(fr, scaled(bf, pulse), 790, by)
            if t < s["reveal"]:
                k = 3 - int(t - s["vote"]); u = (t - s["vote"]) % 1
                circ = Image.new("RGBA", (220, 220), (0, 0, 0, 0)); cd = ImageDraw.Draw(circ)
                cd.ellipse((10, 10, 210, 210), fill=YEL); cd.arc((10, 10, 210, 210), -90, -90 + 360*(1 - u), fill=(255, 255, 255), width=14)
                paste_center(circ, nums[k], 110, 110)
                paste_center(fr, scaled(circ, 1 + 0.15*(1 - ease(u*4))), W//2, by + 230)
        if t >= s["reveal"]:
            u = (t - s["reveal"])/0.25; sc = 2.2 - 1.2*ease(u)
            fade = 1 if t < s["explain"] + 0.2 else max(0, 1 - (t - s["explain"] - 0.2)*3)
            if fade > 0: paste_center(fr, with_alpha(scaled(s["stamp"], sc), fade*min(1, u*2)), W//2, cy)
        if t >= s["explain"]:
            u = ease((t - s["explain"] - 0.2)/0.4); py = 340 + s["card"].height + 110 + (1 - u)*900
            paste_center(fr, s["panel_lbl"], W//2, py - 30)
            fr.alpha_composite(s["panel"], (W//2 - s["panel"].width//2, int(py + 20)))
        # mascot
        if t < s["vote"]: pose, msg = "idle", "read fast!"
        elif t < s["reveal"]: pose, msg = "idle", "pick one!"
        elif it["real"]: pose, msg = "shock", "NO WAY!"
        else: pose, msg = "laugh", "gotcha!"
        if t < s["explain"]:
            m = scaled(mascot(pose, (-0.6, -0.4), blink=(int(t*10) % 34 == 0)), 0.95)
            mx, my = 920, 1730 + 8*math.sin(t*5)
            paste_center(fr, m, mx, my)
            if (t < s["vote"] and lt % 6 < 3) or t >= s["reveal"]:
                b = bub[msg]; fr.alpha_composite(b, (int(mx - m.width//2 - b.width + 30), int(my - 120)))
        ff.stdin.write(fr.convert("RGB").tobytes())
    ff.stdin.close(); ff.wait()
    return segs, total

def make_sfx(items, path):
    segs, total = timeline(items); sr = 44100; N = int(sr*(total + 0.3)); a = np.zeros(N); mus = np.zeros(N)
    rng = np.random.default_rng(5)
    def add(sig, t, buf=a):
        i = int(t*sr); n = min(len(sig), N - i)
        if n > 0 and i >= 0: buf[i:i + n] += sig[:n]
    def tt_(dur): return np.arange(int(dur*sr))/sr
    def env(n, dec): return np.exp(-np.arange(n)/(sr*dec))
    def lp(x, k=8): return np.convolve(x, np.ones(k)/k, mode="same")
    def tick(t, fr, amp=0.5):
        x = tt_(0.07); add((amp*np.sin(2*np.pi*fr*x) + rng.standard_normal(len(x))*0.1)*env(len(x), 0.012), t)
    def whoosh(t, dur=0.4, amp=0.5):
        x = rng.standard_normal(int(dur*sr)); e = np.sin(np.linspace(0, np.pi, len(x)))**2; add(amp*lp(x, 6)*e, t)
    def pop(t, amp=0.5):
        x = tt_(0.12); add(amp*np.sin(2*np.pi*(400*x + 3000*x**2))*env(len(x), 0.04), t)
    def hit(t):
        x = tt_(0.5); add(0.8*np.sin(2*np.pi*60*x)*env(len(x), 0.15), t); whoosh(t, 0.25, 0.4)
    def chime(t):
        for j, fr in enumerate([1046.5, 1318.5, 1568.0, 2093.0]):
            x = tt_(1.2); add(0.2*(np.sin(2*np.pi*fr*x) + 0.3*np.sin(4*np.pi*fr*x))*env(len(x), 0.4), t + j*0.06)
    def buzz(t):
        for j, f0 in enumerate([220, 165]):
            x = tt_(0.28); add(0.22*lp(np.sign(np.sin(2*np.pi*f0*x)), 3)*env(len(x), 0.2), t + j*0.26)
    def laugh(t):
        for j in range(5):
            x = tt_(0.11); f0 = 520 - j*30; sig = np.sign(np.sin(2*np.pi*f0*x))*0.5 + np.sin(4*np.pi*f0*x)*0.5
            add(0.18*lp(sig, 4)*np.sin(np.linspace(0, np.pi, len(x))), t + j*0.13)
    def news_sting(t):
        for j, fr in enumerate([392.0, 523.3, 659.3, 784.0]):
            x = tt_(0.35); add(0.18*np.sign(np.sin(2*np.pi*fr*x))*env(len(x), 0.12), t + j*0.09)
    news_sting(0.0); hit(0.0)
    for s in segs:
        it = items[s["i"]]
        if s["i"]: whoosh(s["start"], 0.4, 0.6)
        pop(s["vote"]); whoosh(s["vote"], 0.3, 0.4)
        for k in range(3): tick(s["vote"] + k, 1300 if k < 2 else 1800, 0.55)
        for k in range(4): tick(s["vote"] + 2 + k*0.25, 1800, 0.35)
        hit(s["reveal"])
        if it["real"]: chime(s["reveal"] + 0.05)
        else: buzz(s["reveal"] + 0.05); laugh(s["reveal"] + 0.4)
        whoosh(s["explain"] + 0.2, 0.4, 0.5); pop(s["explain"] + 0.55)
    news_sting(segs[-1]["end"]); laugh(segs[-1]["end"] + 0.5)
    bpm = 118; beat = 60/bpm; notes = [55.0, 55.0, 65.4, 49.0]; b = 0; t = 0.4
    while t < total - 0.2:
        x = tt_(0.25); add(0.5*np.sin(2*np.pi*(50 + 90*np.exp(-x*30))*x)*env(len(x), 0.08), t, mus)
        h = rng.standard_normal(int(0.04*sr)); h = h - lp(h, 4); add(0.1*h*env(len(h), 0.01), t + beat/2, mus)
        x = tt_(beat*0.9); add(0.2*np.sin(2*np.pi*notes[(b//4) % 4]*x)*np.minimum(1, x*40)*env(len(x), 0.25), t, mus)
        t += beat; b += 1
    duck = np.ones(N)
    for s in segs: duck[int(s["reveal"]*sr):int((s["reveal"] + 1.0)*sr)] = 0.35
    out = a + mus*duck*0.6; out = out/np.abs(out).max()*0.9
    st = (np.stack([out, out], 1)*32767).astype(np.int16)
    with wave.open(path, "wb") as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes(st.tobytes())

def load(path):
    spec = importlib.util.spec_from_file_location("news_day", path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

if __name__ == "__main__":
    data, out = sys.argv[1], sys.argv[2]
    items = load(data).ITEMS
    for it in items:
        assert ("source" in it) == it["real"] and ("fix" in it) == (not it["real"]), it
    wav = out + ".wav"; make_sfx(items, wav); segs, total = make_video(items, out, wav); os.remove(wav)
    print("total", round(total, 1), "s")
    for s in segs: print(s["i"] + 1, "read", round(s["vote"] - s["start"], 1), "s", items[s["i"]]["text"], "->", "REAL" if items[s["i"]]["real"] else "FAKE")
