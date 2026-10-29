"""Noggin Battle: a ball battle royale. 16-30 contestants (flags, foods, animals... anything that has an emoji) bounce inside
a ring with a slowly spinning gap. Whoever slips out through the gap is OUT. The last one inside wins.

simulate()  -> runs the physics (deterministic for a seed) and returns per-frame positions and events
render()    -> draws the 1080x1920 30 fps video (pipes frames to ffmpeg) and adds a calm sound track
Normally called by make_battle.py.
"""
import math, os, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
W, H, FPS = 1080, 1920, 30
CX, CY, R = 540, 1030, 470                     # arena centre and inner radius of the ring
FONTS = os.path.join(HERE, "assets", "fonts")
EMOJI = os.path.join(FONTS, "NotoColorEmoji.ttf")
BLACK = os.path.join(FONTS, "Inter-Black.otf"); XBOLD = os.path.join(FONTS, "Inter-ExtraBold.otf")
GOLD, WHITE, RED, INK = (255, 196, 46), (255, 255, 255), (255, 84, 84), (14, 16, 34)
PASTEL = [(255, 214, 165), (189, 224, 254), (202, 255, 191), (255, 198, 255), (253, 255, 182), (155, 246, 255),
          (255, 173, 173), (210, 196, 255), (255, 228, 196), (190, 242, 226)]


def font(path, size): return ImageFont.truetype(path, size)


# ----------------------------------------------------------------------------------------------- physics
def simulate(n, seed, r, gap0=0.36, grow=0.006, spin=0.85, speed0=470.0, accel=5.0, max_t=60.0, sub=8, cool=0.9):
    """Returns dict(frames=[(pos[n,2], state[n], gap_angle, gap_width)], events=[per-frame list], order=[(idx, t)], end=t)."""
    rng = np.random.default_rng(seed)
    pos = np.zeros((n, 2)); k = 0; tries = 0
    while k < n:
        a = rng.uniform(0, 2*math.pi); d = (R - r - 8)*math.sqrt(rng.uniform(0, 1))
        p = np.array([CX + d*math.cos(a), CY + d*math.sin(a)])
        if k == 0 or np.min(np.hypot(*(pos[:k] - p).T)) > 2*r + 6: pos[k] = p; k += 1
        tries += 1
        if tries > 200000: raise RuntimeError("too many balls for the arena")
    ang = rng.uniform(0, 2*math.pi, n); vel = np.stack([np.cos(ang), np.sin(ang)], 1)*speed0
    state = np.zeros(n, int)                     # 0 inside, 1 escaping/falling, 2 gone
    g_ang = rng.uniform(0, 2*math.pi); spin_dir = rng.choice([-1, 1])
    frames, events, order = [], [], []; t = 0.0; dt = 1/FPS/sub; end = None; last_out = 2.0 - cool
    while True:
        ev = []
        for _ in range(sub):
            t += dt
            alive = state == 0; n_alive = int(alive.sum())
            full = gap0 + grow*t + 0.55*(1 - n_alive/n) + (0.2 if n_alive <= 3 else 0.0)
            since = t - last_out                       # the gap snaps shut after each knock-out, then slowly reopens
            gw = full*(0.0 if since < cool else min(1.0, (since - cool)/0.6))
            g_ang = (g_ang + spin_dir*spin*dt) % (2*math.pi)
            sp = speed0 + accel*t
            pos[state < 2] += vel[state < 2]*dt
            fall = state == 1; vel[fall, 1] += 1600*dt                     # escaped balls drop off the screen
            # walls
            for i in np.where(alive)[0]:
                dx, dy = pos[i, 0] - CX, pos[i, 1] - CY; d = math.hypot(dx, dy)
                if d > R - r:
                    a = math.atan2(dy, dx); diff = (a - g_ang + math.pi) % (2*math.pi) - math.pi
                    if gw > 0.05 and abs(diff) < gw/2 - (r*0.8)/R and n_alive > 1:
                        state[i] = 1; order.append((i, t)); ev.append(("out", i)); n_alive -= 1; last_out = t
                        continue
                    nx, ny = dx/d, dy/d; vn = vel[i, 0]*nx + vel[i, 1]*ny
                    if vn > 0: vel[i] -= 2*vn*np.array([nx, ny]); ev.append(("wall", i))
                    pos[i] = [CX + nx*(R - r), CY + ny*(R - r)]
            # ball-ball (equal mass, elastic)
            idx = np.where(state == 0)[0]
            if len(idx) > 1:
                P = pos[idx]; D = P[:, None, :] - P[None, :, :]; dist = np.hypot(D[..., 0], D[..., 1])
                ii, jj = np.where(np.triu(dist < 2*r, 1))
                for a_, b_ in zip(ii, jj):
                    i, j = idx[a_], idx[b_]; dvec = pos[j] - pos[i]; d = max(1e-6, math.hypot(*dvec)); nrm = dvec/d
                    rel = np.dot(vel[i] - vel[j], nrm)
                    if rel > 0: vel[i] -= rel*nrm; vel[j] += rel*nrm; ev.append(("hit", i, j))
                    ov = 2*r - d; pos[i] -= nrm*ov/2; pos[j] += nrm*ov/2
            ins = state == 0
            if ins.any():
                v = np.hypot(vel[ins, 0], vel[ins, 1])[:, None]; vel[ins] = vel[ins]/np.maximum(v, 1e-6)*sp
            gone = (state == 1) & (pos[:, 1] > H + 2*r); state[gone] = 2
        frames.append((pos.copy(), state.copy(), g_ang, gw)); events.append(ev)
        if end is None and int((state == 0).sum()) == 1: end = t
        if end is not None and t > end + 0.4: break
        if t > max_t: return None
    return dict(frames=frames, events=events, order=order, end=end, winner=int(np.where(state == 0)[0][0]))


def find_run(n, r, seed0=1, lo=42.0, hi=54.0, tries=400):
    """Try seeds until the battle finishes between lo and hi seconds."""
    for s in range(seed0, seed0 + tries):
        run = simulate(n, s, r)
        if run and lo <= run["end"] <= hi: run["seed"] = s; return run
    raise RuntimeError("no seed gave a good length")


# ----------------------------------------------------------------------------------------------- sprites
def is_flag(e): return len(e) >= 2 and all(0x1F1E6 <= ord(c) <= 0x1F1FF for c in e[:2]) or e.startswith("\U0001F3F4")


def emoji_img(e, size=136):
    f = font(EMOJI, 109); im = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((10, 10), e, font=f, embedded_color=True)
    bb = im.getbbox(); im = im.crop(bb) if bb else im
    return im


def ball_sprite(e, r, k):
    S = 4; D = 2*r*S; base = Image.new("RGBA", (D, D), (0, 0, 0, 0))
    mask = Image.new("L", (D, D), 0); ImageDraw.Draw(mask).ellipse((0, 0, D - 1, D - 1), fill=255)
    em = emoji_img(e)
    if is_flag(e):
        # crop the waving edges a little and cover the whole ball with the flag
        w, h = em.size; em = em.crop((int(w*0.06), int(h*0.1), int(w*0.94), int(h*0.9)))
        sc = D/min(em.size); em = em.resize((max(D, int(em.size[0]*sc)), max(D, int(em.size[1]*sc))), Image.LANCZOS)
        x0 = (em.size[0] - D)//2; y0 = (em.size[1] - D)//2; fill = em.crop((x0, y0, x0 + D, y0 + D))
        bg = Image.new("RGBA", (D, D), (255, 255, 255, 255)); bg.alpha_composite(fill); base.paste(bg, (0, 0), mask)
    else:
        col = PASTEL[k % len(PASTEL)]; ImageDraw.Draw(base).ellipse((0, 0, D - 1, D - 1), fill=col + (255,))
        s = int(D*0.66)
        sc = s/max(em.size); em = em.resize((max(1, int(em.size[0]*sc)), max(1, int(em.size[1]*sc))), Image.LANCZOS)
        base.alpha_composite(em, ((D - em.size[0])//2, (D - em.size[1])//2))
    # shading: soft dark rim + highlight
    rim = Image.new("L", (D, D), 0); ImageDraw.Draw(rim).ellipse((0, 0, D - 1, D - 1), fill=255)
    inner = Image.new("L", (D, D), 0); ImageDraw.Draw(inner).ellipse((D*0.08, D*0.04, D*0.96, D*0.92), fill=255)
    inner = inner.filter(ImageFilter.GaussianBlur(D*0.06))
    dark = Image.new("RGBA", (D, D), (0, 0, 0, 0)); dark.putalpha(Image.eval(Image.composite(Image.new("L", (D, D), 0), rim, inner), lambda v: int(v*0.45)))
    base.alpha_composite(dark)
    hl = Image.new("L", (D, D), 0); ImageDraw.Draw(hl).ellipse((D*0.18, D*0.08, D*0.55, D*0.36), fill=120)
    hl = hl.filter(ImageFilter.GaussianBlur(D*0.05)); white = Image.new("RGBA", (D, D), (255, 255, 255, 0)); white.putalpha(hl)
    base.alpha_composite(white)
    ImageDraw.Draw(base).ellipse((S, S, D - 1 - S, D - 1 - S), outline=(10, 10, 20, 255), width=3*S)
    out = Image.new("RGBA", (D, D), (0, 0, 0, 0)); out.paste(base, (0, 0), mask)
    return out.resize((2*r, 2*r), Image.LANCZOS)


def text_sprite(txt, f, fill, stroke=4, sc=INK):
    bb = f.getbbox(txt, stroke_width=stroke); im = Image.new("RGBA", (bb[2] - bb[0] + 4, bb[3] - bb[1] + 4), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((2 - bb[0], 2 - bb[1]), txt, font=f, fill=fill, stroke_width=stroke, stroke_fill=sc); return im


def fit_font(txt, path, size, maxw, stroke=0):
    while size > 20 and font(path, size).getlength(txt) + 2*stroke > maxw: size -= 2
    return font(path, size)


def background():
    y = np.linspace(0, 1, H)[:, None]; top = np.array([22, 18, 52]); bot = np.array([70, 26, 60])
    img = (top*(1 - y[..., None]) + bot*y[..., None]).repeat(W, 1).astype(np.uint8)
    im = Image.fromarray(img, "RGB").convert("RGBA"); d = ImageDraw.Draw(im); rng = np.random.default_rng(3)
    for _ in range(140):
        x, yy, s = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(1, 3.2)
        d.ellipse((x - s, yy - s, x + s, yy + s), fill=(255, 255, 255, int(rng.uniform(40, 140))))
    glow = Image.new("L", (W, H), 0); ImageDraw.Draw(glow).ellipse((CX - R - 90, CY - R - 90, CX + R + 90, CY + R + 90), fill=150)
    glow = glow.filter(ImageFilter.GaussianBlur(70)); g = Image.new("RGBA", (W, H), (255, 150, 40, 0)); g.putalpha(Image.eval(glow, lambda v: v//2))
    im.alpha_composite(g)
    d = ImageDraw.Draw(im); d.ellipse((CX - R, CY - R, CX + R, CY + R), fill=(24, 22, 44, 255))
    tex = Image.new("RGBA", (W, H), (0, 0, 0, 0)); td = ImageDraw.Draw(tex)
    for _ in range(90):
        a = rng.uniform(0, 2*math.pi); dd = R*math.sqrt(rng.uniform(0, 0.95)); x, yy = CX + dd*math.cos(a), CY + dd*math.sin(a); s = rng.uniform(6, 22)
        td.ellipse((x - s, yy - s, x + s, yy + s), fill=(255, 255, 255, 10))
    im.alpha_composite(tex)
    return im


# ----------------------------------------------------------------------------------------------- sound
def make_audio(run, n_frames, path, sr=44100):
    import news5
    N = int(sr*(n_frames/FPS + 0.3)); bed = news5.calm_bed(N, sr, seed=5)*0.22; fx = np.zeros(N)
    def add(sig, t):
        i = int(t*sr); m = min(len(sig), N - i)
        if m > 0 and i >= 0: fx[i:i + m] += sig[:m]
    notes = [523.25, 587.33, 659.25, 783.99, 880.0, 1046.5]
    def pluck(f, a, dur=0.35):
        x = np.arange(int(dur*sr))/sr; return a*(np.sin(2*np.pi*f*x) + 0.3*np.sin(4*np.pi*f*x))*np.exp(-x/0.09)*(1 - np.exp(-x*400))
    def pop(a=0.5):
        x = np.arange(int(0.28*sr))/sr; f = 300 + 500*np.exp(-x*18); return a*np.sin(2*np.pi*np.cumsum(f)/sr)*np.exp(-x/0.07)
    last_w = -1; last_h = -1; rng = np.random.default_rng(4)
    for fi, ev in enumerate(run["events"]):
        t = fi/FPS
        if any(e[0] == "out" for e in ev): add(pop(0.55), t)
        if any(e[0] == "wall" for e in ev) and t - last_w > 0.09: add(pluck(notes[rng.integers(len(notes))], 0.13), t); last_w = t
        if any(e[0] == "hit" for e in ev) and t - last_h > 0.12: add(pluck(220*rng.choice([1, 1.25, 1.5]), 0.10, 0.2), t); last_h = t
    te = run["end"] + 0.5
    for k, f in enumerate([523.25, 659.25, 783.99, 1046.5]): add(pluck(f, 0.3, 1.2), te + k*0.13)
    g = np.ones(N); fo = int(1.0*sr); g[-fo:] *= np.linspace(1, 0, fo)
    out = (bed + fx[:, None])*g[:, None]; out = out/np.abs(out).max()*0.85
    with wave.open(path, "wb") as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes((out*32767).astype(np.int16).tobytes())


# ----------------------------------------------------------------------------------------------- render
def render(contestants, headline, run, r, out_mp4, sheet=None, stills=None):
    n = len(contestants); bg = background()
    balls = [ball_sprite(e, r, k) for k, (nm, e) in enumerate(contestants)]
    lab_f = font(XBOLD, 21 if n > 24 else 24)
    labels = [text_sprite(nm.upper(), lab_f, WHITE, 3) for nm, e in contestants]
    l1 = fit_font(headline[0], BLACK, 70, W - 80, 6); l2 = fit_font(headline[1], BLACK, 70, W - 80, 6)
    h1 = text_sprite(headline[0], l1, WHITE, 6); h2 = text_sprite(headline[1], l2, GOLD, 6)
    pill_f = font(BLACK, 44); feed_f = font(XBOLD, 38); big_f = font(BLACK, 110); mid_f = font(BLACK, 64); sm_f = font(XBOLD, 40)
    hook = text_sprite("Pick your winner before it starts!", sm_f, WHITE, 4)
    emo_small = [emoji_img(e) for nm, e in contestants]
    out_time = {i: t for i, t in run["order"]}; rank = {i: n - k for k, (i, t) in enumerate(run["order"])}
    end = run["end"]; win = run["winner"]; tail = 4.2
    nf = len(run["frames"]) + int((tail - 0.4)*FPS)
    tmp = out_mp4[:-4] + ".tmp.mp4"; wav = out_mp4[:-4] + ".wav"
    if stills: nf_list = [int(x*FPS) for x in stills]
    ff = None if stills else subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    pops = []; conf_rng = np.random.default_rng(9)
    conf = [(conf_rng.uniform(0, W), conf_rng.uniform(-600, 0), conf_rng.uniform(-80, 80), conf_rng.uniform(250, 520),
             tuple(int(c) for c in conf_rng.choice([(255, 196, 46), (255, 84, 84), (90, 200, 255), (130, 255, 150), (255, 140, 230)])),
             conf_rng.uniform(0, 6.3)) for _ in range(160)]
    sheet_frames = []; sheet_at = {int(FPS*x) for x in (0.5, end*0.25, end*0.5, end*0.8)} | {nf - int(FPS*1.5)}
    for fi in range(nf):
        if stills and fi > max(nf_list): break
        t = fi/FPS; fr = run["frames"][min(fi, len(run["frames"]) - 1)]; pos, state, g_ang, gw = fr
        im = bg.copy(); d = ImageDraw.Draw(im)
        # ring with the gap
        a0 = math.degrees(g_ang + gw/2); a1 = math.degrees(g_ang - gw/2) + 360
        d.arc((CX - R - 16, CY - R - 16, CX + R + 16, CY + R + 16), a0, a1, fill=(255, 150, 40, 255), width=18)
        d.arc((CX - R - 10, CY - R - 10, CX + R + 10, CY + R + 10), a0, a1, fill=(255, 205, 90, 255), width=5)
        for aa in ((g_ang + gw/2, g_ang - gw/2) if gw > 0.05 else ()):
            x, y = CX + (R + 7)*math.cos(aa), CY + (R + 7)*math.sin(aa); d.ellipse((x - 13, y - 13, x + 13, y + 13), fill=(255, 205, 90, 255))
        # header
        im.alpha_composite(h1, ((W - h1.size[0])//2, 150)); im.alpha_composite(h2, ((W - h2.size[0])//2, 150 + h1.size[1] + 10))
        left = int((state == 0).sum()) if fi < len(run["frames"]) else 1
        pill = text_sprite(f"{left} LEFT", pill_f, WHITE, 0); px = (W - pill.size[0] - 70)//2; py = 150 + h1.size[1] + h2.size[1] + 40
        d.rounded_rectangle((px, py, px + pill.size[0] + 70, py + pill.size[1] + 30), 40, fill=(14, 16, 34, 230), outline=(255, 150, 40, 255), width=5)
        im.alpha_composite(pill, (px + 35, py + 15))
        # balls
        for i in range(n):
            if state[i] == 2: continue
            if fi >= len(run["frames"]) - 1 and i == win and t > end + 0.4: continue
            x, y = pos[i]; im.alpha_composite(balls[i], (int(x - r), int(y - r)))
            lb = labels[i]; im.alpha_composite(lb, (int(x - lb.size[0]/2), int(y + r - 2)))
        ev = run["events"][fi] if fi < len(run["events"]) else []
        for e in ev:
            if e[0] == "out": pops.append((t, "OUT!", pos[e[1]].copy(), RED))
            if e[0] == "hit" and conf_rng.random() < 0.06 and (not pops or t - pops[-1][0] > 0.8):
                i, j = e[1], e[2]; pops.append((t, "BONK!", (pos[i] + pos[j])/2, GOLD))
        keep = []
        for (t0, txt, p, col) in pops:
            age = t - t0
            if age < 0.7:
                s = text_sprite(txt, font(BLACK, int(46 + 30*min(1, age*6))), col, 4); s.putalpha(Image.eval(s.getchannel("A"), lambda v, a=age: int(v*min(1, (0.7 - a)*3))))
                im.alpha_composite(s, (int(p[0] - s.size[0]/2), int(min(H - 120, p[1]) - s.size[1]/2 - 40*age))); keep.append((t0, txt, p, col))
        pops = keep
        # bottom: hook first, then the elimination feed
        fy = CY + R + 70
        if t < run["order"][0][1]:
            im.alpha_composite(hook, ((W - hook.size[0])//2, fy + 20))
        else:
            gone = [(i, tt) for i, tt in run["order"] if tt <= t][-3:][::-1]
            for k, (i, tt) in enumerate(gone):
                em = emo_small[i].resize((46, int(46*emo_small[i].size[1]/emo_small[i].size[0]))); rowy = fy + k*62
                txt = text_sprite(f"#{rank[i]}  OUT:  {contestants[i][0].upper()}", feed_f, WHITE if k == 0 else (200, 200, 215), 3)
                x0 = (W - txt.size[0] - 60)//2; im.alpha_composite(em, (x0, rowy + 4)); im.alpha_composite(txt, (x0 + 60, rowy))
        # winner finale
        if t > end + 0.4:
            u = min(1, (t - end - 0.4)/0.8); e3 = 1 - (1 - u)**3
            x, y = pos[win]; tx, ty = x + (CX - x)*e3, y + (CY - 60 - y)*e3; s = int(2*r*(1 + 2.2*e3))
            veil = Image.new("RGBA", (W, H), (10, 8, 24, int(150*e3))); im.alpha_composite(veil)
            b = balls[win].resize((s, s), Image.LANCZOS); im.alpha_composite(b, (int(tx - s/2), int(ty - s/2)))
            if u >= 1:
                wt = text_sprite("WINNER!", big_f, GOLD, 8); im.alpha_composite(wt, ((W - wt.size[0])//2, int(CY - 60 - s/2 - wt.size[1] - 30)))
                nm = text_sprite(contestants[win][0].upper(), fit_font(contestants[win][0].upper(), BLACK, 72, W - 100, 6), WHITE, 6)
                im.alpha_composite(nm, ((W - nm.size[0])//2, int(CY - 60 + s/2 + 30)))
                cm = text_sprite("Did you pick it? Comment below!", sm_f, WHITE, 4); im.alpha_composite(cm, ((W - cm.size[0])//2, int(CY - 60 + s/2 + 140)))
            tc = t - end - 0.4; d = ImageDraw.Draw(im)
            for (x0, y0, vx, vy, col, ph) in conf:
                cx_, cy_ = x0 + vx*tc + 20*math.sin(tc*3 + ph), y0 + vy*tc
                if 0 < cy_ < H: d.rectangle((cx_ - 6, cy_ - 3, cx_ + 6, cy_ + 3), fill=col + (255,))
        frame = im.convert("RGB")
        if stills:
            if fi in nf_list: frame.save(out_mp4[:-4] + f"_still_{fi}.jpg", quality=90)
            continue
        ff.stdin.write(frame.tobytes())
        if fi in sheet_at: sheet_frames.append(frame.resize((270, 480)))
    if stills: return None
    ff.stdin.close(); ff.wait()
    if ff.returncode: raise RuntimeError("ffmpeg video failed")
    make_audio(run, nf, wav)
    tmp2 = out_mp4[:-4] + ".tmp2.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", tmp, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
                    "-shortest", "-movflags", "+faststart", tmp2], check=True)
    os.replace(tmp2, out_mp4); os.remove(tmp); os.remove(wav)
    if sheet:
        sh = Image.new("RGB", (270*len(sheet_frames), 480), "grey")
        for k, f in enumerate(sheet_frames): sh.paste(f, (270*k, 0))
        sh.save(sheet)
    return nf/FPS
