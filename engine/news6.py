"""The Noggin Times, v6: cinematic "news you missed" Short (owner's reference: lifestyle-news reels).

Look: full-screen real photos with a slow push/pan, warm film grade, grain and vignette; big centred serif captions
that change phrase by phrase in sync with a smooth British female voiceover (tts.py: Kokoro bf_emma, offline; ed["voice"]="us" = Piper male); a
"This Week in / The Noggin Times" title card over a photo collage; an italic category collage; crossfades.
No presenter on camera (never real people's faces). Sound: voiceover + a very soft ambient pad.

Edition data = one NEWS entry from a news day file (same fields as news_sample4.py). Optional extras:
  item["vo"]  = [sentence for photo 1, sentence(s) for photo 2]   (default: [text, detail])
  brief["vo"] = "one or two short sentences"                      (default: title + ".")
  edition["vo_open"], edition["vo_outro"], edition["cats"] (4 short words for the category collage)
Write every vo line the way it should be SPOKEN and SHOWN (captions show the same words). Digits are fine
("$125", "1940s", "120 mph"); tts.py spells them out.

Usage:  python3 news6.py days/<file>.py <index> out.mp4 [--stills]
Photos: the bigger the better (ask Commons for iiurlwidth=2560); anything under ~1000 px tall looks soft full-screen.
"""
import math, os, re, subprocess, sys, importlib.util
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import tts
from news5 import calm_bed

W, H, FPS = 1080, 1920, 30
XF = 0.4                                   # crossfade
FONTS = os.path.join(HERE, "assets", "fonts")
SERIF, ITAL = os.path.join(FONTS, "texgyretermes-regular.otf"), os.path.join(FONTS, "texgyretermes-italic.otf")
def F(p, s): return ImageFont.truetype(p, s)
def ease(x): x = min(1, max(0, x)); return x*x*(3 - 2*x)

# ---------------------------------------------------------------- look
def grade(im):
    a = np.asarray(im.convert("RGB"), dtype=np.float32)/255
    lum = (a*[0.299, 0.587, 0.114]).sum(2, keepdims=True)
    a = lum + (a - lum)*0.82                                      # a little less saturated
    a = a*[1.04, 1.0, 0.93] + [0.012, 0.004, -0.004]              # warm
    a = np.clip(a, 0, 1); a = a*a*(3 - 2*a)*0.55 + a*0.45          # gentle S-curve
    a = 0.045 + a*0.91                                            # lifted blacks, soft highlights
    return Image.fromarray((np.clip(a, 0, 1)*255).astype(np.uint8))

def make_overlay():
    y, x = np.mgrid[0:H, 0:W].astype(np.float32); d = np.sqrt(((x - W/2)/(W*0.62))**2 + ((y - H*0.48)/(H*0.6))**2)
    v = np.clip((d - 0.55)/0.65, 0, 1)**1.6*0.62                  # vignette
    band = np.exp(-((y - H*0.47)/(H*0.11))**2)*0.40               # soft dark band behind the captions
    a = np.clip(v + band*(1 - v), 0, 1)
    return Image.fromarray(np.dstack([np.zeros((H, W, 3), np.uint8), (a*255).astype(np.uint8)]), "RGBA")

GRAIN = []
def grains():
    if not GRAIN:
        rng = np.random.default_rng(5)
        for _ in range(6):
            g = rng.normal(0, 1, (H//2, W//2)).astype(np.float32)
            g = np.array(Image.fromarray(((g*0.5 + 0.5).clip(0, 1)*255).astype(np.uint8)).resize((W, H), Image.BILINEAR), np.int16) - 128
            GRAIN.append(g)
    return GRAIN

class Photo:
    """A graded photo ready for a slow push-in / pan. mode: 'push' or 'pan'."""
    cache = {}
    def __init__(self, path, seed=0):
        if path not in Photo.cache:
            im = Image.open(os.path.join(HERE, path)).convert("RGB"); s = max(W*1.14/im.width, H*1.08/im.height)
            im = im.resize((round(im.width*s), round(im.height*s)), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 60, 2))
            Photo.cache[path] = grade(im)
        self.im = Photo.cache[path]; self.seed = seed
    def at(self, u):
        iw, ih = self.im.size; u = ease(u)
        z = 1.0 + 0.06*u if self.seed % 2 == 0 else 1.06 - 0.06*u
        sc = max(W/iw, H/ih)*z; cw, ch = W/sc, H/sc
        span = iw - cw; dirn = 1 if self.seed % 4 < 2 else -1
        cx = iw/2 + dirn*span*0.42*(u - 0.5)                      # slow pan across wide photos
        cy = ih/2 - (ih - ch)*0.08
        x0 = min(max(0, cx - cw/2), iw - cw); y0 = min(max(0, cy - ch/2), ih - ch)
        return self.im.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch))

def collage(paths, n=4):
    """2x2 photo collage with thin dark gutters (title card and category screen)."""
    out = Image.new("RGB", (W, H), (12, 10, 9)); g = 8; cw, ch = (W - g)//2, (H - g)//2
    for k, p in enumerate(paths[:4]):
        im = Image.open(os.path.join(HERE, p)).convert("RGB"); s = max(cw/im.width, ch/im.height)
        im = im.resize((math.ceil(im.width*s), math.ceil(im.height*s)), Image.LANCZOS)
        x0, y0 = (im.width - cw)//2, (im.height - ch)//2
        out.paste(grade(im.crop((x0, y0, x0 + cw, y0 + ch))), ((k % 2)*(cw + g), (k//2)*(ch + g)))
    return out

# ---------------------------------------------------------------- text
def text_img(txt, font, fill=(255, 252, 245), maxw=930, lh=1.08, shadow=True):
    d = ImageDraw.Draw(Image.new("L", (1, 1))); words, lines, cur = txt.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= maxw or not cur: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    asc, desc = font.getmetrics(); step = int((asc + desc)*lh); pad = 40
    wd = int(max(d.textlength(l, font=font) for l in lines)) + 2*pad; ht = step*len(lines) + 2*pad
    im = Image.new("RGBA", (wd, ht), (0, 0, 0, 0))
    if shadow:
        sh = Image.new("L", (wd, ht), 0); ds = ImageDraw.Draw(sh)
        for i, l in enumerate(lines): ds.text((wd/2, pad + i*step + 3), l, font=font, fill=200, anchor="ma")
        sh = sh.filter(ImageFilter.GaussianBlur(9)); im.putalpha(sh)
        im = Image.composite(Image.new("RGBA", (wd, ht), (0, 0, 0, 255)), Image.new("RGBA", (wd, ht), (0, 0, 0, 0)), sh)
    dt = ImageDraw.Draw(im)
    for i, l in enumerate(lines): dt.text((wd/2, pad + i*step), l, font=font, fill=fill + (255,), anchor="ma")
    return im

def put(base, im, cx, cy, alpha=1.0, dy=0):
    if alpha <= 0: return
    if alpha < 1: im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v*alpha)))
    base.alpha_composite(im, (int(cx - im.width/2), int(cy - im.height/2 + dy)))

SMALL = set("a an the to of for in on at by with and or but his her its their my your our one two three four five six seven eight nine ten is was are it that this".split())
def phrases(sentence):
    """Split a spoken sentence into caption phrases (<= 5 words, break after punctuation) with phoneme weights."""
    words = sentence.split(); out, cur = [], []
    for w in words:
        cur.append(w)
        weak = w.lower() in SMALL
        if re.search(r"[,.!?;:]$", w) or (not weak and (len(cur) >= 5 or (len(" ".join(cur)) > 24 and len(cur) >= 3))) or len(cur) >= 7:
            out.append(cur); cur = []
    if cur:
        if out and len(cur) == 1: out[-1] += cur
        else: out.append(cur)
    res = []
    for ph in out:
        wgt = 0
        for w in ph:
            try: wgt += sum(len(i) for _, i in tts.words_to_ipa(w)) + (6 if re.search(r"[,.!?;:]$", w) else 0)
            except KeyError: wgt += len(w)
        res.append((" ".join(ph), wgt))
    return res

# ---------------------------------------------------------------- build
def build(ed, NB=2):
    items = ed["items"]; briefs = [b for page in ed["briefs"] for b in page]
    pick, seen = [], set()
    for b in briefs:                                     # up to 3 briefs, different categories first
        if b["cat"] not in seen and len(pick) < NB: pick.append(b); seen.add(b["cat"])
    for b in briefs:
        if len(pick) < NB and b not in pick: pick.append(b)
    first = items[0]; spare = [b for b in briefs if b not in pick]
    op = ed.get("open_photo") or (spare[0]["photo"] if spare else first.get("explain_photo") or first["photo"])
    opc = ed.get("open_credit") or (spare[0]["credit"] if spare else first.get("explain_credit") or first["credit"])
    shots = []   # dict(kind, photo(s), vo=[sentences], label, credit)
    shots.append(dict(kind="photo", photo=op, vo=[ed.get("vo_open", "Here's the news you missed this week.")], credit=opc))
    shots.append(dict(kind="title", photos=[it["photo"] for it in items] + [pick[0]["photo"]], vo=["This week in the Noggin Times."]))
    cats = ed.get("cats") or ["Weird", "Space", "Drops", "Sport"]
    shots.append(dict(kind="cats", photos=([b["photo"] for b in pick] + [b["photo"] for b in spare[1:]] + [it["photo"] for it in items])[:4], cats=cats, vo=[]))
    for k, it in enumerate(items):
        vo = it.get("vo") or [it["text"], it["detail"]]
        shots.append(dict(kind="photo", photo=it["photo"], vo=[vo[0]], credit=it["credit"], src=it["source"]["outlet"]))
        if len(vo) > 1:
            shots.append(dict(kind="photo", photo=it.get("explain_photo") or it["photo"], vo=vo[1:], credit=it.get("explain_credit") or it["credit"], src=it["source"]["outlet"]))
    for b in pick:
        shots.append(dict(kind="photo", photo=b["photo"], vo=[b.get("vo") or b["title"] + "."], label=b["cat"], credit=b["credit"], src=b["source"]["outlet"]))
    shots.append(dict(kind="outro", photos=[it["photo"] for it in items] + [pick[-1]["photo"]], vo=[ed.get("vo_outro", "That's the news. Follow so you don't miss next week.")]))
    # ---- voice
    sr = 22050; t = 0.0; voice = []; caps = []
    for i, s in enumerate(shots):
        s["t0"] = t; tt = t + (0.3 if i else 0.2)
        if s["kind"] == "cats": tt += 1.9
        for sent in s["vo"]:
            a, sr, _ = tts.say_gb(sent) if ed.get("voice", "gb") == "gb" else tts.say(sent, seed=i)
            d = len(a)/sr; voice.append((tt, a))
            ph = phrases(sent); tot = sum(w for _, w in ph); c = tt
            for txt, w in ph:
                if s["kind"] == "photo": caps.append((c, c + d*w/tot, txt))
                c += d*w/tot
            tt += d + 0.22
        s["t1"] = t = tt + 0.2
    dur = t + 0.6
    if dur > 59: raise SystemExit(f"too long for a Short: {dur:.1f} s (shorten the vo lines or use fewer briefs)")
    return shots, caps, voice, sr, dur

def render(ed, out, stills=False):
    shots, caps, voice, sr, dur = build(ed)
    over = make_overlay(); G = grains(); capf = F(SERIF, 82); labf = F(ITAL, 64); smallf = F(SERIF, 26)
    titleA, titleB = F(ITAL, 70), F(SERIF, 168)
    for s in shots:
        if s["kind"] == "photo": s["P"] = Photo(s["photo"], seed=shots.index(s))
        else: s["C"] = grade(collage(s["photos"])) if s["kind"] != "cats" else collage(s["photos"])
    capims = {}
    def capim(txt):
        if txt not in capims: capims[txt] = text_img(txt, capf)
        return capims[txt]
    def shot_frame(s, t):
        u = (t - s["t0"])/max(0.1, s["t1"] - s["t0"] + XF)
        if s["kind"] == "photo": return s["P"].at(u).convert("RGBA")
        z = 1.0 + 0.04*ease(u); im = s["C"]; cw, ch = W/z, H/z
        im = im.resize((W, H), Image.BILINEAR, box=((W - cw)/2, (H - ch)/2, (W + cw)/2, (H + ch)/2)).convert("RGBA")
        if s["kind"] in ("title", "outro"): im.alpha_composite(Image.new("RGBA", (W, H), (8, 6, 5, 120)))
        return im
    def frame(t):
        k = max(i for i, s in enumerate(shots) if s["t0"] <= t or i == 0); s = shots[k]
        im = shot_frame(s, t)
        if k + 1 < len(shots) and t > s["t1"] - XF:              # crossfade into the next shot
            a = ease((t - (s["t1"] - XF))/XF); im = Image.blend(im, shot_frame(shots[k + 1], t), a)
            if a > 0.5: s = shots[k + 1]
        im.alpha_composite(over)
        lt = t - s["t0"]
        if s["kind"] == "title":
            a = ease((lt - 0.2)/0.6); put(im, text_img("This Week in", titleA), W/2, H*0.36, a, dy=12*(1 - a))
            b = ease((lt - 0.5)/0.7); put(im, text_img("The Noggin Times", titleB, maxw=900, lh=0.98), W/2, H*0.47, b, dy=18*(1 - b))
        elif s["kind"] == "cats":
            pos = [(W*0.30, H*0.30), (W*0.66, H*0.42), (W*0.28, H*0.54), (W*0.66, H*0.66)]
            for j, c in enumerate(s["cats"][:4]):
                a = ease((lt - 0.15 - j*0.45)/0.45); put(im, text_img(c, labf), pos[j][0], pos[j][1], a, dy=10*(1 - a))
        elif s["kind"] == "outro":
            a = ease((lt - 0.3)/0.6); put(im, text_img("The Noggin Times", F(SERIF, 120), maxw=900, lh=0.98), W/2, H*0.40, a)
            b = ease((lt - 1.0)/0.6); put(im, text_img("New edition every week", F(ITAL, 54)), W/2, H*0.53, b)
        if s["kind"] == "photo":
            fa = min(ease(lt/0.5), ease((s["t1"] - t)/0.4))
            if s.get("label"): put(im, text_img(s["label"], labf), W/2, H*0.30, fa*ease((lt - 0.1)/0.4))
            line = ("Source: " + s["src"] + "   |   " if s.get("src") else "") + "Photo: " + s["credit"]
            put(im, text_img(line, smallf, fill=(235, 230, 220), maxw=980, shadow=True), W/2, H*0.735, 0.75*fa)
        for c0, c1, txt in caps:                                  # spoken caption, phrase by phrase
            if c0 <= t < c1 + 0.02:
                a = ease((t - c0)/0.12); put(im, capim(txt), W/2, H*0.47, a, dy=6*(1 - a)); break
        rgb = np.asarray(im.convert("RGB"), np.int16) + (G[int(t*FPS) % len(G)][..., None]*0.085).astype(np.int16)
        return Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8))
    # ---- check sheet
    marks = [(s["t0"] + s["t1"])/2 for s in shots]
    sheet = Image.new("RGB", (270*6, 480*math.ceil(len(marks)/6)))
    for i, tm in enumerate(marks): sheet.paste(frame(tm).resize((270, 480)), ((i % 6)*270, (i//6)*480))
    sp = "/tmp/news6_check_" + os.path.basename(os.path.dirname(os.path.abspath(out))) + ".jpg"; sheet.save(sp, quality=85)
    print("shots", len(shots), "duration", round(dur, 1), "check", sp)
    if stills: return dur
    # ---- audio
    N = int(sr*(dur + 0.5)); vo = np.zeros(N, np.float32)
    for t0, a in voice: i = int(t0*sr); vo[i:i + len(a)] += a[:N - i]
    bed = calm_bed(int(44100*(dur + 0.5)), 44100)[:, 0]
    bed = np.interp(np.arange(N)/sr, np.arange(len(bed))/44100, bed).astype(np.float32)
    fade = np.clip(np.arange(N)/sr/1.0, 0, 1)*np.clip((dur + 0.3 - np.arange(N)/sr)/1.2, 0, 1)
    mix = vo*0.95 + bed*0.07*fade
    mix = (np.clip(mix, -1, 1)*32767).astype(np.int16)
    wav = out.replace(".mp4", ".wav")
    import wave
    with wave.open(wav, "wb") as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(mix.tobytes())
    tmp = out.replace(".mp4", ".tmp.mp4")
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-maxrate", "8M", "-bufsize", "16M", "-pix_fmt", "yuv420p",
                          "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-shortest", "-movflags", "+faststart", tmp], stdin=subprocess.PIPE)
    for i in range(int(dur*FPS)): p.stdin.write(frame(i/FPS).tobytes())
    p.stdin.close(); p.wait(); os.remove(wav)
    if p.returncode: raise SystemExit("ffmpeg failed")
    os.replace(tmp, out); print("done", out, round(dur, 1), "s"); return dur

if __name__ == "__main__":
    path, idx, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    spec = importlib.util.spec_from_file_location("day", path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    render(m.NEWS[idx], out, "--stills" in sys.argv)
