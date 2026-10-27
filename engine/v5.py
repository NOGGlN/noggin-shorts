"""Noggin v5: 3-level version of the v4 engine (Easy green / Medium red / Hard purple)."""
import math, random, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from render import W, H, FPS, font, text_layer, rounded, with_alpha, paste_center, gradient, ease_back, ease_out, DARK
from mascot import mascot, tomato, splat, bubble
from v3 import (CARD, LV, LV_NAME, LV_ICON, LV_BG, GREEN, emoji, tile, level_bar, card_layer, scaled, TW, TH)

LIMITS = [8.5, 6.5, 5.0]
LV = [(46, 204, 113), (231, 76, 60), (155, 89, 182)]
LV_NAME = ["EASY", "MEDIUM", "HARD"]
LV_ICON = ["🙂", "😰", "🤯"]
LV_BG = [("#0f9b58", "#4be08a"), ("#b81d2a", "#f5574a"), ("#4a1491", "#a64bf4")]
_icons = {}
def level_bar(cur, pulse=0.0):
    n = 3; im = Image.new("RGBA", (1000, 170), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    segw = (920 - (n - 1)*18)/n
    for k in range(n):
        x = 40 + k*(segw + 18); col = LV[k] + (255,) if k <= cur else (255, 255, 255, 80)
        d.rounded_rectangle((x, 58, x + segw, 86), 14, fill=col, outline=(255, 255, 255, 230) if k <= cur else None, width=3)
    for k in range(n):
        x = 40 + k*(segw + 18) + segw/2; act = k == cur; rad = (52 + 6*pulse) if act else 40
        if k <= cur: d.ellipse((x - rad, 72 - rad, x + rad, 72 + rad), fill=LV[k], outline="white", width=7 if act else 4)
        else: d.ellipse((x - rad, 72 - rad, x + rad, 72 + rad), fill=(255, 255, 255, 90), outline=(255, 255, 255, 160), width=3)
        key = (k, int(rad))
        if key not in _icons: _icons[key] = emoji(LV_ICON[k], int(rad*1.25))
        ic = _icons[key] if k <= cur else with_alpha(_icons[key], 0.45)
        im.alpha_composite(ic, (int(x - ic.width/2), int(72 - ic.height/2)))
        t = text_layer(LV_NAME[k], 220, 40, 30, stroke=4) if k <= cur else with_alpha(text_layer(LV_NAME[k], 220, 40, 30), 0.6)
        im.alpha_composite(t, (int(x - t.width/2), 132))
    return im
HOOK_LINE = "ONLY 2% REACH"
HOOK, INTRO, REV, OUTRO = 1.9, 0.7, 2.1, 2.2
HOOK_FIRST = False   # True: no hook/intro card, level-1 question is on screen from frame 0 with the hook line on top
def _h0(): return 0.0 if HOOK_FIRST else HOOK
INTRO_TXT = ["warm up...", "getting spicy", "IMPOSSIBLE lol"]
TAUNT = [["sooo easy", "I know it already"], ["faster!!"], ["tick tock..."], ["HURRY!!!"]]
PRE_TAUNT = {"WATCH THE BALL!": "eyes on the ball!", "MEMORIZE!": "remember them!"}

def build_timeline(puzzles):
    segs = []; t = _h0()
    for i, (L, P) in enumerate(zip(LIMITS, puzzles)):
        pre = P.get("pre", 0.0); IN = 0.0 if (HOOK_FIRST and i == 0) else INTRO
        sg = dict(i=i, intro=t, pstart=t + IN, start=t + IN + pre, reveal=t + IN + pre + L,
                  end=t + IN + pre + L + REV, pre=pre); t = sg["end"]
        side = 190 if i % 2 == 0 else 890
        mode = P.get("throw") if i <= 1 else None   # hard/genius: no tomatoes at all
        tt = sg["start"] + max(0.75, L*0.33)
        sg.update(side=side, mode=mode, throw=tt if mode else None, splat_at=tt + 0.42 if mode else None)
        rr = random.Random(int(t*100) + i)
        if mode == "screen": sg["target"] = (rr.uniform(300, 760), rr.uniform(620, 1020)); sg["stay"] = 0.55
        else: sg["target"] = (1080 - side + (60 if side > 540 else -60), 1800); sg["stay"] = 0.7
        bub = []
        if i <= 1:
            bub.append((sg["start"] + 0.3, sg["start"] + min(1.6, L*0.35) + 0.3, TAUNT[i][0]))
            if len(TAUNT[i]) > 1: bub.append((tt + 2.05, tt + 3.4, TAUNT[i][1]))
        if pre: bub.insert(0, (sg["pstart"] + 0.3, sg["pstart"] + 1.8, PRE_TAUNT.get(P.get("pre_label"), "watch closely")))
        sg["bubbles"] = bub
        segs.append(sg)
    return segs, t + OUTRO

def mascot_state(t, segs, total, puzzles):
    blink = (t % 2.7) < 0.12
    if t < _h0():
        k = ease_back(t/0.4); y = 1890 + (1 - k)*600
        return 540, y, 1.45, ("laugh" if 1.1 < t else "idle"), (0, -1), False, ("you won't." if t > 0.5 else None), blink
    for sg in segs:
        if t >= sg["end"]: continue
        i = sg["i"]
        if t < sg["pstart"]:
            lt = t - sg["intro"]
            return 540, 1890, 1.25, ("shock" if i == 2 else "idle"), (0, -1), False, (INTRO_TXT[i] if lt > 0.15 else None), blink
        side = sg["side"]; flip = side > 540
        if t < sg["start"]:  # pre-phase (watching)
            st = t - sg["pstart"]; k = ease_out(st/0.35); x = 540 + (side - 540)*k; s = 1.25 - 0.33*k
            bub = next((b[2] for b in sg["bubbles"] if b[0] <= t < b[1]), None)
            return x, 1895, s, "idle", ((-1 if flip else 1)*0.6, -1), flip, bub, blink
        if t < sg["reveal"]:
            st = t - sg["start"]
            if sg["pre"]: x, s = side, 0.92
            else:
                k = ease_out(st/0.35); x = 540 + (side - 540)*k; s = 1.25 - 0.33*k
            y = 1895 - (abs(math.sin(st/0.35*math.pi*2))*60 if st < 0.35 and not sg["pre"] else 0)
            pose, look = "idle", (0, -1)
            if sg["throw"] and sg["throw"] - 0.4 <= t < sg["throw"]: pose, look = "throw", (-1 if flip else 1, 0) if sg["mode"] == "strip" else (-1 if flip else 1, -1)
            wt = t - (sg["throw"] + 0.6) if sg["throw"] else -1
            if wt > 0 and LIMITS[i] >= 5:
                kk = ease_out(min(wt/0.8, 1)); x = side + (-1 if flip else 1)*200*kk
                if wt < 0.8: y -= abs(math.sin(wt/0.8*math.pi*3))*45
            if sg["reveal"] - t < 1.2 and pose != "throw": pose, look = "shock", ((-1 if flip else 1)*0.3, -1)
            bub = next((b[2] for b in sg["bubbles"] if b[0] <= t < b[1]), None)
            return x, y, s, pose, look, flip, bub, blink
        rt = t - sg["reveal"]; P = puzzles[i]
        prevx = side + ((-1 if side > 540 else 1)*200 if (LIMITS[i] >= 5 and sg["throw"]) else 0)
        k = ease_out(rt/0.3); x = prevx + (540 - prevx)*k; y = 1895 - math.sin(min(rt/0.3, 1)*math.pi)*50
        pose = "laugh" if P["catch"] else "idle"
        txt = "GOTCHA!! haha" if P["catch"] else ["too easy?", "did u get it?", "lucky guess", "no way u got that"][i]
        return x, y, 0.95, pose, (0, -1), False, (txt if rt > 0.2 else None), blink
    ot = t - segs[-1]["end"]; k = ease_back(ot/0.4)
    return 540, 1890, 0.95 + 0.5*k, ("wave" if ot < 1.2 else "laugh"), (0, -1), False, ("AGAIN?" if ot > 0.9 else "your score?"), blink

# ---------------- polish layers ----------------
def float_sprites(seed=3):
    r = random.Random(seed); out = []
    for k in range(16):
        s = r.randint(50, 130); im = Image.new("RGBA", (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(im); kind = k % 4
        c = (255, 255, 255, 46)
        if kind == 0: d.ellipse((4, 4, s - 4, s - 4), outline=c, width=max(6, s//9))
        elif kind == 1: d.rounded_rectangle((6, 6, s - 6, s - 6), s//5, outline=c, width=max(6, s//9))
        elif kind == 2:
            w = max(8, s//6); d.rounded_rectangle((s/2 - w/2, 6, s/2 + w/2, s - 6), w//2, fill=c); d.rounded_rectangle((6, s/2 - w/2, s - 6, s/2 + w/2), w//2, fill=c)
        else: d.text((s/2, s/2), "?", font=font(int(s*0.95)), fill=c, anchor="mm")
        out.append(dict(im=im, x=r.uniform(0, W), y=r.uniform(0, H), vy=r.uniform(18, 45), ph=r.uniform(0, 6), amp=r.uniform(10, 30)))
    return out

def vignette_levels():
    yy, xx = np.mgrid[0:H, 0:W]; dx = (xx - W/2)/(W/2); dy = (yy - H/2)/(H/2)
    d = np.clip((np.sqrt(dx**2*1.1 + dy**2*0.75) - 0.62)/0.5, 0, 1)**1.6
    out = []
    for k in range(1, 6):
        a = (d*150*k/5).astype(np.uint8); im = Image.new("RGBA", (W, H), (230, 20, 40, 0)); im.putalpha(Image.fromarray(a)); out.append(im)
    return out

CONF_COL = [(255, 214, 64), (46, 204, 113), (52, 152, 219), (231, 76, 60), (155, 89, 182), (255, 255, 255)]
def confetti_params(seed, cx, cy, n=70):
    r = random.Random(seed)
    return [dict(vx=r.uniform(-900, 900), vy=r.uniform(-1500, -500), c=r.choice(CONF_COL), w=r.uniform(12, 22), h=r.uniform(7, 12),
                 rot=r.uniform(0, 6), vr=r.uniform(-12, 12), x=cx, y=cy) for _ in range(n)]

def draw_confetti(fr, parts, u):
    if u < 0 or u > 1.8: return
    d = ImageDraw.Draw(fr); g = 2600; fade = 1 if u < 1.3 else 1 - (u - 1.3)/0.5
    for p in parts:
        x = p["x"] + p["vx"]*u*0.85; y = p["y"] + p["vy"]*u + 0.5*g*u*u
        if y > H + 20: continue
        a = p["rot"] + p["vr"]*u; c, s_ = math.cos(a), math.sin(a); w, h = p["w"], p["h"]*abs(math.cos(a*1.7))
        pts = [(x + c*dx - s_*dy, y + s_*dx + c*dy) for dx, dy in ((-w/2, -h/2), (w/2, -h/2), (w/2, h/2), (-w/2, h/2))]
        d.polygon(pts, fill=p["c"] + (int(255*fade),))

def pill(txt, col=(255, 255, 255), bg=(30, 20, 60, 170), size=54):
    t = text_layer(txt, 900, 80, size, fill=col); im = rounded((t.width + 70, t.height + 34), (t.height + 34)//2, bg)
    im.alpha_composite(t, (35, 17)); return im

# ---------------- video ----------------
def make_video(puzzles, out, sfx):
    segs, total = build_timeline(puzzles); NF = int(round(total*FPS))
    bgs = [gradient(*LV_BG[k]).convert("RGBA") for k in range(3)]
    sprites = float_sprites(); vig = vignette_levels()
    CX, CY = 540, 800
    TPOS = [(85, 1270), (555, 1270), (85, 1460), (555, 1460)]
    for sg in segs:
        P = puzzles[sg["i"]]; i = sg["i"]
        sg["cq"], sg["ca"] = card_layer(P["q"]), card_layer(P["a"])
        sg["qt"] = text_layer(P["question"], 990, 190, 84, stroke=7)
        sg["tiles"] = [[tile(k, o, s) for s in ("normal", "right", "dim")] for k, o in enumerate(P["options"])]
        bt = text_layer(P["banner"], 860, 90, 66, fill=DARK); b = rounded((bt.width + 80, bt.height + 50), 60, (255, 210, 0, 255))
        b.alpha_composite(bt, (40, 25)); sg["banner"] = b
        sg["big"] = text_layer(f"LEVEL {i+1}", 1000, 260, 220, stroke=12)
        sg["sub"] = text_layer(f"{LV_NAME[i]}  ·  {LIMITS[i]:g} SECONDS", 900, 90, 66, stroke=6)
        sg["icon"] = emoji(LV_ICON[i], 200)
        sg["splat"], sg["drips"] = splat(i*13 + 5, 400)
        cx_, cy_ = TPOS[P["correct"]]; sg["conf"] = confetti_params(i*7 + 1, cx_ + TW/2, cy_ + TH/2)
        if P.get("pre_label"): sg["plabel"] = pill(P["pre_label"], (255, 225, 40))
        sg["mini"] = scaled(card_layer(P["q"]), 0.42)
    gotcha = text_layer("GOTCHA!", 700, 200, 150, fill=(235, 40, 50), stroke=12, stroke_fill="white").rotate(12, expand=True, resample=Image.BICUBIC)
    hook1 = text_layer(HOOK_LINE, 1000, 160, 120, fill=(255, 225, 40), stroke=12)
    hook2 = text_layer("LEVEL 3", 1000, 300, 260, stroke=14)
    hook3 = pill("keep score!", (255, 255, 255), size=50)
    out1 = text_layer("WHAT'S YOUR\nSCORE?", 1000, 400, 160, stroke=12)
    out2 = text_layer("comment 0/3 ... 3/3", 900, 90, 70, fill=(255, 225, 40), stroke=7)
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
    bubs = {}; tom = tomato(200)
    timer_cache = {}
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-", "-i", sfx, "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", out]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in range(NF):
        t = f/FPS
        H0 = _h0()
        sg = next((s for s in segs if t < s["end"]), None) if t >= H0 else None
        li = sg["i"] if sg else (2 if t >= H0 else -1)
        # ---- background: gradient + drifting translucent shapes
        if t < H0: bg = bgs[-1]
        elif sg and t < sg["intro"] + 0.35 and not (HOOK_FIRST and sg["i"] == 0):
            prev = bgs[-1] if sg["i"] == 0 else bgs[sg["i"] - 1]; bg = Image.blend(prev, bgs[sg["i"]], (t - sg["intro"])/0.35)
        else: bg = bgs[li]
        fr = bg.copy()
        for sp in sprites:
            y = (sp["y"] - sp["vy"]*t) % (H + 200) - 100; x = sp["x"] + sp["amp"]*math.sin(t*0.8 + sp["ph"])
            fr.alpha_composite(sp["im"], (int(x), int(y)))
        # ---- level bar
        cur, pulse = (min(2, int(t/0.3)), 0) if t < H0 else (li, (math.sin(t*2*math.pi*2.2) + 1)/2)
        fr.alpha_composite(bar(cur, pulse), (40, 25))
        # ---- content
        if t < H0:
            for k in range(len(segs)):  # teaser: the puzzles fanned out behind the hook text
                kk = ease_back((t - 0.06*k)/0.4)
                if kk <= 0: continue
                ang = (k - 1)*12 + 3*math.sin(t*3 + k)
                m = segs[k]["mini"].rotate(ang, expand=True, resample=Image.BILINEAR)
                paste_center(fr, with_alpha(scaled(m, max(0.01, kk*1.12)), 0.92), 540 + (k - 1)*290, 1270 + abs(k - 1)*50)
            k1 = ease_back(t/0.3); paste_center(fr, scaled(hook1, max(0.01, k1)), 540, 560)
            k2 = ease_back((t - 0.25)/0.35)
            if k2 > 0: paste_center(fr, scaled(hook2, max(0.01, k2*(1 + 0.04*math.sin(t*40)))), 540 + 6*math.sin(t*55), 760)
            if t > 0.7: paste_center(fr, with_alpha(hook3, min(1, (t - 0.7)/0.2)), 540, 960)
        elif sg is None:
            ot = t - segs[-1]["end"]; k = ease_back(ot/0.4)
            paste_center(fr, scaled(out1, max(0.01, k)), 540, 720)
            paste_center(fr, with_alpha(out2, min(1, max(0, (ot - 0.3)/0.3))), 540, 1010)
        elif t < sg["pstart"]:
            lt = t - sg["intro"]; k = ease_back(lt/0.35)
            paste_center(fr, scaled(sg["icon"], max(0.01, k)), 540, 560)
            paste_center(fr, scaled(sg["big"], max(0.01, k)), 540, 820)
            paste_center(fr, with_alpha(sg["sub"], min(1, max(0, (lt - 0.15)/0.25))), 540, 1010)
        else:
            P = puzzles[li]; pt = t - sg["pstart"]; st = t - sg["start"]; rev = t >= sg["reveal"]; rt = t - sg["reveal"]
            in_pre = t < sg["start"]; hf = HOOK_FIRST and li == 0; pa = pt + (1.0 if hf else 0)
            qa = ease_out(pa/0.25)
            if hf and pt < 2.65:   # hook line sits where the header goes, shrinks away, then the header pops in
                hk = (1 + 0.04*math.sin(t*9)) if pt < 2.5 else max(0.01, 1 - (pt - 2.5)/0.15)
                paste_center(fr, scaled(hook1, hk), 540, 300)
            elif hf and pt < 3.0: paste_center(fr, scaled(sg["qt"], max(0.01, ease_back((pt - 2.65)/0.35))), 540, 300)
            else: paste_center(fr, with_alpha(sg["qt"], qa), 540, 300 - 40*(1 - qa))
            # card: slide in from right, out to left at the very end
            k_in = ease_back(pa/0.45); k_out = ease_out((t - (sg["end"] - 0.32))/0.32) if t > sg["end"] - 0.32 else 0
            cx = CX + (1 - k_in)*900 - k_out*1000; rotd = (1 - k_in)*-8 + k_out*6
            if in_pre: L = card_layer(P["anim"](pt))
            elif not rev: L = sg["cq"]
            else:
                kk = min(rt/0.22, 1); L = Image.blend(sg["cq"], sg["ca"], kk) if kk < 1 else sg["ca"]
            s = 1 + (0.05*math.sin(min(rt/0.35, 1)*math.pi) if rev else 0)
            if abs(rotd) > 0.2: L = L.rotate(rotd, expand=True, resample=Image.BILINEAR)
            paste_center(fr, scaled(L, s), cx, CY)
            if in_pre and "plabel" in sg:
                pl = scaled(sg["plabel"], 1 + 0.06*math.sin(t*8)); paste_center(fr, with_alpha(pl, min(1, pt/0.3)), 540, 1330)
            if not in_pre and not rev:
                rem = sg["reveal"] - t; lim = LIMITS[li]; key = (li, round(rem, 1))
                if key not in timer_cache:
                    T = Image.new("RGBA", (200, 200), (0, 0, 0, 0)); td = ImageDraw.Draw(T)
                    td.ellipse((5, 5, 195, 195), fill="white")
                    colr = (231, 76, 60) if rem < 1.5 else LV[li]
                    td.arc((15, 15, 185, 185), -90, -90 + 360*rem/lim, fill=colr, width=16)
                    td.text((100, 104), f"{rem:.1f}", font=font(62), fill=colr, anchor="mm"); timer_cache[key] = T
                sc = 0.82*(1 + (0.1*abs(math.sin(t*math.pi*4)) if rem < 1.5 else 0)) * ease_back(min(1, st/0.3))
                paste_center(fr, scaled(timer_cache[key], max(0.01, sc)), 965, 440)
                if rem < 1.5:  # danger vignette pulse
                    lvl = int(1 + 4*abs(math.sin(t*math.pi*2)))
                    fr.alpha_composite(vig[min(4, lvl - 1)])
            if not in_pre:
                for k, (x, y) in enumerate(TPOS):
                    kk = ease_out((st - 0.05*k)/0.28)
                    if kk <= 0: continue
                    im = sg["tiles"][k][0] if not rev else (sg["tiles"][k][1] if k == P["correct"] else sg["tiles"][k][2])
                    if rev and k == P["correct"]: im = scaled(im, 1 + 0.08*math.sin(min(rt/0.3, 1)*math.pi))
                    if rev and k != P["correct"] and rt < 0.3: x += 10*math.sin(rt*60)*(1 - rt/0.3)
                    xo = -k_out*1000
                    fr.alpha_composite(with_alpha(im, kk*(1 - k_out)), (int(x + xo + TW/2 - im.width/2), int(y + 80*(1 - kk) + (TH - im.height)/2)))
            if rev:
                draw_confetti(fr, sg["conf"], rt)
                if rt >= 0.1:
                    kk = ease_back((rt - 0.1)/0.35); paste_center(fr, with_alpha(scaled(sg["banner"], max(0.01, kk)), 1 - k_out), 540 - k_out*1000, 1210)
                if P["catch"] and rt >= 0.05:
                    kk = min(1, (rt - 0.05)/0.18); gs = 2.4 - 1.4*ease_out(kk)
                    paste_center(fr, with_alpha(scaled(gotcha, gs), min(1, kk*2)*(1 - k_out)), 330, 520)
        # ---- mascot
        x, y, s, pose, look, flip, btxt, blink = mascot_state(t, segs, total, puzzles)
        m = mimg(pose, look, blink, s, flip)
        fr.alpha_composite(m, (int(x - m.width/2), int(y - 290*s)))
        if btxt:
            if btxt not in bubs: bubs[btxt] = {tl: bubble(btxt, font, tl) for tl in ("down", "sideL", "sideR")}
            in_puzzle = sg is not None and t >= sg["pstart"]
            if in_puzzle:
                tail = "sideL" if x <= 560 else "sideR"; bb = bubs[btxt][tail]
                bx = x + 125*s if tail == "sideL" else x - 125*s - bb.width
                by = max(1650, y - 175*s - bb.height/2)
            else:
                bb = bubs[btxt]["down"]; bx = x - bb.width/2; by = y - 290*s - bb.height + 30
            bx = min(max(bx, 10), W - bb.width - 10)
            fr.alpha_composite(bb, (int(bx), int(by)))
        # ---- tomato + splat
        shake = (0, 0)
        if sg is not None and t >= sg["start"] and sg["throw"]:
            hx = x + (-1 if flip else 1)*123*0.92; hy = y - 220*0.92
            u = (t - sg["throw"])/0.42; scr = sg["mode"] == "screen"
            if 0 <= u < 1:
                tx, ty = sg["target"]; hy2 = hy if scr else max(hy, 1725)
                px = hx + (tx - hx)*u; py = hy2 + (ty - hy2)*u - (260 if scr else 40)*math.sin(math.pi*u)
                ti = scaled(tom, 0.3 + (0.9 if scr else 0.45)*u**2).rotate(-u*540, expand=True, resample=Image.BILINEAR); paste_center(fr, ti, px, py)
            sp = t - sg["splat_at"]; stay = sg["stay"]
            if 0 <= sp < stay + 0.3:
                a = 1 if sp < stay else 1 - (sp - stay)/0.3
                img = sg["splat"].copy(); dd = ImageDraw.Draw(img)
                for dx, dw in sg["drips"]:
                    ln = min(1, sp/(stay + 0.3))*img.height*0.25
                    dd.rounded_rectangle((dx - dw/2, img.width*0.5, dx + dw/2, img.width*0.5 + ln), int(dw/2), fill=(214, 32, 38, 255))
                sq = 1.08 - 0.08*ease_out(sp/0.12)
                tx, ty = sg["target"]; si = with_alpha(scaled(img, sq*(1.0 if scr else 0.8)), a)
                if a < 1: si = si.crop((0, 0, si.width, si.height)); 
                fr.alpha_composite(si, (int(tx - si.width/2), int(ty - si.width/2 + (1 - a)*120)))
                if sp < 0.18: amp = 16*(1 - sp/0.18); shake = (int(amp*math.sin(t*170)), int(amp*math.cos(t*130)))
        rgb = fr.convert("RGB")
        if sg is not None and t >= sg["reveal"] and t - sg["reveal"] < 0.2:
            rgb = Image.blend(rgb, Image.new("RGB", (W, H), (255, 255, 255)), 0.45*(1 - (t - sg["reveal"])/0.2))
        if t < 0.12 and not HOOK_FIRST: rgb = Image.blend(rgb, Image.new("RGB", (W, H), (255, 255, 255)), 0.7*(1 - t/0.12))
        if shake != (0, 0):
            sh = Image.new("RGB", (W, H)); sh.paste(rgb, shake); rgb = sh
        ff.stdin.write(rgb.tobytes())
    ff.stdin.close(); ff.wait()
    return segs, total

# ---------------- audio ----------------
def make_sfx(puzzles, path):
    segs, total = build_timeline(puzzles); sr = 44100; N = int(sr*(total + 0.3)); a = np.zeros(N); mus = np.zeros(N)
    rng = np.random.default_rng(3)
    def add(sig, t, buf=a):
        i = int(t*sr); n = min(len(sig), N - i)
        if n > 0 and i >= 0: buf[i:i + n] += sig[:n]
    def tt_(dur): return np.arange(int(dur*sr))/sr
    def env(n, dec): return np.exp(-np.arange(n)/(sr*dec))
    def lp(x, k=8): return np.convolve(x, np.ones(k)/k, mode="same")
    def tick(t, fr, amp=0.5):
        x = tt_(0.07); add((amp*np.sin(2*np.pi*fr*x) + rng.standard_normal(len(x))*0.1)*env(len(x), 0.012), t)
    def whoosh(t, dur=0.5, amp=0.5):
        x = rng.standard_normal(int(dur*sr)); e = np.sin(np.linspace(0, np.pi, len(x)))**2; add(amp*lp(x, 6)*e, t)
    def pop(t, amp=0.5):
        x = tt_(0.12); add(amp*np.sin(2*np.pi*(400*x + 3000*x**2))*env(len(x), 0.04), t)
    def boing(t):
        x = tt_(0.35); f = 220 + 160*np.exp(-x*8); add(0.35*np.sin(2*np.pi*np.cumsum(f)/sr*(1 + 0.04*np.sin(2*np.pi*18*x)))*env(len(x), 0.12), t)
    def splat_s(t):
        x = rng.standard_normal(int(0.28*sr)); add(0.9*lp(x, 30)*env(len(x), 0.07), t)
        y = tt_(0.2); add(0.6*np.sin(2*np.pi*(120*y - 150*y**2))*env(len(y), 0.06), t)
    def chime(t):
        for j, fr in enumerate([1046.5, 1318.5, 1568.0, 2093.0]):
            x = tt_(1.3); add(0.2*(np.sin(2*np.pi*fr*x) + 0.3*np.sin(4*np.pi*fr*x))*env(len(x), 0.4), t + j*0.06)
    def confetti_s(t):
        for j in range(10):
            x = rng.standard_normal(int(0.03*sr)); add(0.12*lp(x, 2)*env(len(x), 0.006), t + 0.05 + j*0.035 + rng.uniform(0, 0.02))
    def laugh(t):
        for j in range(5):
            x = tt_(0.11); f0 = 520 - j*30
            sig = np.sign(np.sin(2*np.pi*f0*x))*0.5 + np.sin(2*np.pi*f0*2*x)*0.5
            add(0.18*lp(sig, 4)*np.sin(np.linspace(0, np.pi, len(x))), t + j*0.13)
    def buzz(t):
        for j, f0 in enumerate([220, 165]):
            x = tt_(0.28); add(0.22*lp(np.sign(np.sin(2*np.pi*f0*x)), 3)*env(len(x), 0.2), t + j*0.26)
    def riser(t, dur):
        x = tt_(dur); f = 200 + 1800*(x/dur)**2; add(0.25*np.sin(2*np.pi*np.cumsum(f)/sr)*(x/dur), t); whoosh(t, dur, 0.25)
    def hit(t):
        x = tt_(0.5); add(0.8*np.sin(2*np.pi*(60*x))*env(len(x), 0.15), t); whoosh(t, 0.25, 0.4)
    def heartbeat(t):
        for d_, g in ((0, 0.55), (0.16, 0.4)):
            x = tt_(0.18); add(g*np.sin(2*np.pi*(55 + 30*np.exp(-x*30))*x)*env(len(x), 0.05), t + d_)
    hit(0.0); pop(0.05)
    if not HOOK_FIRST: riser(0.25, 0.6); hit(0.85); laugh(1.1)
    for k in range(4): pop(0.05 + 0.05*k, 0.3)
    for sg in segs:
        i = sg["i"]; P = puzzles[i]; whoosh(sg["intro"], 0.45, 0.6); pop(sg["intro"] + 0.1)
        whoosh(sg["pstart"], 0.3, 0.45)
        for st_ in P.get("sfx_times", []): whoosh(sg["pstart"] + st_, 0.28, 0.35); pop(sg["pstart"] + st_ + 0.05, 0.25)
        boing(sg["start"] + 0.05)
        step = [1.0, 0.5, 0.5, 0.25][i]; t = sg["start"]; k = 0
        while t < sg["reveal"] - 0.05:
            rem = sg["reveal"] - t; tick(t, 1300 if rem > 1.5 else 1800, 0.5 if k % 2 == 0 else 0.33)
            t += step if rem > 1.5 else 0.25; k += 1
        heartbeat(sg["reveal"] - 1.45); heartbeat(sg["reveal"] - 0.75)
        if sg["throw"]:
            whoosh(sg["throw"], 0.3, 0.5); splat_s(sg["splat_at"])
            if LIMITS[i] >= 5:
                for j in range(3): boing(sg["throw"] + 0.6 + j*0.27)
        for b in sg["bubbles"]: pop(b[0])
        chime(sg["reveal"]); confetti_s(sg["reveal"])
        if P["catch"]: buzz(sg["reveal"] + 0.05); laugh(sg["reveal"] + 0.35)
        else: boing(sg["reveal"])
        whoosh(sg["end"] - 0.32, 0.35, 0.5)
    end = segs[-1]["end"]; hit(end); laugh(end + 0.5)
    for j, fr in enumerate([523.3, 659.3, 784.0, 1046.5]):
        x = tt_(1.0); add(0.2*np.sin(2*np.pi*fr*x)*env(len(x), 0.3), end + 0.1 + j*0.08)
    bpm = 124; beat = 60/bpm; bass_notes = [55.0, 55.0, 65.4, 49.0]; b = 0; t = 0.85
    while t < total - 0.2:
        x = tt_(0.25); add(0.55*np.sin(2*np.pi*(50 + 90*np.exp(-x*30))*x)*env(len(x), 0.08), t, mus)
        h = rng.standard_normal(int(0.04*sr)); h = h - lp(h, 4); add(0.12*h*env(len(h), 0.01), t + beat/2, mus)
        x = tt_(beat*0.9); f0 = bass_notes[(b//4) % 4]
        add(0.22*np.sin(2*np.pi*f0*x)*np.minimum(1, x*40)*env(len(x), 0.25), t, mus)
        t += beat; b += 1
    duck = np.ones(N)
    for sg in segs:
        i0, i1 = int(sg["reveal"]*sr), int((sg["reveal"] + 0.9)*sr); duck[i0:i1] = 0.35
        if sg["pre"]: duck[int(sg["pstart"]*sr):int(sg["start"]*sr)] = 0.6
    out = a + mus*duck*0.7; out = out/np.abs(out).max()*0.9
    s = (np.stack([out, out], 1)*32767).astype(np.int16)
    with wave.open(path, "wb") as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes(s.tobytes())

if __name__ == "__main__":
    from puzzles5 import GENS
    names = sys.argv[1:4]
    puzzles = [GENS[n](500 + i*13, i) for i, n in enumerate(names)]
    make_sfx(puzzles, "/home/claude/shorts/sfx_v5.wav")
    segs, total = make_video(puzzles, "/home/claude/shorts/sample_v5.mp4", "/home/claude/shorts/sfx_v5.wav")
    print("total", round(total, 1))
    for i, P in enumerate(puzzles): print(i + 1, names[i], P["options"], "->", P["options"][P["correct"]])
