"""Noggin NEWS Shorts, v3: real stories only, built to be shared. No quiz, no votes, no song.

Each video: 2-3 real, recent, wild stories. For each: photo + punchy headline (reading time grows with length),
then "WHAT HAPPENED" with 1-2 sentences of detail and the verified source (outlet, date, article headline, site).
Ends with "Which one is the craziest? Comment 1, 2 or 3" + follow prompt.

Usage:  python3 news3.py days/news_sample3.py out.mp4
Data module: ITEMS = [dict(text, detail, photo, credit, source=dict(outlet, date, headline, url, link),
                          explain_photo=, explain_credit=), ...]   (2 or 3 items)
             HOOK = "3 things that actually happened this week"   (optional)
"""
import math, os, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from news2 import (W, H, FPS, F, GREEN, ACC, WHITE, MUTED, read_time, ease, ease_io, text_block, rr_mask, cover,
                   load_photo, background, photo_card, chip, PW, PH, PY, ambient_bed, load)
from mascot import mascot

OUTRO = 3.2

def detail_time(it):
    return max(5.0, min(9.0, 2.5 + 0.28*len(it["detail"].split())))

def timeline(items):
    t, segs = 0.0, []
    for i, it in enumerate(items):
        s = dict(i=i, start=t); s["explain"] = t + read_time(it["text"]); s["end"] = s["explain"] + detail_time(it)
        segs.append(s); t = s["end"]
    return segs, t + OUTRO

def detail_card(it):
    cw = 960; src = it["source"]
    body = text_block(it["detail"], cw - 96, 300, 46, w="Medium", fill=(236, 237, 245))
    head = text_block(f'"{src["headline"]}"', cw - 96, 140, 32, w="Regular", fill=MUTED)
    ch = 120 + body.height + 40 + 150 + head.height
    im = Image.new("RGBA", (cw, ch), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, cw - 1, ch - 1), 40, fill=(18, 20, 32, 238), outline=(255, 255, 255, 40), width=2)
    d.rounded_rectangle((48, 44, 62, 96), 7, fill=ACC); d.text((88, 40), "WHAT HAPPENED", font=F(30, "Bold"), fill=ACC)
    im.alpha_composite(body, (48, 110)); y = 110 + body.height + 30
    d.line((48, y, cw - 48, y), fill=(255, 255, 255, 40), width=2); y += 26
    d.ellipse((48, y + 6, 76, y + 34), fill=GREEN); d.line((55, y + 20, 61, y + 27), fill=WHITE, width=4); d.line((61, y + 27, 70, y + 13), fill=WHITE, width=4)
    d.text((92, y), src["outlet"], font=F(40, "Bold"), fill=WHITE)
    ow = d.textlength(src["outlet"], font=F(40, "Bold"))
    d.text((92 + ow + 20, y + 10), src["date"], font=F(28, "Regular"), fill=MUTED)
    y += 64; im.alpha_composite(head, (48, y)); y += head.height + 6
    d.text((48, y), src["url"], font=F(28, "Medium"), fill=(110, 170, 255))
    return im

def make_video(items, out, wav, hook_txt=None):
    segs, total = timeline(items); NF = int(round(total*FPS))
    logo = mascot("idle", (0.3, -0.3)).resize((96, 105), Image.LANCZOS)
    brand = Image.new("RGBA", (W, 200), (0, 0, 0, 0)); d = ImageDraw.Draw(brand)
    brand.alpha_composite(logo, (52, 70)); d.text((160, 122), "NOGGIN", font=F(40, "Bold"), fill=WHITE, anchor="lm")
    d.text((160 + d.textlength("NOGGIN", font=F(40, "Bold")) + 12, 122), "NEWS", font=F(40, "Light"), fill=WHITE, anchor="lm")
    tag = chip("THIS REALLY HAPPENED", ACC, (15, 15, 20), 28)
    hook = text_block(hook_txt or f"{len(items)} things that actually happened this week", 960, 140, 58, align="center")
    nums = " or ".join(str(k + 1) for k in range(len(items))).replace(" or ", ", ", len(items) - 2)
    o1 = text_block("Which one is the craziest?", 960, 130, 84, align="center")
    o2 = text_block(f"Comment {nums}", 960, 70, 54, w="Medium", fill=ACC, align="center")
    o3 = text_block("Follow for wild news every day", 960, 60, 40, w="Medium", fill=MUTED, align="center")
    for s in segs:
        it = items[s["i"]]
        s["photo"] = load_photo(it["photo"]); s["bg"] = background(s["photo"])
        if it.get("explain_photo"): s["photo2"] = load_photo(it["explain_photo"]); s["bg2"] = background(s["photo2"])
        s["head"] = text_block(it["text"], 940, 420, 76)
        s["count"] = chip(f"{s['i'] + 1} / {len(items)}", (10, 10, 18, 190), WHITE, 30)
        s["card"] = detail_card(it)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    blank = lambda im, a: im if a >= 1 else Image.blend(Image.new("RGBA", im.size, (0, 0, 0, 0)), im, max(0.0, a))
    for f in range(NF):
        t = f/FPS; s = next((x for x in segs if t < x["end"]), None)
        if s is None:
            u = t - segs[-1]["end"]; fr = segs[-1].get("bg2", segs[-1]["bg"]).copy()
            fr.alpha_composite(brand, (0, 0)); fr.alpha_composite(tag, (W - tag.width - 52, 98))
            a = ease(u/0.5); fr.alpha_composite(blank(o1, a), ((W - o1.width)//2, int(760 - 40*(1 - a))))
            fr.alpha_composite(blank(o2, ease((u - 0.3)/0.5)), ((W - o2.width)//2, 900))
            fr.alpha_composite(blank(o3, ease((u - 0.6)/0.5)), ((W - o3.width)//2, 1000))
            m = mascot("wave", (0, 0)).resize((288, 315), Image.LANCZOS); fr.alpha_composite(m, (W//2 - 144, 1180 + int(10*math.sin(t*5))))
            ff.stdin.write(fr.convert("RGB").tobytes()); continue
        it = items[s["i"]]; lt = t - s["start"]
        two = "photo2" in s and t >= s["explain"]
        fr = (s["bg2"] if two else s["bg"]).copy()
        fr.alpha_composite(brand, (0, 0)); fr.alpha_composite(tag, (W - tag.width - 52, 98))
        tin = ease(lt/0.45) if s["i"] else 1.0; dx = int((1 - tin)*120)
        zoom = min(1.0, lt/(s["end"] - s["start"]))
        card = photo_card(s["photo"], it["credit"], zoom)
        if "photo2" in s and t >= s["explain"] - 0.4:
            c2 = photo_card(s["photo2"], it["explain_credit"], (t - s["explain"])/4)
            card = Image.blend(card, c2, ease_io((t - s["explain"] + 0.4)/0.6))
        ex = ease_io((t - s["explain"])/0.5) if t >= s["explain"] else 0.0
        sc = 1 - 0.40*ex
        cimg = card if sc > 0.995 else card.resize((int(PW*sc), int(PH*sc)), Image.LANCZOS)
        cimg = blank(cimg, tin)
        cx = (W - cimg.width)//2 + dx; cy = PY
        fr.alpha_composite(cimg, (cx, cy)); fr.alpha_composite(s["count"], (cx + 28, cy + 28))
        hy = cy + cimg.height + 50
        fr.alpha_composite(blank(s["head"], tin), (70 + dx, hy)); d = ImageDraw.Draw(fr)
        bar_y = hy + s["head"].height + 26
        if s["i"] == 0 and t < 2.6:  # opening hook over the photo
            a = min(1, (2.6 - t)*2.5)
            plate = Image.new("RGBA", (PW, hook.height + 70), (0, 0, 0, 0))
            ImageDraw.Draw(plate).rounded_rectangle((0, 0, PW - 1, plate.height - 1), 0, fill=(6, 7, 14, int(185*a)))
            fr.alpha_composite(plate, ((W - PW)//2, cy + PH//2 - plate.height//2))
            fr.alpha_composite(blank(hook, a), ((W - hook.width)//2, cy + PH//2 - hook.height//2))
        if t < s["explain"]:
            u = lt/(s["explain"] - s["start"])
            d.rounded_rectangle((70, bar_y, 1010, bar_y + 8), 4, fill=(255, 255, 255, 40))
            d.rounded_rectangle((70, bar_y, 70 + max(8, int(940*u)), bar_y + 8), 4, fill=ACC)
        else:
            u = ease((t - s["explain"] - 0.15)/0.5); c = s["card"]
            fr.alpha_composite(blank(c, u), ((W - c.width)//2, int(bar_y + 10 + 80*(1 - u))))
        if s["end"] - t < 0.25 and s["i"] < len(segs) - 1:
            fr.alpha_composite(Image.new("RGBA", (W, H), (6, 7, 14, int(255*(1 - (s["end"] - t)/0.25)*0.8))))
        ff.stdin.write(fr.convert("RGB").tobytes())
    ff.stdin.close(); ff.wait()
    return segs, total

def make_audio(items, path):
    segs, total = timeline(items); sr = 44100; N = int(sr*(total + 0.5))
    m = ambient_bed(N, sr); fx = np.zeros(N); rng = np.random.default_rng(9)
    def add(sig, t):
        i = int(t*sr); n = min(len(sig), N - i)
        if n > 0 and i >= 0: fx[i:i + n] += sig[:n]
    def tt(dd): return np.arange(int(dd*sr))/sr
    def env(n, dec): return np.exp(-np.arange(n)/(sr*dec))
    def lp(x, k): return np.convolve(x, np.ones(k)/k, mode="same")
    def whoosh(t, dd=0.5, a=0.35):
        x = rng.standard_normal(int(dd*sr)); e = np.sin(np.linspace(0, np.pi, len(x)))**2; add(a*lp(x, 14)*e, t)
    def sub_hit(t, a=0.8):
        x = tt(0.9); fq = 38 + 50*np.exp(-x*10); add(a*np.sin(2*np.pi*np.cumsum(fq)/sr)*env(len(x), 0.28), t)
    def swell(t, dd=1.2):
        x = tt(dd); n = lp(rng.standard_normal(len(x)), 20); add(0.18*(x/dd)**2*n, t - dd)
    sub_hit(0.0, 0.8)
    for s in segs:
        if s["i"]: whoosh(s["start"] - 0.15, 0.5, 0.4); sub_hit(s["start"], 0.45)
        swell(s["explain"]); sub_hit(s["explain"], 0.7); whoosh(s["explain"] + 0.1, 0.45, 0.25)
    sub_hit(segs[-1]["end"], 0.6)
    g = np.full(N, 0.5); fi = int(0.3*sr); g[:fi] *= np.linspace(0, 1, fi); fo = int(1.5*sr); g[-fo:] *= np.linspace(1, 0, fo)
    out = m*g[:, None] + fx[:, None]; out = out/np.abs(out).max()*0.92
    with wave.open(path, "wb") as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes((out*32767).astype(np.int16).tobytes())

if __name__ == "__main__":
    data, out = sys.argv[1], sys.argv[2]
    mod = load(data); items = mod.ITEMS; assert 2 <= len(items) <= 3
    wav = out + ".wav"; make_audio(items, wav); segs, total = make_video(items, out, wav, getattr(mod, "HOOK", None)); os.remove(wav)
    print("total", round(total, 1), "s")
