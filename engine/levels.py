import math, random, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from render import (W, H, FPS, font, text_layer, rounded, with_alpha, paste_center, gradient, RAYS,
                    ease_back, ease_out, tile, TW, TH, BADGE, DARK, hexrgb)

CARD = (960, 800)
LIMITS = [7.0, 5.0, 2.5]
INTRO, REVEAL_LEN, OUTRO = 0.8, 1.7, 1.8
LEVEL_COL = [(46, 204, 113), (243, 156, 18), (231, 76, 60)]
LEVEL_NAME = ["EASY", "MEDIUM", "HARD"]
LEVEL_BG = [("#11998e", "#38ef7d"), ("#f7971e", "#f9d423"), ("#cb2d3e", "#ef473a")]
GREEN = (46, 204, 113)

def blank():
    return rounded(CARD, 56, (255, 255, 255, 255))

# ---------------- FIND THE X ----------------
def find_x(seed, cols=10, rows=8, letters="KY"):
    r = random.Random(seed)
    q = blank(); d = ImageDraw.Draw(q)
    cell = 80; gx = (CARD[0] - cols*cell)//2 + 22; gy = (CARD[1] - rows*cell)//2 + 22
    RL = "ABCDEFGHIJ"
    for c in range(cols):
        d.text((gx + c*cell + cell/2, gy - 34), str(c+1), font=font(34), fill=(150, 150, 170), anchor="mm")
    for j in range(rows):
        d.text((gx - 36, gy + j*cell + cell/2), RL[j], font=font(34), fill=(150, 150, 170), anchor="mm")
    xr, xc = r.randrange(1, rows-1), r.randrange(1, cols-1)
    for j in range(rows):
        for c in range(cols):
            ch = "X" if (j, c) == (xr, xc) else r.choice(letters)
            d.text((gx + c*cell + cell/2, gy + j*cell + cell/2 + 2), ch, font=font(60), fill=DARK, anchor="mm")
    a = q.copy(); ad = ImageDraw.Draw(a)
    cx, cy = gx + xc*cell + cell/2, gy + xr*cell + cell/2
    ad.ellipse((cx-46, cy-46, cx+46, cy+46), outline=(231, 76, 60), width=10)
    ans = f"{RL[xr]}{xc+1}"
    pool = set()
    while len(pool) < 3:
        jr = min(rows-1, max(0, xr + r.choice([-1, 0, 1]))); jc = min(cols-1, max(0, xc + r.choice([-2, -1, 1, 2])))
        s = f"{RL[jr]}{jc+1}"
        if s != ans: pool.add(s)
    opts = list(pool) + [ans]; r.shuffle(opts)
    return dict(q=q, a=a, options=opts, correct=opts.index(ans), question="FIND THE X!", banner=f"IT WAS AT {ans}!")

# ---------------- WHERE WILL THE X GO (tangled lines) ----------------
def catmull(pts, n=24):
    P = [pts[0]] + pts + [pts[-1]]; out = []
    for i in range(1, len(P)-2):
        p0, p1, p2, p3 = map(np.array, P[i-1:i+3])
        for t in np.linspace(0, 1, n, endpoint=False):
            out.append(tuple(0.5*((2*p1) + (-p0+p2)*t + (2*p0-5*p1+4*p2-p3)*t*t + (-p0+3*p1-3*p2+p3)*t**3)))
    out.append(pts[-1]); return out

def tangle(seed, ncp=5):
    r = random.Random(seed)
    xs = [150, 370, 590, 810]; ytop, ybot = 95, 705
    xi = r.randrange(4)
    while True:
        perm = list(range(4)); r.shuffle(perm)
        if perm[xi] not in (xi,) and abs(perm[xi]-xi) >= 1: break
    lanes = list(np.linspace(110, 850, 7))
    rowsx = [r.sample(lanes, 4) for _ in range(ncp)]
    paths = []
    for i in range(4):
        pts = [(xs[i], ytop+40)]
        for k in range(ncp):
            y = ytop + 40 + (k+1)*(ybot - ytop - 120)/(ncp+1)
            pts.append((rowsx[k][i], y))
        pts.append((xs[perm[i]], ybot-60))
        paths.append(catmull(pts))
    q = blank(); d = ImageDraw.Draw(q)
    order = list(range(4)); r.shuffle(order)
    for i in order:
        d.line(paths[i], fill=(255, 255, 255), width=26, joint="curve")
        d.line(paths[i], fill=DARK, width=12, joint="curve")
    for i, x in enumerate(xs):  # start tokens
        if i == xi:
            d.ellipse((x-44, ytop-44, x+44, ytop+44), fill=(231, 76, 60))
            d.text((x, ytop+2), "X", font=font(56), fill="white", anchor="mm")
        else:
            d.ellipse((x-34, ytop-34, x+34, ytop+34), fill=(190, 190, 205))
    for k, x in enumerate(xs):  # end boxes
        d.rounded_rectangle((x-50, ybot-50, x+50, ybot+50), 22, fill=BADGE[k])
        d.text((x, ybot+3), "ABCD"[k], font=font(56), fill="white", anchor="mm")
    a = q.copy(); ad = ImageDraw.Draw(a)
    ad.line(paths[xi], fill=(231, 76, 60), width=16, joint="curve")
    e = xs[perm[xi]]; ad.rounded_rectangle((e-62, ybot-62, e+62, ybot+62), 28, outline=GREEN, width=10)
    opts = ["Box A", "Box B", "Box C", "Box D"]
    return dict(q=q, a=a, options=opts, correct=perm[xi], question="WHERE WILL THE X GO?", banner=f"BOX {'ABCD'[perm[xi]]}!")

# ---------------- WHICH CAMERA (perspective) ----------------
CUBE_COLS = [(231, 76, 60), (52, 152, 219), (241, 196, 15), (155, 89, 182), (46, 204, 113)]
def shade(c, f): return tuple(min(255, int(v*f)) for v in c)

def perspective(seed, n=3, hmax=3):
    r = random.Random(seed)
    while True:
        h = [[r.randint(1, hmax) for _ in range(n)] for _ in range(n)]
        col = {(x, y, z): r.choice(CUBE_COLS) for x in range(n) for y in range(n) for z in range(h[x][y])}
        def view(side):
            img = []
            for z in range(hmax-1, -1, -1):
                row = []
                for u in range(n):
                    if side == "+y": x, ys = u, range(n-1, -1, -1); cell = next(((x, y, z) for y in ys if z < h[x][y]), None)
                    elif side == "-y": x, ys = n-1-u, range(n); cell = next(((x, y, z) for y in ys if z < h[x][y]), None)
                    elif side == "+x": y, xs_ = n-1-u, range(n-1, -1, -1); cell = next(((x, y, z) for x in xs_ if z < h[x][y]), None)
                    else: y, xs_ = u, range(n); cell = next(((x, y, z) for x in xs_ if z < h[x][y]), None)
                    row.append(col[cell] if cell else None)
                img.append(tuple(row))
            return tuple(img)
        sides = ["+y", "+x", "-y", "-x"]
        V = {s: view(s) for s in sides}
        if len(set(V.values())) == 4 and max(max(r_) for r_ in h) == hmax: break
    q = blank(); d = ImageDraw.Draw(q)
    s = 80; a_ = s*0.866; b_ = s*0.5; ox, oy = 600, 300
    def P(x, y, z): return (ox + (x - y)*a_, oy + (x + y)*b_ - z*s)
    # floor
    d.polygon([P(0, 0, 0), P(n, 0, 0), P(n, n, 0), P(0, n, 0)], fill=(225, 228, 238))
    cubes = sorted(col.keys(), key=lambda c: (c[0]+c[1], c[2]))
    for (x, y, z) in cubes:
        c = col[(x, y, z)]
        top = [P(x, y, z+1), P(x+1, y, z+1), P(x+1, y+1, z+1), P(x, y+1, z+1)]
        fy = [P(x, y+1, z), P(x+1, y+1, z), P(x+1, y+1, z+1), P(x, y+1, z+1)]
        fx = [P(x+1, y, z), P(x+1, y+1, z), P(x+1, y+1, z+1), P(x+1, y, z+1)]
        for poly, f in ((top, 1.15), (fy, 0.95), (fx, 0.72)):
            d.polygon(poly, fill=shade(c, f), outline=(30, 30, 50), width=3)
    side_pos = {"+y": (1.5, n+2.2), "+x": (n+2.2, 1.5), "-y": (1.5, -2.2), "-x": (-2.2, 1.5)}
    letters = list("ABCD"); r.shuffle(letters)
    cam = dict(zip(sides, letters))
    target = r.choice(sides)
    cams_xy = {}
    for sd in sides:
        wx, wy = side_pos[sd]; cx, cy = P(wx, wy, 0)
        cams_xy[sd] = (cx, cy)
        k = "ABCD".index(cam[sd])
        d.ellipse((cx-40, cy-40, cx+40, cy+40), fill=BADGE[k], outline="white", width=5)
        # little camera glyph
        d.rounded_rectangle((cx-20, cy-12, cx+20, cy+16), 6, fill="white")
        d.ellipse((cx-9, cy-6, cx+9, cy+12), fill=BADGE[k])
        d.text((cx, cy-56), cam[sd], font=font(40), fill=BADGE[k], anchor="mm", stroke_width=4, stroke_fill="white")
    # photo
    img = V[target]; cs = 70; pw, ph = n*cs, hmax*cs
    px, py = 40, 80
    d.text((px + pw/2 + 12, py - 30), "PHOTO", font=font(34), fill=(120, 120, 140), anchor="mm")
    d.rounded_rectangle((px-4, py-4, px+pw+28, py+ph+28), 18, fill=(245, 246, 250), outline=(120, 120, 140), width=4)
    for zi, row in enumerate(img):
        for u, c in enumerate(row):
            if c: d.rectangle((px+12+u*cs, py+12+zi*cs, px+12+(u+1)*cs, py+12+(zi+1)*cs), fill=shade(c, 0.95), outline=(30, 30, 50), width=3)
    a = q.copy(); ad = ImageDraw.Draw(a)
    cx, cy = cams_xy[target]
    ad.ellipse((cx-58, cy-58, cx+58, cy+58), outline=GREEN, width=10)
    opts = [f"Camera {l}" for l in "ABCD"]
    ans = cam[target]
    return dict(q=q, a=a, options=opts, correct="ABCD".index(ans), question="WHICH CAMERA TOOK THIS PHOTO?", banner=f"CAMERA {ans}!")

# ---------------- video ----------------
def card_layer(c):
    sh = rounded(CARD, 56, (0, 0, 0, 90)).filter(ImageFilter.GaussianBlur(14))
    L = Image.new("RGBA", (CARD[0]+60, CARD[1]+60), (0, 0, 0, 0)); L.alpha_composite(sh, (30, 44)); L.alpha_composite(c, (30, 30))
    return L

def make_video(levels, out, sfx_path):
    # timeline
    segs = []; t = 0
    for i, P in enumerate(levels):
        segs.append(dict(i=i, intro=t, start=t+INTRO, reveal=t+INTRO+LIMITS[i], end=t+INTRO+LIMITS[i]+REVEAL_LEN, P=P)); t = segs[-1]["end"]
    total = t + OUTRO; NF = int(round(total*FPS))
    white = Image.new("RGB", (W, H), (255, 255, 255))
    bgs = [gradient(*LEVEL_BG[i]) for i in range(3)]
    for sg in segs:
        P = sg["P"]; i = sg["i"]
        sg["cq"], sg["ca"] = card_layer(P["q"]), card_layer(P["a"])
        sg["qt"] = text_layer(P["question"], 980, 200, 84, stroke=7)
        sg["tiles"] = [[tile(k, o, s) for s in ("normal", "right", "dim")] for k, o in enumerate(P["options"])]
        bt = text_layer(P["banner"], 860, 90, 66, fill=DARK); b = rounded((bt.width+80, bt.height+50), 60, (255, 210, 0, 255)); b.alpha_composite(bt, (40, 25)); sg["banner"] = b
        big = text_layer(f"LEVEL {i+1}", 1000, 260, 210, stroke=12)
        sub = text_layer(f"{LEVEL_NAME[i]}  ·  {LIMITS[i]:g} SECONDS", 900, 90, 64, stroke=6)
        sg["big"], sg["sub"] = big, sub
    outro1 = text_layer("HOW MANY DID\nYOU GET?", 1000, 400, 150, stroke=12)
    outro2 = text_layer("Comment your score: 0/3, 1/3, 2/3 or 3/3!", 980, 80, 48, stroke=5)
    foot = text_layer("Comment your answer!", 980, 60, 46, stroke=4)

    def steps(cur, done_until):
        im = Image.new("RGBA", (420, 110), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        for k in range(3):
            x = 70 + k*140
            if k < 2: d.line((x+40, 55, x+100, 55), fill=(255, 255, 255, 160), width=8)
        for k in range(3):
            x = 70 + k*140
            active = k == cur
            r = 46 if active else 36
            fill = LEVEL_COL[k] if k <= cur else (255, 255, 255, 90)
            d.ellipse((x-r, 55-r, x+r, 55+r), fill=fill, outline="white", width=6 if active else 4)
            d.text((x, 57), str(k+1), font=font(44 if active else 34), fill="white", anchor="mm")
        return im
    step_imgs = [steps(k, k) for k in range(3)]

    CX, CY = 540, 790
    TPOS = [(85, 1260), (555, 1260), (85, 1455), (555, 1455)]
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-", "-i", sfx_path, "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", out]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in range(NF):
        t = f/FPS
        sg = next((s for s in segs if t < s["end"]), None)
        li = sg["i"] if sg else 2
        # background: crossfade into new level colour during intro
        bg = bgs[li]
        if sg and li > 0 and t < sg["intro"] + 0.4: bg = Image.blend(bgs[li-1], bgs[li], (t - sg["intro"])/0.4)
        rot = RAYS.rotate(t*4, resample=Image.BILINEAR).crop((330, 120, 870, 1080)).resize((W, H), Image.BILINEAR)
        fr = Image.composite(white, bg, rot).convert("RGBA")
        if sg is None:  # outro
            k = ease_back((t - segs[-1]["end"])/0.45)
            o = outro1.resize((max(1, int(outro1.width*k)), max(1, int(outro1.height*k))), Image.BILINEAR)
            paste_center(fr, o, 540, 820); paste_center(fr, with_alpha(outro2, min(1, (t-segs[-1]["end"])/0.4)), 540, 1100)
            ff.stdin.write(fr.convert("RGB").tobytes()); continue
        P = sg["P"]; lt = t - sg["intro"]
        paste_center(fr, step_imgs[li], 540, 120)
        if t < sg["start"]:  # level intro card
            k = ease_back(lt/0.4)
            b = sg["big"].resize((max(1, int(sg["big"].width*k)), max(1, int(sg["big"].height*k))), Image.BILINEAR)
            paste_center(fr, b, 540, 860); paste_center(fr, with_alpha(sg["sub"], min(1, max(0, (lt-0.2)/0.3))), 540, 1050)
            ff.stdin.write(fr.convert("RGB").tobytes()); continue
        st = t - sg["start"]; rev = t >= sg["reveal"]; rt = t - sg["reveal"]
        qa = ease_out(st/0.25); paste_center(fr, with_alpha(sg["qt"], qa), 540, 285 - 50*(1-qa))
        s = 0.7 + 0.3*ease_back(st/0.3)
        if not rev: L = sg["cq"]
        else:
            k = min(rt/0.25, 1); L = Image.blend(sg["cq"], sg["ca"], k) if k < 1 else sg["ca"]
            s *= 1 + 0.05*math.sin(min(rt/0.35, 1)*math.pi)
        if abs(s-1) > 1e-3: L = L.resize((round(L.width*s), round(L.height*s)), Image.BILINEAR)
        paste_center(fr, with_alpha(L, min(st/0.15, 1)), CX, CY)
        if not rev:
            rem = sg["reveal"] - t; lim = LIMITS[li]
            T = Image.new("RGBA", (200, 200), (0, 0, 0, 0)); td = ImageDraw.Draw(T)
            td.ellipse((5, 5, 195, 195), fill="white")
            colr = (231, 76, 60) if rem < 2 else LEVEL_COL[li]
            td.arc((15, 15, 185, 185), -90, -90 + 360*rem/lim, fill=colr, width=16)
            td.text((100, 104), f"{rem:.1f}", font=font(62), fill=colr, anchor="mm")
            sc = 1 + (0.08*math.sin(t*2*math.pi*4) if rem < 2 else 0)
            if sc != 1: T = T.resize((round(200*sc), round(200*sc)), Image.BILINEAR)
            paste_center(fr, T.resize((int(T.width*0.82), int(T.height*0.82)), Image.BILINEAR), 965, 435)
        for k, (x, y) in enumerate(TPOS):
            kk = ease_out((st - 0.05*k)/0.25)
            if kk <= 0: continue
            im = sg["tiles"][k][0] if not rev else (sg["tiles"][k][1] if k == P["correct"] else sg["tiles"][k][2])
            if rev and k == P["correct"]:
                sc = 1 + 0.08*math.sin(min(rt/0.3, 1)*math.pi); im = im.resize((round(im.width*sc), round(im.height*sc)), Image.BILINEAR)
            fr.alpha_composite(with_alpha(im, kk), (int(x + TW/2 - im.width/2), int(y + 60*(1-kk) + (TH - im.height)/2)))
        if rev and rt >= 0.1:
            k = ease_back((rt-0.1)/0.35); b = sg["banner"]
            b = b.resize((max(1, round(b.width*k)), max(1, round(b.height*k))), Image.BILINEAR)
            paste_center(fr, b, 540, 1200)
        else:
            paste_center(fr, with_alpha(foot, min(1, st/0.3)), 540, 1720)
        rgb = fr.convert("RGB")
        if rev and rt < 0.22: rgb = Image.blend(rgb, white, 0.5*(1 - rt/0.22))
        ff.stdin.write(rgb.tobytes())
    ff.stdin.close(); ff.wait()
    return segs, total

def make_sfx(segs, total, path):
    sr = 44100; a = np.zeros(int(sr*(total+0.5)))
    def add(sig, t):
        i = int(t*sr); n = min(len(sig), len(a)-i); a[i:i+n] += sig[:n]
    def env(n, dec): return np.exp(-np.arange(n)/(sr*dec))
    rng = np.random.default_rng(1)
    def tick(t, fr, amp=0.55):
        n = int(0.08*sr); tt = np.arange(n)/sr
        add((amp*np.sin(2*np.pi*fr*tt) + rng.standard_normal(n)*0.12)*env(n, 0.012), t)
    for sg in segs:
        i = sg["i"]
        n = int(0.5*sr); tt = np.arange(n)/sr  # level whoosh
        add(0.4*np.sin(2*np.pi*(250*tt + (600+200*i)*tt**2))*env(n, 0.15), sg["intro"])
        step = [1.0, 0.5, 0.25][i]
        t = sg["start"]; k = 0
        while t < sg["reveal"] - 0.05:
            rem = sg["reveal"] - t
            tick(t, 1300 if rem > 2 else 1800, 0.5 if k % 2 == 0 else 0.35); t += step if rem > 2 else min(step, 0.25); k += 1
        for j, fr in enumerate([1046.5, 1318.5, 1568.0, 2093.0]):
            n = int(1.4*sr); tt = np.arange(n)/sr
            add(0.22*(np.sin(2*np.pi*fr*tt) + 0.3*np.sin(4*np.pi*fr*tt))*env(n, 0.4), sg["reveal"] + j*0.06)
    end = segs[-1]["end"]
    for j, fr in enumerate([523.3, 659.3, 784.0, 1046.5, 1318.5]):
        n = int(1.2*sr); tt = np.arange(n)/sr
        add(0.2*np.sin(2*np.pi*fr*tt)*env(n, 0.35), end + j*0.09)
    a = a/np.abs(a).max()*0.85; s = (np.stack([a, a], 1)*32767).astype(np.int16)
    with wave.open(path, "wb") as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes(s.tobytes())

if __name__ == "__main__":
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    levels = [find_x(seed), tangle(seed+1), perspective(seed+2)]
    # sfx first (timeline only needs limits), then video
    segs = []; t = 0
    for i in range(3):
        segs.append(dict(i=i, intro=t, start=t+INTRO, reveal=t+INTRO+LIMITS[i], end=t+INTRO+LIMITS[i]+REVEAL_LEN)); t = segs[-1]["end"]
    make_sfx(segs, t + OUTRO, "/home/claude/shorts/sfx_lv.wav")
    make_video(levels, f"/home/claude/shorts/sample_levels_{seed}.mp4", "/home/claude/shorts/sfx_lv.wav")
    for i, P in enumerate(levels): print(i+1, P["question"], P["options"], "->", P["options"][P["correct"]])
