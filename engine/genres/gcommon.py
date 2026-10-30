"""Shared toolkit for the Noggin long-video samples: fonts, emoji, text, easing, sound effects, video writer."""
import sys, math, wave, subprocess, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
ENGINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ENGINE)
from mascot import mascot  # noqa

W, H, FPS = 1920, 1080, 30
def set_size(w, h):
    global W, H
    W, H = w, h
FD = os.path.join(ENGINE, "assets", "fonts") + "/"
BLACK, XB, EMOJI_F = FD + "Inter-Black.otf", FD + "Inter-ExtraBold.otf", FD + "NotoColorEmoji.ttf"
INK = (24, 12, 32); WHITE = (255, 255, 255); YEL = (255, 220, 92); RED = (255, 92, 92); GRN = (122, 220, 120); BLU = (110, 150, 255)

_fc = {}
def font(p, s):
    if (p, s) not in _fc: _fc[(p, s)] = ImageFont.truetype(p, s)
    return _fc[(p, s)]

_ec = {}
def emoji(e, size):
    k = (e, size)
    if k not in _ec:
        im = Image.new("RGBA", (200, 160), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((10, 10), e, font=font(EMOJI_F, 109), embedded_color=True)
        bb = im.getbbox(); im = im.crop(bb) if bb else im; s = size/max(im.size)
        _ec[k] = im.resize((max(1, int(im.width*s)), max(1, int(im.height*s))), Image.LANCZOS)
    return _ec[k]

def flag(iso2): return "".join(chr(0x1F1E6 + ord(c) - 65) for c in iso2.upper())

_bc = {}
def ball(e, r, ring=(10, 10, 20), bg=(245, 240, 255), full=True):
    """Round sprite: a flag fills the ball; other emoji sit on a pastel disc."""
    k = (e, r, ring, bg, full)
    if k in _bc: return _bc[k]
    S = 3; D = 2*r*S; base = Image.new("RGBA", (D, D), (0, 0, 0, 0))
    mask = Image.new("L", (D, D), 0); ImageDraw.Draw(mask).ellipse((0, 0, D - 1, D - 1), fill=255)
    em = emoji(e, 140)
    fill = Image.new("RGBA", (D, D), bg + (255,))
    if full:
        w, h = em.size; em2 = em.crop((int(w*0.06), int(h*0.1), int(w*0.94), int(h*0.9)))
        sc = D/min(em2.size); em2 = em2.resize((max(D, int(em2.width*sc)), max(D, int(em2.height*sc))), Image.LANCZOS)
        x0 = (em2.width - D)//2; y0 = (em2.height - D)//2; fill.alpha_composite(em2.crop((x0, y0, x0 + D, y0 + D)))
    else:
        s = int(D*0.68); sc = s/max(em.size); em2 = em.resize((max(1, int(em.width*sc)), max(1, int(em.height*sc))), Image.LANCZOS)
        fill.alpha_composite(em2, ((D - em2.width)//2, (D - em2.height)//2))
    base.paste(fill, (0, 0), mask)
    hl = Image.new("L", (D, D), 0); ImageDraw.Draw(hl).ellipse((D*0.18, D*0.08, D*0.55, D*0.36), fill=110)
    hl = hl.filter(ImageFilter.GaussianBlur(D*0.05)); wh = Image.new("RGBA", (D, D), (255, 255, 255, 0)); wh.putalpha(hl); base.alpha_composite(wh)
    sh = Image.new("L", (D, D), 0); ImageDraw.Draw(sh).ellipse((0, 0, D - 1, D - 1), fill=255)
    inner = Image.new("L", (D, D), 0); ImageDraw.Draw(inner).ellipse((D*0.06, D*0.03, D*0.97, D*0.9), fill=255); inner = inner.filter(ImageFilter.GaussianBlur(D*0.05))
    dark = Image.new("RGBA", (D, D), (0, 0, 0, 0)); dark.putalpha(Image.eval(Image.composite(Image.new("L", (D, D), 0), sh, inner), lambda v: int(v*0.4))); base.alpha_composite(dark)
    ImageDraw.Draw(base).ellipse((S, S, D - 1 - S, D - 1 - S), outline=ring + (255,), width=3*S)
    out = Image.new("RGBA", (D, D), (0, 0, 0, 0)); out.paste(base, (0, 0), mask)
    _bc[k] = out.resize((2*r, 2*r), Image.LANCZOS); return _bc[k]

_tc = {}
def T(txt, size, fill=WHITE, stroke=10, path=BLACK, sc=INK, maxw=1800):
    while size > 20 and font(path, size).getlength(txt) + 2*stroke > maxw: size -= 2
    k = (txt, size, fill, stroke, path, sc)
    if k not in _tc:
        f = font(path, size); bb = f.getbbox(txt, stroke_width=stroke)
        im = Image.new("RGBA", (bb[2] - bb[0] + 8, bb[3] - bb[1] + 8), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((4 - bb[0], 4 - bb[1]), txt, font=f, fill=fill, stroke_width=stroke, stroke_fill=sc)
        _tc[k] = im
    return _tc[k]

def paste(base, im, cx, cy, scale=1.0, rot=0, alpha=1.0, anchor="c"):
    if scale <= 0.01 or alpha <= 0.01: return
    if scale != 1.0: im = im.resize((max(1, int(im.width*scale)), max(1, int(im.height*scale))), Image.BILINEAR)
    if rot: im = im.rotate(rot, Image.BICUBIC, expand=True)
    if alpha < 1: im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v*alpha)))
    x = cx - im.width/2 if anchor == "c" else cx if anchor == "l" else cx - im.width
    base.alpha_composite(im, (int(x), int(cy - im.height/2)))

def ease(x): x = min(1, max(0, x)); return 1 - (1 - x)**3
def back(x):
    x = min(1, max(0, x)); c = 1.9; return 1 + (c + 1)*(x - 1)**3 + c*(x - 1)**2

def gradient(top, bot):
    y = np.linspace(0, 1, H)[:, None, None]
    return Image.fromarray(((np.array(top)*(1 - y) + np.array(bot)*y).repeat(W, 1)).astype(np.uint8), "RGB").convert("RGBA")

def stripes(alpha=9):
    im = Image.new("RGBA", (W + 400, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for x in range(-H, W + 400, 90): d.polygon([(x, H), (x + 40, H), (x + 40 + H, 0), (x + H, 0)], fill=(255, 255, 255, alpha))
    return im

def put_mascot(im, t, pose="idle", look=(0, -1), x=1790, y=950, s=0.8):
    """Noggin in a corner, bobbing."""
    m = mascot(pose, look, (t % 3.1) < 0.12); paste(im, m, x, y + 8*math.sin(t*4.5), s*(1 + 0.03*math.sin(t*7)))

def camera(im, z=1.0, dx=0.0, dy=0.0, flash=0.0, fade_out=None, t=None, dur=None):
    if z > 1.0005 or abs(dx) > 0.5 or abs(dy) > 0.5:
        cw, ch = W/z, H/z; x0 = (W - cw)/2 - dx; y0 = (H - ch)/2 - dy
        im = im.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((W, H), Image.BILINEAR)
    if flash > 0: im = Image.blend(im, Image.new("RGBA", (W, H), (255, 255, 255, 255)), min(1, flash))
    if t is not None and dur and t > dur - 0.4: im = Image.blend(im, Image.new("RGBA", (W, H), (0, 0, 0, 255)), (t - (dur - 0.4))/0.4)
    return im

class Kicks:
    """Screen shake / punch zoom / flash driven by a list of (time, strength)."""
    def __init__(self): self.ev = []
    def add(self, t, s=1.0, flash=False): self.ev.append((t, s, flash))
    def shake(self, t):
        a = 0
        for tt, s, _ in self.ev:
            if 0 <= t - tt < 0.35: a = max(a, 16*s*(1 - (t - tt)/0.35))
        return math.sin(t*93)*a, math.cos(t*71)*a
    def zoom(self, t):
        z = 1.0
        for tt, s, _ in self.ev:
            if 0 <= t - tt < 0.3: z = max(z, 1 + 0.04*s*(1 - (t - tt)/0.3))
        return z
    def flash(self, t):
        f = 0
        for tt, s, fl in self.ev:
            if fl and 0 <= t - tt < 0.18: f = max(f, 0.5*(1 - (t - tt)/0.18))
        return f

# ------------------------------------------------------------------ sound
SR = 44100
class Mix:
    def __init__(self, dur, bed=0.22, seed=1):
        self.N = int(SR*dur); self.out = np.zeros(self.N); self.rr = np.random.default_rng(seed)
        if bed:
            x = np.arange(self.N)/SR
            b = np.convolve(self.rr.normal(0, 1, self.N), np.ones(400)/400, "same")*0.9 + 0.05*np.sin(2*np.pi*55*x)*(0.6 + 0.4*np.sin(2*np.pi*0.13*x))
            self.out += b*bed
    def add(self, sig, t, g=1.0):
        i = int(t*SR); m = min(len(sig), self.N - i)
        if m > 0 and i >= 0: self.out[i:i + m] += sig[:m]*g
    def _env(self, d, att, dec):
        y = np.arange(int(d*SR))/SR; return (1 - np.exp(-y/att))*np.exp(-y/dec), y
    def whoosh(self, d=0.35):
        e, y = self._env(d, 0.12, 0.12); n = self.rr.normal(0, 1, len(y)); return 0.5*np.convolve(n, np.ones(6)/6, "same")*e
    def thud(self, f0=90):
        e, y = self._env(0.35, 0.002, 0.08); return 0.9*np.sin(2*np.pi*np.cumsum(f0 + 120*np.exp(-y*30))/SR)*e
    def pop(self, f0=500):
        e, y = self._env(0.2, 0.001, 0.05); return 0.5*np.sin(2*np.pi*np.cumsum(f0 + 600*np.exp(-y*25))/SR)*e
    def ding(self, f=1318.5, d=1.0):
        e, y = self._env(d, 0.002, 0.35); return 0.28*(np.sin(2*np.pi*f*y) + 0.4*np.sin(2*np.pi*2*f*y))*e
    def pluck(self, f, a=0.25, d=0.35):
        e, y = self._env(d, 0.001, 0.09); return a*(np.sin(2*np.pi*f*y) + 0.3*np.sin(4*np.pi*f*y))*e
    def tick(self, f=1800):
        e, y = self._env(0.05, 0.0005, 0.012); return 0.35*np.sin(2*np.pi*f*y)*e
    def buzzer(self):
        e, y = self._env(0.5, 0.005, 0.25); return 0.3*np.sign(np.sin(2*np.pi*110*y))*e
    def boom(self):
        e, y = self._env(0.9, 0.002, 0.3); return 0.9*np.sin(2*np.pi*np.cumsum(60 + 80*np.exp(-y*12))/SR)*e + 0.2*self.rr.normal(0, 1, len(y))*np.exp(-y/0.05)
    def riser(self, d):
        y = np.arange(int(d*SR))/SR; return 0.18*np.sin(2*np.pi*np.cumsum(300 + 900*(y/d)**2)/SR)*(y/d)
    def fanfare(self, t):
        for k, f in enumerate([523.25, 659.25, 783.99, 1046.5]): self.add(self.pluck(f, 0.32, 1.3), t + k*0.12)
    def save(self, path):
        g = np.ones(self.N); fo = int(0.4*SR); g[-fo:] = np.linspace(1, 0, fo); o = self.out*g
        o = o/max(1e-9, np.abs(o).max())*0.85; st = np.stack([o, o], 1)
        with wave.open(path, "wb") as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st*32767).astype(np.int16).tobytes())

NOTES = [261.63, 293.66, 329.63, 392.0, 440.0, 523.25, 587.33, 659.25, 783.99, 880.0, 1046.5, 1174.66, 1318.5]

def render(frame_fn, dur, wav, out, stills=None):
    if stills:
        for t in stills: frame_fn(t).convert("RGB").save(out.replace(".mp4", f"_still_{t:05.1f}.jpg"), quality=85)
        return
    tmp = out.replace(".mp4", ".tmp.mp4")
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-i", wav, "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
                          "-c:a", "aac", "-b:a", "160k", "-shortest", tmp], stdin=subprocess.PIPE)
    for i in range(int(dur*FPS)): p.stdin.write(frame_fn(i/FPS).convert("RGB").tobytes())
    p.stdin.close(); p.wait()
    if p.returncode == 0:
        import os; os.replace(tmp, out)
    print(out, "exit", p.returncode)

def sheet(paths, out, cols=2):
    ims = [Image.open(p).resize((960, 540)) for p in paths]; rows = (len(ims) + cols - 1)//cols
    s = Image.new("RGB", (960*cols, 540*rows)); [s.paste(im, ((i % cols)*960, (i//cols)*540)) for i, im in enumerate(ims)]; s.save(out, quality=80)
