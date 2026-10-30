"""Satisfying bounce: every bounce the ball grows and draws a line between bounce points, until it fills the circle.
spec: {"hook": ["EVERY BOUNCE IT GETS BIGGER", "WAIT FOR THE END"], "hue_step": 0.037, "speed": 620, "gravity": 980,
       "start": [60, -120], "palette": "rainbow"|"fire"|"ice"|"neon", "end_text": "IT FILLED THE CIRCLE"}
Every run with a different start/speed/gravity gives a different pattern.
"""
import math, colorsys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import gcommon as g
from mascot import mascot

PALS = {"rainbow": (0.0, 1.0), "fire": (0.0, 0.14), "ice": (0.5, 0.68), "neon": (0.78, 1.05)}

def build(spec, fmt):
    W, H = g.W, g.H; vert = fmt == "short"
    CX, CY, R = (W/2, 980, 470) if vert else (960, 560, 430)
    speed, grav = spec.get("speed", 620), spec.get("gravity", 980); sx, sy = spec.get("start", [60, -120])
    h0, h1 = PALS.get(spec.get("palette", "rainbow"), (0, 1)); hs = spec.get("hue_step", 0.037)
    lo, hi = (17.0, 19.5) if vert else (28.0, 34.0)

    def simulate(gr, r0=28, sub=8, max_t=60):
        dt = 1/(g.FPS*sub); p = np.array([CX + sx, CY + sy], float); v = np.array([speed*0.55, 0.0]); r = r0; t = 0.0; fr = []; hits = []
        while t < max_t:
            for _ in range(sub):
                t += dt; v[1] += grav*dt; p += v*dt; d = p - (CX, CY); dist = math.hypot(*d)
                if dist > R - r:
                    n = d/dist; vn = v @ n
                    if vn > 0:
                        v -= 2*vn*n; s = math.hypot(*v); v *= max(s, speed)/s; hits.append((t, (CX + n[0]*R, CY + n[1]*R), r)); r = min(R, r + gr)
                    p = (CX, CY) + n*(R - r)
            fr.append((p.copy(), r))
            if r >= R - 2: return fr, hits, t
        return None
    res = None
    for gr in np.arange(2.0, 14.0, 0.1):
        res = simulate(gr)
        if res and lo < res[2] < hi: break
        res = None
    if not res: raise SystemExit("no growth rate gives the target length; change speed/gravity/start")
    FR, HITS, END = res; T0 = 2.0; DUR = T0 + END + 3.6
    K = g.Kicks(); K.add(0.1, 0.8); K.add(T0 + END, 1.6, True)
    for k, (t, pt, r) in enumerate(HITS):
        if k % 5 == 0: K.add(T0 + t, 0.25)
    BG = g.gradient((10, 10, 26), (34, 12, 46))
    def hue(k):
        hh = h0 + ((k*hs) % 1.0)*(h1 - h0) if spec.get("palette", "rainbow") != "rainbow" else (k*hs) % 1
        return tuple(int(c*255) for c in colorsys.hsv_to_rgb(hh % 1, 0.75, 1.0))
    hook1, hook2 = spec.get("hook", ["EVERY BOUNCE IT GETS BIGGER", "WAIT FOR THE END"]); end_text = spec.get("end_text", "IT FILLED THE CIRCLE")

    def ball_img(r, k):
        D = int(2*r + 40); im = Image.new("RGBA", (D, D), (0, 0, 0, 0)); c = D/2; col = hue(k)
        gl = Image.new("RGBA", (D, D), (0, 0, 0, 0)); ImageDraw.Draw(gl).ellipse((4, 4, D - 4, D - 4), fill=col + (90,)); im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(10)))
        ImageDraw.Draw(im).ellipse((c - r, c - r, c + r, c + r), fill=col + (255,), outline=(255, 255, 255), width=max(3, int(r*0.06)))
        return im

    def frame(t):
        im = BG.copy(); d = ImageDraw.Draw(im); st = t - T0
        fi = max(0, min(len(FR) - 1, int(st*g.FPS))); (p, r) = FR[fi] if st >= 0 else FR[0]
        nh = sum(1 for h in HITS if h[0] <= st)
        d.ellipse((CX - R - 14, CY - R - 14, CX + R + 14, CY + R + 14), fill=(255, 255, 255, 255)); d.ellipse((CX - R, CY - R, CX + R, CY + R), fill=(8, 8, 20, 255))
        lines = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lines)
        for k in range(1, nh): ld.line((HITS[k - 1][1], HITS[k][1]), fill=hue(k) + (190,), width=4)
        im.alpha_composite(lines)
        if nh and st - HITS[nh - 1][0] < 0.25:
            x, y = HITS[nh - 1][1]; rr = 10 + 60*(st - HITS[nh - 1][0]); d.ellipse((x - rr, y - rr, x + rr, y + rr), outline=hue(nh - 1) + (255,), width=5)
        if st < END + 0.05:
            b = ball_img(r, nh); im.alpha_composite(b, (int(p[0] - b.width/2), int(p[1] - b.height/2)))
            g.paste(im, mascot("shock" if r > R*0.75 else "idle", (0, 0), (t % 2.7) < 0.1), p[0], p[1] + r*0.05, r*1.7/350)
        if st < END:
            pct = int(100*(r/R)) if st >= 0 else 0; pop = 1 + 0.2*max(0, 1 - (st - HITS[nh - 1][0])/0.15) if nh else 1
            if not vert:
                g.paste(im, g.T("BOUNCES", 46, g.WHITE, 6), 230, 420); g.paste(im, g.T(str(nh), 140, g.YEL, 12), 230, 530, pop)
                g.paste(im, g.T("SIZE", 46, g.WHITE, 6), 1690, 420); g.paste(im, g.T(f"{pct}%", 130, g.GRN if pct < 75 else g.RED, 12), 1690, 530)
            else:
                g.paste(im, g.T("BOUNCES", 44, g.WHITE, 6), 270, 250); g.paste(im, g.T(str(nh), 130, g.YEL, 12), 270, 360, pop)
                g.paste(im, g.T("SIZE", 44, g.WHITE, 6), 810, 250); g.paste(im, g.T(f"{pct}%", 120, g.GRN if pct < 75 else g.RED, 12), 810, 360)
            if 0.75 < r/R < 0.995: g.paste(im, g.T("ALMOST...", 90, g.RED, 10), CX, CY + R + 90 if vert else 1040, 1 + 0.06*math.sin(t*14))
        if t < T0 + 0.3:
            a = 1 - g.ease((t - T0)/0.3); im.alpha_composite(Image.new("RGBA", (W, H), (8, 6, 20, int(170*a))))
            g.paste(im, g.T(hook1, 110, g.WHITE, 12, maxw=W - 80), W/2, H/2 - 120, g.back((t - 0.1)/0.25), alpha=a)
            g.paste(im, g.T(hook2, 130, g.YEL, 12, maxw=W - 80), W/2, H/2 + 40, g.back((t - 0.8)/0.25), rot=-3, alpha=a)
        if st >= END:
            k = st - END; d = ImageDraw.Draw(im)
            for j in range(60):
                a = j*2.39; v = 300 + (j*53) % 700; x = CX + math.cos(a)*v*k; y = CY + math.sin(a)*v*k + 400*k*k
                d.rectangle((x - 10, y - 7, x + 10, y + 7), fill=hue(j) + (255,))
            g.paste(im, g.T(end_text, 110, g.WHITE, 12, maxw=W - 80), CX, CY - 90, g.back((k - 0.2)/0.3))
            g.paste(im, g.T(f"IN {len(HITS)} BOUNCES", 130, g.YEL, 12, maxw=W - 80), CX, CY + 60, g.back((k - 0.5)/0.3))
            g.paste(im, g.T("GUESS THE NEXT ONE IN THE COMMENTS", 54, g.GRN, 7, maxw=W - 80), W/2, H - 60 if not vert else CY + R + 120, g.back((k - 1.0)/0.3))
        dx, dy = K.shake(t); return g.camera(im, K.zoom(t), dx, dy, K.flash(t), t=t, dur=DUR)

    def audio(path):
        M = g.Mix(DUR, bed=0.15); M.add(M.boom(), 0.1, 0.8); M.add(M.ding(), 0.9)
        scale = [261.63, 293.66, 329.63, 392.0, 440.0, 523.25, 587.33, 659.25, 783.99, 880.0]
        for k, (t, pt, r) in enumerate(HITS): M.add(M.pluck(scale[k % len(scale)]*(1 + 0.5*(r/R)), 0.22, 0.6), T0 + t)
        M.add(M.riser(2.5), T0 + END - 2.5); M.add(M.boom(), T0 + END); M.fanfare(T0 + END + 0.3); M.save(path)

    return frame, audio, DUR, [1.2, T0 + 5, T0 + END - 2, T0 + END + 1.8], dict(bounces=len(HITS), duration=round(DUR, 1))
