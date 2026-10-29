"""YouTube Short for The Noggin Times, v5: the same 8 (or 10) carousel slides, animated as a newspaper you flip through.

Every slide is different (cover, story, by-the-numbers, story, by-the-numbers, In Brief grid, In Brief rows, comment+follow),
so nothing on screen repeats. Each slide holds long enough to read (by slide type), with a slow push-in, paper grain flicker,
and a page-turn into the next one. Sound: a soft, calm pad (no drone, no sub pulse, no high whine) + paper rustle on every turn + stamp thud on the cover.

Usage (normally called by make_news.py):  news5.make_video(tt_slide_paths, out_mp4, kinds)
kinds = list like ["cover","story","numbers","story","numbers","brief","brief","outro"] (decides how long each slide stays).
"""
import math, os, random, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageEnhance
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from news2 import ease_io
import news4

W, H, FPS = 1080, 1920, 30
TURN = 0.5
HOLD = {"cover": 3.6, "story": 4.6, "numbers": 7.0, "brief": 6.5, "outro": 3.6}


def calm_bed(N, sr, seed=11):
    """Calm, warm pad for the news Shorts: slow chord swells (C - Am - F - G), gently low-passed, no beating drone,
    no sub pulse and no high shimmer (those made the old bed tiring). Very soft room-tone air underneath."""
    rng = np.random.default_rng(seed); x = np.arange(N)/sr
    def lp(v, k): return np.convolve(v, np.ones(k)/k, mode="same")
    chords = [(130.81, 164.81, 196.00, 246.94), (110.00, 130.81, 164.81, 196.00),
              (87.31, 130.81, 174.61, 220.00), (98.00, 123.47, 146.83, 196.00)]
    CH = 8.0; out = np.zeros(N)
    for k in range(int(N/sr/CH) + 2):
        t0 = k*CH - 2.0; i0 = max(0, int(t0*sr)); i1 = min(N, int((t0 + CH + 4.0)*sr))
        if i1 <= i0: continue
        xx = x[i0:i1]; u = (xx - t0)/(CH + 4.0)
        env = np.sin(np.pi*np.clip(u, 0, 1))**2                       # slow swell in and out, overlapping the next chord
        for j, f in enumerate(chords[k % 4]):
            a = 0.22/(1 + j*0.35)
            out[i0:i1] += env*a*(np.sin(2*np.pi*f*xx + j) + 0.25*np.sin(2*np.pi*2*f*xx + j)*0.5)
    out = lp(lp(out, 6), 6)                                            # soften the top end
    air = lp(rng.standard_normal(N), 120); air = (air - lp(air, 2000))*0.6
    L = out + air*0.08; R = np.roll(out, 220) + np.roll(air, 331)*0.08
    st = np.stack([L, R], 1); return st/np.abs(st).max()*0.8


def timeline(kinds):
    t, segs = 0.0, []
    for k in kinds:
        d = HOLD.get(k, 5.0); segs.append((t, t + d)); t += d
    return segs, t

def make_audio(kinds, path):
    segs, total = timeline(kinds); sr = 44100; N = int(sr*(total + 0.5))
    m = calm_bed(N, sr); fx = np.zeros(N); rng = np.random.default_rng(21)
    def add(sig, t):
        i = int(t*sr); n = min(len(sig), N - i)
        if n > 0 and i >= 0: fx[i:i + n] += sig[:n]
    def lp(x, k): return np.convolve(x, np.ones(k)/k, mode="same")
    def rustle(t, dd=0.55, a=0.35):
        x = rng.standard_normal(int(dd*sr)); bp = lp(x, 3) - lp(x, 25); e = np.sin(np.linspace(0, np.pi, len(x)))**1.5
        cr = (rng.random(len(x)) < 0.004)*rng.standard_normal(len(x))*3; add(a*(bp*e + lp(cr, 2)*e), t)
    def thud(t, a=0.9):
        x = np.arange(int(0.35*sr))/sr; add(a*np.sin(2*np.pi*(70 + 60*np.exp(-x*30))*x)*np.exp(-x/0.07), t)
        n = rng.standard_normal(int(0.05*sr)); add(0.35*lp(n, 6)*np.exp(-np.arange(len(n))/(sr*0.012)), t)
    thud(0.15)
    for a, b in segs[1:]: rustle(a - 0.08)
    g = np.full(N, 0.40); fi = int(1.0*sr); g[:fi] *= np.linspace(0, 1, fi); fo = int(1.2*sr); g[-fo:] *= np.linspace(1, 0, fo)
    out = m*g[:, None] + fx[:, None]; out = out/np.abs(out).max()*0.80
    with wave.open(path, "wb") as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes((out*32767).astype(np.int16).tobytes())
    return total

def make_video(slide_paths, out, kinds):
    assert len(slide_paths) == len(kinds)
    slides = [Image.open(p).convert("RGB").resize((W, H), Image.LANCZOS) for p in slide_paths]
    segs, total = timeline(kinds); NF = int(round(total*FPS))
    wav = out + ".wav"; make_audio(kinds, wav)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-maxrate", "6M", "-bufsize", "12M", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    news4.H = H; grains = news4.grain_layers(); rj = random.Random(4); jit = (0, 0)
    shade = np.zeros((H, 70, 4), np.uint8); shade[..., 3] = np.linspace(120, 0, 70)[None, :].astype(np.uint8)
    shade = Image.fromarray(shade, "RGBA")
    def page(i, t):
        a, b = segs[i]; u = (t - a)/(b - a)
        z = 1.0 + 0.035*u                                   # slow push-in
        w, h = int(W*z), int(H*z); im = slides[i].resize((w, h), Image.BILINEAR)
        ox, oy = (w - W)//2, int((h - H)*(0.35 + 0.3*u))    # drift down while reading
        return im.crop((ox, oy, ox + W, oy + H))
    for f in range(NF):
        t = f/FPS; i = next(k for k, (a, b) in enumerate(segs) if t < b or k == len(segs) - 1)
        fr = page(i, t)
        a = segs[i][0]
        if i > 0 and t < a + TURN:                          # page turn: new page slides over the old one
            u = ease_io((t - a)/TURN); old = page(i - 1, a - 1/FPS)
            old = ImageEnhance.Brightness(old).enhance(1 - 0.35*u)
            x = int(W*(1 - u)); base = old.copy()
            if x < W: base.paste(fr.crop((0, 0, W - x, H)), (x, 0))
            if 0 < x < W: base.paste(shade, (max(0, x - 70), 0), shade)
            fr = base
        if i == 0 and t < 0.35:                             # cover lands like a stamp
            s = 1.06 - 0.06*ease_io(t/0.35); big = fr.resize((int(W*s), int(H*s)), Image.BILINEAR)
            fr = big.crop(((big.width - W)//2, (big.height - H)//2, (big.width - W)//2 + W, (big.height - H)//2 + H))
        fr = fr.convert("RGBA"); fr.alpha_composite(grains[(f//6) % len(grains)])
        if f % 6 == 0: jit = (rj.randint(-1, 1), rj.randint(-1, 1))
        out_fr = Image.new("RGB", (W, H), news4.PAPER); out_fr.paste(fr.convert("RGB"), jit)
        if f % 5 == 0: out_fr = ImageEnhance.Brightness(out_fr).enhance(1 + rj.uniform(-0.012, 0.012))
        ff.stdin.write(out_fr.tobytes())
    ff.stdin.close(); ff.wait(); os.remove(wav)
    return segs, total

def kinds_for(n_items, n_brief_slides):
    return ["cover"] + ["story", "numbers"]*n_items + ["brief"]*n_brief_slides + ["outro"]

if __name__ == "__main__":
    import glob
    d, out = sys.argv[1], sys.argv[2]; n_items = int(sys.argv[3]) if len(sys.argv) > 3 else 2
    ps = sorted(glob.glob(os.path.join(d, "tt_*.jpg")))
    segs, total = make_video(ps, out, kinds_for(n_items, len(ps) - 2 - 2*n_items))
    print("total", round(total, 1), "s")
