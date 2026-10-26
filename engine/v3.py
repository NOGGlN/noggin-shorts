import math, random, colorsys, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from render import (W, H, FPS, font, text_layer, rounded, with_alpha, paste_center, gradient, RAYS,
                    ease_back, ease_out, BADGE, DARK, fit)
from mascot import mascot, tomato, splat, bubble

CARD = (960, 800)
LIMITS = [8.5, 6.5, 5.0, 4.0]
HOOK_LINE = "ONLY 2% REACH"
HOOK, INTRO, REV, OUTRO = 1.7, 0.7, 1.6, 2.0
LV = [(46, 204, 113), (243, 156, 18), (231, 76, 60), (155, 89, 182)]
LV_NAME = ["EASY", "MEDIUM", "HARD", "GENIUS"]
LV_ICON = ["🙂", "🤔", "😰", "🤯"]
LV_BG = [("#0f9b58", "#4be08a"), ("#f7971e", "#f9c823"), ("#b81d2a", "#f5574a"), ("#4a1491", "#a64bf4")]
GREEN = (46, 204, 113)
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"

def blank(): return rounded(CARD, 56, (255, 255, 255, 255))

def emoji(e, size):
    f = ImageFont.truetype(EMOJI, 109); im = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((80, 80), e, font=f, embedded_color=True, anchor="mm"); im = im.crop(im.getbbox())
    return im.resize((size, round(im.height*size/im.width)), Image.LANCZOS)

# ======================= PUZZLES =======================
def coord_opts(r, ans_rc, rows, cols):
    RL = "ABCDEFGH"; ans = f"{RL[ans_rc[0]]}{ans_rc[1]+1}"; pool = set()
    while len(pool) < 3:
        rr = min(rows-1, max(0, ans_rc[0] + r.choice([-1, 0, 1]))); cc = min(cols-1, max(0, ans_rc[1] + r.choice([-2, -1, 1, 2])))
        s = f"{RL[rr]}{cc+1}"
        if s != ans: pool.add(s)
    o = list(pool) + [ans]; r.shuffle(o); return o, o.index(ans), ans

def odd_color(seed, n=5, delta=0.085):
    r = random.Random(seed); q = blank(); d = ImageDraw.Draw(q)
    h = r.random(); base = colorsys.hls_to_rgb(h, 0.52, 0.75); odd = colorsys.hls_to_rgb(h, 0.52 + delta, 0.75)
    base = tuple(int(v*255) for v in base); odd = tuple(int(v*255) for v in odd)
    size = 640; cell = size/n; gx = (CARD[0]-size)/2 + 22; gy = (CARD[1]-size)/2 + 26
    rr, cc = r.randrange(n), r.randrange(n)
    for c in range(n): d.text((gx + c*cell + cell/2, gy - 30), str(c+1), font=font(34), fill=(150, 150, 170), anchor="mm")
    for j in range(n): d.text((gx - 34, gy + j*cell + cell/2), "ABCDEFGH"[j], font=font(34), fill=(150, 150, 170), anchor="mm")
    for j in range(n):
        for c in range(n):
            d.rounded_rectangle((gx + c*cell + 6, gy + j*cell + 6, gx + (c+1)*cell - 6, gy + (j+1)*cell - 6), 18,
                                fill=odd if (j, c) == (rr, cc) else base)
    a = q.copy(); ad = ImageDraw.Draw(a)
    ad.rounded_rectangle((gx + cc*cell - 4, gy + rr*cell - 4, gx + (cc+1)*cell + 4, gy + (rr+1)*cell + 4), 24, outline=DARK, width=12)
    opts, k, ans = coord_opts(r, (rr, cc), n, n)
    return dict(q=q, a=a, options=opts, correct=k, question="FIND THE DIFFERENT COLOR!", banner=f"IT'S {ans}!", catch=False)

def gear_poly(cx, cy, r, ang=0, tooth=14):
    n = max(9, int(r/16)); p = 2*math.pi/n; pts = []
    for j in range(n):
        a = ang + j*p
        for da, rad in ((0, r - 4), (0.12*p, r + tooth), (0.42*p, r + tooth), (0.54*p, r - 4)):
            pts.append((cx + rad*math.cos(a + da), cy + rad*math.sin(a + da)))
    return pts

def curved_arrow(d, cx, cy, rr, cw, col, w=12):
    a0, a1 = 200, 430
    d.arc((cx - rr, cy - rr, cx + rr, cy + rr), a0, a1, fill=col, width=w)
    a = math.radians(a1 if cw else a0); P = (cx + rr*math.cos(a), cy + rr*math.sin(a))
    t = (-math.sin(a), math.cos(a)) if cw else (math.sin(a), -math.cos(a)); nrm = (math.cos(a), math.sin(a))
    hs = w*2.2; tip = (P[0] + t[0]*hs, P[1] + t[1]*hs)
    d.polygon([tip, (P[0] + nrm[0]*hs*0.8, P[1] + nrm[1]*hs*0.8), (P[0] - nrm[0]*hs*0.8, P[1] - nrm[1]*hs*0.8)], fill=col)

def gears(seed, k=5):
    r = random.Random(seed)
    for _ in range(5000):
        g = [(0, 0, 0)]; r0 = r.randint(78, 96); g = [(r0 + 50, r0 + 60 + r.randint(0, 60), r0)]
        ok = True
        for i in range(1, k):
            for _try in range(60):
                ri = r.randint(62, 98); a = math.radians(r.uniform(-45, 120)); px, py, pr = g[-1]
                dist = pr + ri + 6; x, y = px + dist*math.cos(a), py + dist*math.sin(a)
                if not (ri + 30 < x < CARD[0] - ri - 30 and ri + 30 < y < CARD[1] - ri - 30): continue
                if any(math.hypot(x - gx, y - gy) < gr + ri + 40 for gx, gy, gr in g[:-1]): continue
                g.append((x, y, ri)); break
            else: ok = False; break
        if ok: break
    # fit the whole chain to fill the card
    x0b = min(x - rr - 16 for x, y, rr in g); x1b = max(x + rr + 16 for x, y, rr in g)
    y0b = min(y - rr - 16 for x, y, rr in g); y1b = max(y + rr + 16 for x, y, rr in g)
    sc = min(880/(x1b - x0b), 740/(y1b - y0b))
    ox = (CARD[0] - (x1b - x0b)*sc)/2; oy = (CARD[1] - (y1b - y0b)*sc)/2
    g = [((x - x0b)*sc + ox, (y - y0b)*sc + oy, rr*sc) for x, y, rr in g]
    q = blank(); d = ImageDraw.Draw(q)
    cols = [(52, 152, 219), (243, 156, 18), (231, 76, 60), (26, 188, 156), (230, 126, 34), (52, 73, 94)]
    def draw_gears(dd):
        for i, (x, y, rr) in enumerate(g):
            colr = GREEN if i == 0 else (155, 89, 182) if i == k-1 else cols[i % len(cols)]
            dd.polygon(gear_poly(x, y, rr, ang=i*0.3, tooth=14*rr/80), fill=colr, outline=DARK, width=5)
            dd.ellipse((x - rr*0.62, y - rr*0.62, x + rr*0.62, y + rr*0.62), fill=tuple(min(255, int(c*1.15)) for c in colr), outline=DARK, width=4)
            pass
    draw_gears(d)
    x0, y0, r0 = g[0]; curved_arrow(d, x0, y0, r0*0.42, True, "white", int(r0*0.13))
    xl, yl, rl = g[-1]; d.text((xl, yl + 3), "?", font=font(int(rl*0.8)), fill="white", anchor="mm", stroke_width=5, stroke_fill=DARK)
    a = blank(); ad = ImageDraw.Draw(a); draw_gears(ad)
    for i, (x, y, rr) in enumerate(g):
        curved_arrow(ad, x, y, rr*0.42, i % 2 == 0, "white", int(rr*0.13))
    last_cw = (k-1) % 2 == 0
    ad.ellipse((xl - rl - 26, yl - rl - 26, xl + rl + 26, yl + rl + 26), outline=GREEN, width=10)
    opts = ["Clockwise", "Anti-clockwise", "Won't move", "Both ways"]
    return dict(q=q, a=a, options=opts, correct=0 if last_cw else 1, question="WHICH WAY DOES THE PURPLE GEAR TURN?",
                banner="CLOCKWISE!" if last_cw else "ANTI-CLOCKWISE!", catch=False)

def count_squares(seed, n=3):
    r = random.Random(seed); q = blank(); d = ImageDraw.Draw(q)
    S = 540; x0, y0 = (CARD[0]-S)/2, (CARD[1]-S)/2 - 40; c = S/n
    def grid(dd):
        for k in range(n+1):
            dd.line((x0 + k*c, y0, x0 + k*c, y0 + S), fill=DARK, width=12)
            dd.line((x0, y0 + k*c, x0 + S, y0 + k*c), fill=DARK, width=12)
    grid(d)
    ans = sum((n-s+1)**2 for s in range(1, n+1))
    a = blank(); ad = ImageDraw.Draw(a); grid(ad)
    hc = [(231, 76, 60), (52, 152, 219), (243, 156, 18), (46, 204, 113)]
    k = 0
    for i in range(n-1):
        for j in range(n-1):
            o = 14 + k*7
            ad.rectangle((x0 + i*c + o, y0 + j*c + o, x0 + (i+2)*c - o, y0 + (j+2)*c - o), outline=hc[k % 4], width=8); k += 1
    ad.rectangle((x0 - 22, y0 - 22, x0 + S + 22, y0 + S + 22), outline=(155, 89, 182), width=10)
    parts = " + ".join(str((n-s+1)**2) for s in range(1, n+1))
    ad.text((CARD[0]/2, y0 + S + 62), f"{parts} = {ans}", font=font(50), fill=DARK, anchor="mm")
    opts = sorted({n*n, n*n + 1, ans - 1, ans}); r.shuffle(opts)
    return dict(q=q, a=a, options=[str(o) for o in opts], correct=opts.index(ans), question="HOW MANY SQUARES?",
                banner=f"{ans} SQUARES!", catch=True)

STROOP = {"RED": (231, 60, 50), "BLUE": (40, 110, 230), "GREEN": (30, 170, 80), "YELLOW": (240, 190, 0),
          "PURPLE": (140, 60, 190), "ORANGE": (245, 120, 20)}
def stroop(seed):
    r = random.Random(seed); names = list(STROOP)
    word = r.choice(names); ink = r.choice([n for n in names if n != word])
    q = blank(); d = ImageDraw.Draw(q)
    sz = fit(word, 840, 360, 300)
    d.text((CARD[0]/2, CARD[1]/2), word, font=font(sz), fill=STROOP[ink], anchor="mm")
    a = q.copy(); ad = ImageDraw.Draw(a)
    ad.text((CARD[0]/2, CARD[1] - 90), f"the word says {word}... but it's painted {ink}", font=font(36), fill=(120, 120, 140), anchor="mm")
    opts = [ink, word] + r.sample([n for n in names if n not in (ink, word)], 2); r.shuffle(opts)
    # each option written in a misleading ink
    tcols = []
    for o in opts:
        tcols.append(STROOP[r.choice([n for n in names if n != o])])
    return dict(q=q, a=a, options=[o.title() for o in opts], correct=opts.index(ink), question="WHAT COLOR IS THE TEXT?",
                banner=f"IT'S {ink}!", catch=True, tcols=tcols)

# ======================= UI PIECES =======================
TW, TH = 440, 170
def tile(i, text, state, tcol=None):
    fill = (46, 204, 113, 255) if state == "right" else (255, 255, 255, 255)
    im = Image.new("RGBA", (TW, TH + 12), (0, 0, 0, 0))
    im.alpha_composite(rounded((TW, TH), 44, (0, 0, 0, 70)), (0, 12)); im.alpha_composite(rounded((TW, TH), 44, fill), (0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((24, TH/2 - 44, 112, TH/2 + 44), fill=(255, 255, 255) if state == "right" else BADGE[i])
    if state == "right": d.line([(46, TH/2 + 2), (63, TH/2 + 20), (92, TH/2 - 18)], fill=GREEN, width=12, joint="curve")
    else: d.text((68, TH/2 + 3), "ABCD"[i], font=font(50), fill="white", anchor="mm")
    sz = fit(text, TW - 160, TH - 40, 58)
    d.text((128 + (TW - 150)/2, TH/2 + 3), text, font=font(sz), fill="white" if state == "right" else (tcol or DARK), anchor="mm")
    return with_alpha(im, 0.4) if state == "dim" else im

_icons = {}
def level_bar(cur, pulse=0.0):
    im = Image.new("RGBA", (1000, 170), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    segw = (920 - 3*14)/4
    for k in range(4):
        x = 40 + k*(segw + 14)
        col = LV[k] + (255,) if k <= cur else (255, 255, 255, 80)
        d.rounded_rectangle((x, 58, x + segw, 86), 14, fill=col, outline=(255, 255, 255, 230) if k <= cur else None, width=3)
    for k in range(4):
        x = 40 + k*(segw + 14) + segw/2
        act = k == cur; rad = (50 + 6*pulse) if act else 38
        if k <= cur:
            d.ellipse((x - rad, 72 - rad, x + rad, 72 + rad), fill=LV[k], outline="white", width=7 if act else 4)
        else:
            d.ellipse((x - rad, 72 - rad, x + rad, 72 + rad), fill=(255, 255, 255, 90), outline=(255, 255, 255, 160), width=3)
        key = (k, int(rad))
        if key not in _icons: _icons[key] = emoji(LV_ICON[k], int(rad*1.25))
        ic = _icons[key] if k <= cur else with_alpha(_icons[key], 0.45)
        im.alpha_composite(ic, (int(x - ic.width/2), int(72 - ic.height/2)))
        t = text_layer(LV_NAME[k], 220, 40, 28, stroke=4) if k <= cur else with_alpha(text_layer(LV_NAME[k], 220, 40, 28), 0.6)
        im.alpha_composite(t, (int(x - t.width/2), 132))
    return im

def card_layer(c):
    sh = rounded(CARD, 56, (0, 0, 0, 90)).filter(ImageFilter.GaussianBlur(14))
    L = Image.new("RGBA", (CARD[0] + 60, CARD[1] + 60), (0, 0, 0, 0)); L.alpha_composite(sh, (30, 44)); L.alpha_composite(c, (30, 30))
    return L

def scaled(im, s):
    return im if abs(s - 1) < 1e-3 else im.resize((max(1, round(im.width*s)), max(1, round(im.height*s))), Image.BILINEAR)

# ======================= TIMELINE + MASCOT =======================
INTRO_TXT = ["warm up...", "getting spicy", "you'll fail this", "IMPOSSIBLE lol"]
TAUNT = [["sooo easy", "I already know it"], ["faster!!"], ["tick tock..."], ["HURRY!!!"]]

def build_timeline():
    segs = []; t = HOOK
    for i, L in enumerate(LIMITS):
        sg = dict(i=i, intro=t, start=t + INTRO, reveal=t + INTRO + L, end=t + INTRO + L + REV); t = sg["end"]
        side = 190 if i % 2 == 0 else 890
        tt = sg["start"] + max(0.75, L*0.45)
        sg.update(side=side, throw=tt, splat_at=tt + 0.42, target=(1080 - side + (60 if side > 540 else -60), 1800))
        bub = [(sg["start"] + 0.3, sg["start"] + min(1.6, L*0.35) + 0.3, TAUNT[i][0])]
        if len(TAUNT[i]) > 1: bub.append((tt + 0.9, tt + 2.2, TAUNT[i][1]))
        sg["bubbles"] = bub
        segs.append(sg)
    return segs, t + OUTRO

def mascot_state(t, segs, total, puzzles):
    """returns x, feet_y, scale, pose, look, flip, bubble"""
    blink = (t % 2.7) < 0.12
    if t < HOOK:
        k = ease_back(t/0.4); y = 1890 + (1 - k)*600
        return 540, y, 1.45, ("laugh" if 1.0 < t else "idle"), (0, -1), False, ("you won't." if t > 0.5 else None), blink
    for sg in segs:
        if t >= sg["end"]: continue
        i = sg["i"]
        if t < sg["start"]:
            lt = t - sg["intro"]; k = ease_out(lt/0.3)
            px = 540 if i == 0 else segs[i-1]["side"]*0 + 540
            return 540, 1890, 1.25, ("shock" if i == 3 else "idle"), (0, -1), False, (INTRO_TXT[i] if lt > 0.15 else None), blink
        if t < sg["reveal"]:
            st = t - sg["start"]; side = sg["side"]; flip = side > 540
            k = ease_out(st/0.35); x = 540 + (side - 540)*k; s = 1.25 - 0.33*k
            y = 1895 - (abs(math.sin(st/0.35*math.pi*2))*60 if st < 0.35 else 0)
            pose, look = "idle", (0, -1)
            if sg["throw"] - 0.4 <= t < sg["throw"]: pose, look = "throw", (-1 if flip else 1, 0)
            # walk after throw
            wt = t - (sg["throw"] + 0.6)
            if wt > 0 and LIMITS[i] >= 5:
                kk = ease_out(min(wt/0.8, 1)); x = side + (-1 if flip else 1)*200*kk
                if wt < 0.8: y -= abs(math.sin(wt/0.8*math.pi*3))*45
            if sg["reveal"] - t < 1.2 and pose != "throw": pose, look = "shock", ((-1 if flip else 1)*0.3, -1)
            bub = next((b[2] for b in sg["bubbles"] if b[0] <= t < b[1]), None)
            return x, y, s, pose, look, flip, bub, blink
        rt = t - sg["reveal"]; P = puzzles[i]
        prevx = sg["side"] + ((-1 if sg["side"] > 540 else 1)*200 if LIMITS[i] >= 5 else 0)
        k = ease_out(rt/0.3); x = prevx + (540 - prevx)*k; y = 1895 - math.sin(min(rt/0.3, 1)*math.pi)*50
        pose = "laugh" if P["catch"] else "idle"
        txt = "GOTCHA!! haha" if P["catch"] else ["too easy?", "did u get it?"][i % 2]
        return x, y, 0.95, pose, (0, -1), False, (txt if rt > 0.2 else None), blink
    ot = t - segs[-1]["end"]
    k = ease_back(ot/0.4)
    return 540, 1890, 0.95 + 0.5*k, ("wave" if ot < 1.2 else "laugh"), (0, -1), False, ("AGAIN?" if ot > 0.9 else "your score?"), blink

# ======================= VIDEO =======================
def make_video(puzzles, out, sfx):
    segs, total = build_timeline(); NF = int(round(total*FPS))
    white = Image.new("RGB", (W, H), (255, 255, 255)); bgs = [gradient(*LV_BG[k]) for k in range(4)]
    for sg in segs:
        P = puzzles[sg["i"]]; i = sg["i"]
        sg["cq"], sg["ca"] = card_layer(P["q"]), card_layer(P["a"])
        sg["qt"] = text_layer(P["question"], 990, 190, 84, stroke=7)
        tc = P.get("tcols", [None]*4)
        sg["tiles"] = [[tile(k, o, s, tc[k]) for s in ("normal", "right", "dim")] for k, o in enumerate(P["options"])]
        bt = text_layer(P["banner"], 860, 90, 66, fill=DARK); b = rounded((bt.width + 80, bt.height + 50), 60, (255, 210, 0, 255))
        b.alpha_composite(bt, (40, 25)); sg["banner"] = b
        sg["big"] = text_layer(f"LEVEL {i+1}", 1000, 260, 220, stroke=12)
        sg["sub"] = text_layer(f"{LV_NAME[i]}  ·  {LIMITS[i]:g} SECONDS", 900, 90, 66, stroke=6)
        sg["icon"] = emoji(LV_ICON[i], 200)
        sg["splat"], sg["drips"] = splat(i*13 + 5, 400)
    gotcha = text_layer("GOTCHA!", 700, 200, 150, fill=(235, 40, 50), stroke=12, stroke_fill="white").rotate(12, expand=True, resample=Image.BICUBIC)
    hook1 = text_layer(HOOK_LINE, 1000, 160, 120, fill=(255, 225, 40), stroke=12)
    hook2 = text_layer("LEVEL 4", 1000, 300, 260, stroke=14)
    hook3 = text_layer("keep score!", 600, 80, 60, stroke=6)
    out1 = text_layer("WHAT'S YOUR\nSCORE?", 1000, 400, 160, stroke=12)
    out2 = text_layer("comment 0/4 ... 4/4", 900, 90, 70, fill=(255, 225, 40), stroke=7)
    bars = {}
    def bar(cur, pulse):
        k = (cur, round(pulse, 1))
        if k not in bars: bars[k] = level_bar(cur, pulse)
        return bars[k]
    mcache = {}
    def mimg(pose, look, blink, s, flip):
        k = (pose, look, blink, round(s, 2), flip)
        if k not in mcache:
            m = mascot(pose, look, blink)
            if flip: m = m.transpose(Image.FLIP_LEFT_RIGHT)
            mcache[k] = scaled(m, s)
        return mcache[k]
    bubs = {}
    tom = tomato(200)
    CX, CY = 540, 800
    TPOS = [(85, 1270), (555, 1270), (85, 1460), (555, 1460)]
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-", "-i", sfx, "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", out]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in range(NF):
        t = f/FPS
        sg = next((s for s in segs if t < s["end"]), None) if t >= HOOK else None
        li = sg["i"] if sg else (3 if t >= HOOK else -1)
        # ---- background
        if t < HOOK: bg = bgs[3]
        elif sg and t < sg["intro"] + 0.35:
            prev = bgs[3] if sg["i"] == 0 else bgs[sg["i"] - 1]; bg = Image.blend(prev, bgs[sg["i"]], (t - sg["intro"])/0.35)
        else: bg = bgs[li]
        rot = RAYS.rotate(t*6, resample=Image.BILINEAR).crop((330, 120, 870, 1080)).resize((W, H), Image.BILINEAR)
        fr = Image.composite(white, bg, rot).convert("RGBA")
        # ---- level bar
        if t < HOOK:
            cur = min(3, int(t/0.25)); pulse = 0
        else:
            cur = li; pulse = (math.sin(t*2*math.pi*2.2) + 1)/2
        fr.alpha_composite(bar(cur, pulse), (40, 25))
        # ---- content
        if t < HOOK:
            k1 = ease_back(t/0.3); paste_center(fr, scaled(hook1, max(0.01, k1)), 540, 620)
            k2 = ease_back((t - 0.25)/0.35)
            if k2 > 0:
                h2 = scaled(hook2, max(0.01, k2*(1 + 0.04*math.sin(t*40)))); paste_center(fr, h2, 540 + 6*math.sin(t*55), 820)
            if t > 0.7: paste_center(fr, with_alpha(hook3, min(1, (t - 0.7)/0.2)), 540, 1030)
        elif sg is None:
            ot = t - segs[-1]["end"]; k = ease_back(ot/0.4)
            paste_center(fr, scaled(out1, max(0.01, k)), 540, 720)
            paste_center(fr, with_alpha(out2, min(1, max(0, (ot - 0.3)/0.3))), 540, 1010)
        elif t < sg["start"]:
            lt = t - sg["intro"]; k = ease_back(lt/0.35)
            paste_center(fr, scaled(sg["icon"], max(0.01, k)), 540, 560)
            paste_center(fr, scaled(sg["big"], max(0.01, k)), 540, 820)
            paste_center(fr, with_alpha(sg["sub"], min(1, max(0, (lt - 0.15)/0.25))), 540, 1010)
        else:
            P = puzzles[li]; st = t - sg["start"]; rev = t >= sg["reveal"]; rt = t - sg["reveal"]
            qa = ease_out(st/0.25); paste_center(fr, with_alpha(sg["qt"], qa), 540, 300 - 40*(1 - qa))
            s = 0.7 + 0.3*ease_back(st/0.3)
            if not rev: L = sg["cq"]
            else:
                kk = min(rt/0.22, 1); L = Image.blend(sg["cq"], sg["ca"], kk) if kk < 1 else sg["ca"]
                s *= 1 + 0.05*math.sin(min(rt/0.35, 1)*math.pi)
            paste_center(fr, with_alpha(scaled(L, s), min(st/0.15, 1)), CX, CY)
            if not rev:
                rem = sg["reveal"] - t; lim = LIMITS[li]
                T = Image.new("RGBA", (200, 200), (0, 0, 0, 0)); td = ImageDraw.Draw(T)
                td.ellipse((5, 5, 195, 195), fill="white")
                colr = (231, 76, 60) if rem < 1.5 else LV[li]
                td.arc((15, 15, 185, 185), -90, -90 + 360*rem/lim, fill=colr, width=16)
                td.text((100, 104), f"{rem:.1f}", font=font(62), fill=colr, anchor="mm")
                sc = 0.82*(1 + (0.1*abs(math.sin(t*math.pi*4)) if rem < 1.5 else 0))
                paste_center(fr, scaled(T, sc), 965, 440)
            for k, (x, y) in enumerate(TPOS):
                kk = ease_out((st - 0.05*k)/0.25)
                if kk <= 0: continue
                im = sg["tiles"][k][0] if not rev else (sg["tiles"][k][1] if k == P["correct"] else sg["tiles"][k][2])
                if rev and k == P["correct"]: im = scaled(im, 1 + 0.08*math.sin(min(rt/0.3, 1)*math.pi))
                fr.alpha_composite(with_alpha(im, kk), (int(x + TW/2 - im.width/2), int(y + 60*(1 - kk) + (TH - im.height)/2)))
            if rev and rt >= 0.1:
                kk = ease_back((rt - 0.1)/0.35); paste_center(fr, scaled(sg["banner"], max(0.01, kk)), 540, 1210)
            if rev and P["catch"] and rt >= 0.05:
                kk = min(1, (rt - 0.05)/0.18); gs = 2.4 - 1.4*ease_out(kk)
                paste_center(fr, with_alpha(scaled(gotcha, gs), min(1, kk*2)), 330, 520)
        # ---- mascot
        x, y, s, pose, look, flip, btxt, blink = mascot_state(t, segs, total, puzzles)
        m = mimg(pose, look, blink, s, flip)
        fr.alpha_composite(m, (int(x - m.width/2), int(y - 290*s)))
        if btxt:
            if btxt not in bubs: bubs[btxt] = {tl: bubble(btxt, font, tl) for tl in ("down", "sideL", "sideR")}
            in_puzzle = sg is not None and t >= sg["start"]
            if in_puzzle:
                tail = "sideL" if x <= 560 else "sideR"; bb = bubs[btxt][tail]
                bx = x + 125*s if tail == "sideL" else x - 125*s - bb.width
                by = max(1650, y - 175*s - bb.height/2)
            else:
                bb = bubs[btxt]["down"]; bx = x - bb.width/2; by = y - 290*s - bb.height + 30
            bx = min(max(bx, 10), W - bb.width - 10)
            fr.alpha_composite(bb, (int(bx), int(by)))
        # ---- tomato + splat (on the "glass", above everything)
        shake = (0, 0)
        if sg is not None and t >= sg["start"]:
            hx = x + (-1 if flip else 1)*123*0.92; hy = y - 220*0.92
            u = (t - sg["throw"])/0.42
            if 0 <= u < 1:
                tx, ty = sg["target"]
                hy2 = max(hy, 1725); px = hx + (tx - hx)*u; py = hy2 + (ty - hy2)*u - 40*math.sin(math.pi*u)
                ti = scaled(tom, 0.3 + 0.45*u**2).rotate(-u*540, expand=True, resample=Image.BILINEAR)
                paste_center(fr, ti, px, py)
            sp = t - sg["splat_at"]
            if 0 <= sp < 2.0:
                a = 1 if sp < 1.5 else 1 - (sp - 1.5)/0.5
                img = sg["splat"].copy(); dd = ImageDraw.Draw(img)
                for dx, dw in sg["drips"]:
                    ln = min(1, sp/1.5)*img.height*0.35
                    dd.rounded_rectangle((dx - dw/2, img.width*0.5, dx + dw/2, img.width*0.5 + ln), int(dw/2), fill=(214, 32, 38, 255))
                sq = 1.08 - 0.08*ease_out(sp/0.12)
                tx, ty = sg["target"]; si = with_alpha(scaled(img, sq*0.8), a)
                fr.alpha_composite(si, (int(tx - si.width/2), int(ty - si.width/2)))
                if sp < 0.18: amp = 16*(1 - sp/0.18); shake = (int(amp*math.sin(t*170)), int(amp*math.cos(t*130)))
        rgb = fr.convert("RGB")
        if sg is not None and t >= sg["reveal"] and t - sg["reveal"] < 0.2:
            rgb = Image.blend(rgb, white, 0.5*(1 - (t - sg["reveal"])/0.2))
        if t < 0.12: rgb = Image.blend(rgb, white, 0.7*(1 - t/0.12))
        if shake != (0, 0):
            sh = Image.new("RGB", (W, H)); sh.paste(rgb, shake); rgb = sh
        ff.stdin.write(rgb.tobytes())
    ff.stdin.close(); ff.wait()
    return segs, total

# ======================= AUDIO =======================
def make_sfx(puzzles, path):
    segs, total = build_timeline(); sr = 44100; N = int(sr*(total + 0.3)); a = np.zeros(N); mus = np.zeros(N)
    rng = np.random.default_rng(3)
    def add(sig, t, buf=a):
        i = int(t*sr); n = min(len(sig), N - i)
        if n > 0: buf[i:i + n] += sig[:n]
    def tt_(dur): return np.arange(int(dur*sr))/sr
    def env(n, dec): return np.exp(-np.arange(n)/(sr*dec))
    def lp(x, k=8): return np.convolve(x, np.ones(k)/k, mode="same")
    def tick(t, fr, amp=0.5):
        x = tt_(0.07); add((amp*np.sin(2*np.pi*fr*x) + rng.standard_normal(len(x))*0.1)*env(len(x), 0.012), t)
    def whoosh(t, dur=0.5, amp=0.5):
        x = rng.standard_normal(int(dur*sr)); e = np.sin(np.linspace(0, np.pi, len(x)))**2; add(amp*lp(x, 6)*e, t)
    def pop(t):
        x = tt_(0.12); add(0.5*np.sin(2*np.pi*(400*x + 3000*x**2))*env(len(x), 0.04), t)
    def boing(t):
        x = tt_(0.35); f = 220 + 160*np.exp(-x*8); add(0.35*np.sin(2*np.pi*np.cumsum(f)/sr*(1 + 0.04*np.sin(2*np.pi*18*x)))*env(len(x), 0.12), t)
    def splat_s(t):
        x = rng.standard_normal(int(0.28*sr)); add(0.9*lp(x, 30)*env(len(x), 0.07), t)
        y = tt_(0.2); add(0.6*np.sin(2*np.pi*(120*y - 150*y**2))*env(len(y), 0.06), t)
    def chime(t):
        for j, fr in enumerate([1046.5, 1318.5, 1568.0, 2093.0]):
            x = tt_(1.3); add(0.2*(np.sin(2*np.pi*fr*x) + 0.3*np.sin(4*np.pi*fr*x))*env(len(x), 0.4), t + j*0.06)
    def laugh(t):
        for j in range(5):
            x = tt_(0.11); f0 = 520 - j*30
            sig = np.sign(np.sin(2*np.pi*f0*x))*0.5 + np.sin(2*np.pi*f0*2*x)*0.5
            add(0.18*lp(sig, 4)*np.sin(np.linspace(0, np.pi, len(x))), t + j*0.13)
    def buzz(t):
        for j, f0 in enumerate([220, 165]):
            x = tt_(0.28); add(0.22*lp(np.sign(np.sin(2*np.pi*f0*x)), 3)*env(len(x), 0.2), t + j*0.26)
    def riser(t, dur):
        x = tt_(dur); f = 200 + 1800*(x/dur)**2; add(0.25*np.sin(2*np.pi*np.cumsum(f)/sr)*(x/dur), t)
        whoosh(t, dur, 0.25)
    def hit(t):
        x = tt_(0.5); add(0.8*np.sin(2*np.pi*(60*x))*env(len(x), 0.15), t); whoosh(t, 0.25, 0.4)
    # hook
    hit(0.0); pop(0.05); riser(0.25, 0.6); hit(0.85); laugh(1.05)
    for sg in segs:
        i = sg["i"]; whoosh(sg["intro"], 0.45, 0.6); pop(sg["intro"] + 0.1)
        boing(sg["start"] + 0.05)
        step = [1.0, 0.5, 0.5, 0.25][i]; t = sg["start"]; k = 0
        while t < sg["reveal"] - 0.05:
            rem = sg["reveal"] - t; tick(t, 1300 if rem > 1.5 else 1800, 0.5 if k % 2 == 0 else 0.33)
            t += step if rem > 1.5 else 0.25; k += 1
        whoosh(sg["throw"], 0.3, 0.5); splat_s(sg["splat_at"])
        if LIMITS[i] >= 5:
            for j in range(3): boing(sg["throw"] + 0.6 + j*0.27)
        for b in sg["bubbles"]: pop(b[0])
        chime(sg["reveal"])
        if puzzles[i]["catch"]: buzz(sg["reveal"] + 0.05); laugh(sg["reveal"] + 0.35)
        else: boing(sg["reveal"])
    end = segs[-1]["end"]; hit(end); laugh(end + 0.5)
    for j, fr in enumerate([523.3, 659.3, 784.0, 1046.5]):
        x = tt_(1.0); add(0.2*np.sin(2*np.pi*fr*x)*env(len(x), 0.3), end + 0.1 + j*0.08)
    # background beat (124 bpm): kick, hats, bass; ducked during reveals
    bpm = 124; beat = 60/bpm; bass_notes = [55.0, 55.0, 65.4, 49.0]
    b = 0; t = 0.85
    while t < total - 0.2:
        x = tt_(0.25); add(0.55*np.sin(2*np.pi*(50 + 90*np.exp(-x*30))*x)*env(len(x), 0.08), t, mus)
        h = rng.standard_normal(int(0.04*sr)); h = h - lp(h, 4); add(0.12*h*env(len(h), 0.01), t + beat/2, mus)
        x = tt_(beat*0.9); f0 = bass_notes[(b//4) % 4]
        add(0.22*np.sin(2*np.pi*f0*x)*np.minimum(1, x*40)*env(len(x), 0.25), t, mus)
        t += beat; b += 1
    duck = np.ones(N)
    for sg in segs:
        i0, i1 = int(sg["reveal"]*sr), int((sg["reveal"] + 0.9)*sr); duck[i0:i1] = 0.35
    out = a + mus*duck*0.7
    out = out/np.abs(out).max()*0.9
    s = (np.stack([out, out], 1)*32767).astype(np.int16)
    with wave.open(path, "wb") as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes(s.tobytes())

if __name__ == "__main__":
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    puzzles = [odd_color(seed), gears(seed + 1), count_squares(seed + 2), stroop(seed + 3)]
    make_sfx(puzzles, "/home/claude/shorts/sfx_v3.wav")
    make_video(puzzles, f"/home/claude/shorts/sample_v3_{seed}.mp4", "/home/claude/shorts/sfx_v3.wav")
    for i, P in enumerate(puzzles): print(i + 1, P["question"], P["options"], "->", P["options"][P["correct"]])
