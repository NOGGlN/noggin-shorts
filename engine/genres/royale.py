"""Battle royale: contestant balls in a ring with a spinning gap; whoever slips out is OUT, last one inside wins.
spec["contestants"] = [["PORTUGAL", "🇵🇹"], ...] (12-24), spec["headline"] = ["16 COUNTRIES. 1 RING.", "ONLY 1 SURVIVES"],
spec["label"] = "BATTLE ROYALE" (small title), spec["pick_line"] = "PICK YOUR COUNTRY NOW".
Video (16:9): ring centre, standings left, alive + feed right.  Short (9:16): ring top, standings grid below.
"""
import math
import numpy as np
from PIL import Image, ImageDraw
import gcommon as g

def is_flag(e): return len(e) >= 2 and all(0x1F1E6 <= ord(c) <= 0x1F1FF for c in e[:2])

def simulate(N, CX, CY, R, r, seed, grow, max_t=80.0, sub=8):
    rng = np.random.default_rng(seed); dt = 1/(g.FPS*sub)
    p = np.zeros((N, 2)); placed = 0; tries = 0
    while placed < N and tries < 20000:
        tries += 1; a = rng.uniform(0, 2*np.pi); d = rng.uniform(0, R - r - 10); q = np.array([CX + d*np.cos(a), CY + d*np.sin(a)])
        if all(np.hypot(*(q - p[j])) > 2*r + 4 for j in range(placed)): p[placed] = q; placed += 1
    ang = rng.uniform(0, 2*np.pi, N); v = np.stack([np.cos(ang), np.sin(ang)], 1)*480
    alive = np.ones(N, bool); out_t = np.full(N, -1.0); falling = np.zeros(N, bool); frames = []; ev = []; t = 0.0
    iu, ju = np.triu_indices(N, 1)
    while t < max_t:
        for _ in range(sub):
            t += dt; gc_ = 0.9*t; gw = 0.30 + grow*t; speed = 480 + 6*t
            v[falling, 1] += 1800*dt; p += v*dt
            for i in np.where(alive)[0]:
                d = p[i] - (CX, CY); dist = math.hypot(*d)
                if dist > R - r:
                    a = math.atan2(d[1], d[0]); diff = (a - gc_ + math.pi) % (2*math.pi) - math.pi
                    if abs(diff) < gw:
                        if dist > R + r: alive[i] = False; falling[i] = True; out_t[i] = t; ev.append((t, "out", i))
                    else:
                        n = d/dist; vn = v[i] @ n
                        if vn > 0: v[i] -= 2*vn*n; ev.append((t, "wall", i))
                        p[i] = (CX, CY) + n*(R - r)
            d = p[ju] - p[iu]; dd = np.sqrt((d**2).sum(1)); m = (dd < 2*r) & (dd > 0) & alive[iu] & alive[ju]
            for k in np.where(m)[0]:
                i, j = iu[k], ju[k]; n = d[k]/dd[k]; rel = (v[i] - v[j]) @ n
                if rel > 0: v[i] -= rel*n; v[j] += rel*n
                ov = 2*r - dd[k]; p[i] -= n*ov/2; p[j] += n*ov/2
            sp = np.hypot(v[:, 0], v[:, 1]); v[alive] *= (speed/np.maximum(sp, 1))[alive, None]
        frames.append((p.copy(), alive.copy(), 0.9*t, 0.30 + grow*t))
        if alive.sum() == 1: return frames, ev, out_t, t
    return None

def build(spec, fmt):
    W, H = g.W, g.H; vert = fmt == "short"; C = spec["contestants"]; N = len(C)
    if vert: CX, CY, R = W/2, 800, 470
    else: CX, CY, R = 960, 575, 395
    r = int(min(44, max(30, R*0.105*(16/N)**0.5)))
    lo, hi, grow = (14.0, 19.0, 0.014) if vert else (26.0, 38.0, 0.006)
    if N > 18 and not vert: lo, hi = 30.0, 42.0
    res = None
    for seed in range(int(spec.get("seed", 1)), int(spec.get("seed", 1)) + 600):
        res = simulate(N, CX, CY, R, r, seed, grow)
        if res and lo < res[3] < hi: break
        res = None
    if not res: raise SystemExit("no battle seed found in range; try other contestants or seed")
    FR, EV, OUT, END = res; T0 = 2.4; DUR = T0 + END + 4.0
    WIN = int(np.where(FR[-1][1])[0][0]); order = sorted([i for i in range(N) if OUT[i] > 0], key=lambda i: OUT[i])
    place = {i: N - k for k, i in enumerate(order)}; place[WIN] = 1
    K = g.Kicks(); [K.add(T0 + t, 0.5) for t, kind, i in EV if kind == "out"]; K.add(T0 + END, 1.4, True); K.add(0.1, 1.0, True); K.add(0.8, 0.8)
    BG = g.gradient((18, 22, 60), (60, 20, 70)); ST = g.stripes(7)
    SPR = [g.ball(e, r, full=is_flag(e)) for _, e in C]
    head1, head2 = spec.get("headline", [f"{N} CONTESTANTS. 1 RING.", "ONLY 1 SURVIVES"])
    label = spec.get("label", "BATTLE ROYALE"); pick_line = spec.get("pick_line", "PICK YOUR WINNER NOW")

    def ring(im, gc_, gw):
        d = ImageDraw.Draw(im)
        d.ellipse((CX - R - 24, CY - R - 24, CX + R + 24, CY + R + 24), fill=(255, 150, 60, 255))
        d.ellipse((CX - R - 10, CY - R - 10, CX + R + 10, CY + R + 10), fill=(60, 30, 70, 255))
        d.ellipse((CX - R, CY - R, CX + R, CY + R), fill=(16, 14, 34, 255))
        d.arc((CX - R - 8, CY - R - 8, CX + R + 8, CY + R + 8), math.degrees(gc_ + gw), math.degrees(gc_ - gw) + 360, fill=(255, 255, 255), width=14)

    def frame(t):
        im = BG.copy(); off = int((t*50) % 90); im.alpha_composite(ST.crop((off, 0, off + W, H)))
        st = t - T0; fi = min(len(FR) - 1, max(0, int(st*g.FPS)))
        pos, alive, gc_, gw = FR[fi] if st >= 0 else (FR[0][0], FR[0][1], 0, 0.30)
        ring(im, gc_, gw)
        for i in range(N):
            x, y = pos[i]
            if -100 < y < H + 100: g.paste(im, SPR[i], x, y)
        d = ImageDraw.Draw(im); n_alive = int(alive.sum()) if st >= 0 else N
        is_out = lambda k: st >= 0 and OUT[k] > 0 and st >= OUT[k]
        if not vert:
            rows = N; rh = min(54, 860/rows); fs = int(min(34, rh*0.62))
            d.rounded_rectangle((40, 140, 470, 150 + rows*rh + 20), 24, fill=(10, 8, 24, 210))
            for k, (nm, e) in enumerate(C):
                y = 172 + k*rh; o = is_out(k)
                g.paste(im, g.emoji(e, int(rh*0.72)), 92, y, alpha=0.35 if o else 1)
                g.paste(im, g.T(nm, fs, (120, 110, 140) if o else g.WHITE, 0, maxw=240), 130, y, anchor="l")
                if o: g.paste(im, g.T(f"#{place[k]}", int(fs*0.95), g.RED, 0), 440, y, anchor="r"); d.line((128, y, 360, y), fill=(255, 92, 92), width=4)
            ax, ay = 1650, 210
            g.paste(im, g.T("ALIVE", 48, g.WHITE, 7), ax, ay)
            last = [st - OUT[i] for i in range(N) if 0 < OUT[i] <= st]; pop = 1 + 0.25*max(0, 1 - (min(last) if last else 9)/0.25)
            g.paste(im, g.T(str(n_alive), 150, g.YEL, 12), ax, ay + 120, pop)
            feed = [i for i in order if OUT[i] <= st][-4:]
            for k, i in enumerate(reversed(feed)):
                y = 500 + k*80; a = 1 - k*0.22
                g.paste(im, g.emoji(C[i][1], 44), 1470, y, alpha=a); g.paste(im, g.T(f"{C[i][0]} OUT", 40, g.RED, 6, maxw=360), 1505, y, anchor="l", alpha=a)
        else:
            g.paste(im, g.T(label, 64, g.YEL, 8, maxw=W - 80), W/2, 110)
            last = [st - OUT[i] for i in range(N) if 0 < OUT[i] <= st]; pop = 1 + 0.25*max(0, 1 - (min(last) if last else 9)/0.25)
            g.paste(im, g.T(f"ALIVE {n_alive}", 72, g.WHITE, 9), W/2, 200, pop)
            cols = 3; rows_ = math.ceil(N/cols); rh = min(64, 560/rows_); fs = int(min(36, rh*0.6)); cw = (W - 80)/cols
            d.rounded_rectangle((30, 1340, W - 30, 1340 + rows_*rh + 30), 24, fill=(10, 8, 24, 210))
            for k, (nm, e) in enumerate(C):
                cx_ = 40 + (k % cols)*cw; y = 1370 + (k//cols)*rh; o = is_out(k)
                g.paste(im, g.emoji(e, int(rh*0.66)), cx_ + 34, y, alpha=0.35 if o else 1)
                g.paste(im, g.T(nm, fs, (120, 110, 140) if o else g.WHITE, 0, maxw=cw - 120), cx_ + 66, y, anchor="l")
                if o: g.paste(im, g.T(f"#{place[k]}", int(fs*0.85), g.RED, 0), cx_ + cw - 14, y, anchor="r")
        if 2 <= n_alive <= 3 and st < END: g.paste(im, g.T(f"LAST {n_alive}!", 90, g.RED, 10), CX, CY + R + 70 if not vert else CY + R + 70, 1 + 0.06*math.sin(t*12))
        if t < T0 + 0.6:
            a = 1 - g.ease((t - T0)/0.6); im.alpha_composite(Image.new("RGBA", (W, H), (8, 6, 20, int(170*a))))
            g.paste(im, g.T(head1, 110, g.WHITE, 12, maxw=W - 80), W/2, H/2 - 210, g.back((t - 0.1)/0.25), alpha=a)
            g.paste(im, g.T(head2, 130, g.RED, 12, maxw=W - 80), W/2, H/2 - 60, g.back((t - 0.8)/0.25), rot=-3, alpha=a)
            g.paste(im, g.T(pick_line, 64, g.YEL, 8, maxw=W - 80), W/2, H/2 + 100, g.back((t - 1.4)/0.25), alpha=a)
        elif not vert: g.paste(im, g.T(label, 56, g.YEL, 7), CX, 80)
        if st >= END:
            k = st - END; im.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(150*g.ease(k/0.4))))); dd = ImageDraw.Draw(im)
            g.paste(im, g.ball(C[WIN][1], 170, full=is_flag(C[WIN][1])), W/2, H/2 - 70, g.back(k/0.4), rot=math.sin(t*3)*5)
            g.paste(im, g.T(f"{C[WIN][0]} WINS!", 130, g.YEL, 12, maxw=W - 80), W/2, H/2 + 200, g.back((k - 0.2)/0.3))
            g.paste(im, g.T("DID YOU PICK IT? COMMENT BELOW", 56, g.WHITE, 7, maxw=W - 80), W/2, H/2 + 330, g.back((k - 0.6)/0.3))
            for j in range(30):
                a = j*2.39; vv = 300 + (j*53) % 400; x = W/2 + math.cos(a)*vv*k; y = H/2 - 70 + math.sin(a)*vv*k + 500*k*k
                dd.rectangle((x - 9, y - 6, x + 9, y + 6), fill=[g.RED, g.YEL, g.GRN, g.BLU, g.WHITE][j % 5] + (255,))
        pose = "laugh" if t < T0 or st >= END else "shock" if 2 <= n_alive <= 3 else "idle"
        g.put_mascot(im, t, pose, (-1, 0), W - 110, H - 120 if not vert else H - 150, 0.62)
        dx, dy = K.shake(t); return g.camera(im, K.zoom(t), dx, dy, K.flash(t), t=t, dur=DUR)

    def audio(path):
        M = g.Mix(DUR); M.add(M.boom(), 0.1); M.add(M.boom(), 0.8, 0.8); M.add(M.ding(), 1.4); M.add(M.whoosh(0.5), T0 - 0.3)
        lw = -1; rng = np.random.default_rng(3)
        for t, kind, i in EV:
            tt = T0 + t
            if kind == "wall" and tt - lw > 0.07: M.add(M.pluck(g.NOTES[rng.integers(4, len(g.NOTES))], 0.12), tt); lw = tt
            if kind == "out": M.add(M.pop(400), tt); M.add(M.thud(70), tt, 0.6)
        M.add(M.boom(), T0 + END); M.fanfare(T0 + END + 0.2); M.save(path)

    info = dict(winner=C[WIN][0], duration=round(DUR, 1))
    return frame, audio, DUR, [1.2, T0 + 4, T0 + END - 1.5, T0 + END + 2], info
