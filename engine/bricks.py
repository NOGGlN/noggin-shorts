"""Noggin Brick Race: two emoji balls, each bouncing in its own ring. Every bounce adds a brick to the wall where it hit,
so each ring slowly walls itself in. The first ball that gets walled in LOSES; the one still free wins.

simulate_arena()  -> physics for one ring (deterministic for a seed)
find_race()       -> picks two seeds that give a close, 30-50 s race
render()          -> 1080x1920 30 fps video + sound (normally called by make_bricks.py)
"""
import math, os, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import battle
from battle import font, text_sprite, fit_font, ball_sprite, emoji_img, BLACK, XBOLD, GOLD, WHITE, RED, INK

W, H, FPS = 1080, 1920, 30
R = 315                                   # inner radius of each ring
BR = 30                                   # ball radius
ARENAS = [(690, 735), (390, 1440)]        # ring centres: top one on the right, bottom one on the left
NB = 360                                  # angular bins of the brick wall
TH = np.arange(NB)*2*math.pi/NB
BRICK_H, BRICK_HW = 12.0, 12  # brick height (px) and half width (bins = degrees)
RMIN = 1.25*BR                            # bricks never reach the very centre (keeps a tiny cell for the ball)
TRAP_AREA = 0.06*math.pi*R*R               # walled in when the space the ball can reach is this small
COLORS = [((255, 150, 120), (120, 46, 40)), ((120, 200, 255), (30, 70, 120))]   # (brick, mortar) per ball


# ----------------------------------------------------------------------------------------------- physics
def free_area(rho): return 0.5*float(np.sum(rho*rho))*(2*math.pi/NB)


RADII = np.arange(0.0, R, 3.0)
WINS = [int(min(NB//2, math.ceil(math.degrees(math.asin(min(1.0, BR/max(r_, BR))))*NB/360))) for r_ in RADII]


def settle(rho):
    """Brick up every part of the ring the ball can no longer get into (gaps or arms whose neck is narrower than the ball),
    so what you see always matches the space the ball really has."""
    from scipy.ndimage import minimum_filter1d
    ok_all = np.ones(NB, bool); reach = np.zeros(NB)
    for r_, w in zip(RADII, WINS):
        ok = minimum_filter1d(rho, 2*w + 1, mode="wrap") >= r_ + BR
        ok_all &= ok
        if not ok_all.any(): break
        reach[ok_all] = r_
    return np.maximum(RMIN, np.minimum(rho, reach + BR + 4))


def reach_area(rho, win=8):
    """Free space the ball can actually get into: slits narrower than the ball (about +-8 degrees) don't count."""
    m = rho.copy()
    for k in range(1, win + 1): m = np.minimum(m, np.minimum(np.roll(rho, k), np.roll(rho, -k)))
    return free_area(m)


def simulate_arena(seed, max_t=70.0, speed0=780.0, accel=6.0, sub=8, stop_on_trap=True):
    """Returns dict(frames=[(pos(2,), rho copy every frame)], bricks=[frame indices with a new brick], trap=t or None)."""
    rng = np.random.default_rng(seed)
    p = np.array([rng.uniform(-60, 60), rng.uniform(-60, 60)]); a = rng.uniform(0, 2*math.pi)
    v = np.array([math.cos(a), math.sin(a)])*speed0
    rho = np.full(NB, float(R)); dt = 1/FPS/sub; t = 0.0
    frames, bricks, trap = [], [], None
    prof = BRICK_H*0.5*(1 + np.cos(np.pi*np.arange(-BRICK_HW, BRICK_HW + 1)/BRICK_HW))
    while True:
        hit = False
        for _ in range(sub):
            t += dt; p += v*dt
            bx, by = rho*np.cos(TH), rho*np.sin(TH)
            dx, dy = p[0] - bx, p[1] - by; dist = np.hypot(dx, dy); k = int(np.argmin(dist))
            d = math.hypot(*p); ang = math.atan2(p[1], p[0]) % (2*math.pi); kb = int(round(ang/(2*math.pi)*NB)) % NB
            if d > rho[kb] - BR*0.35:                       # centre ended up inside the bricks: push it back to the middle
                u = p/max(d, 1e-6); p = u*max(0.0, min(d, rho[kb] - BR)); vn = v @ u
                if vn > 0: v = v - 2*vn*u
                continue
            if dist[k] < BR:
                n = np.array([dx[k], dy[k]])/max(dist[k], 1e-6); vn = v @ n
                p = np.array([bx[k], by[k]]) + n*BR
                if vn < 0:
                    v = v - 2*vn*n
                    idx = (k + np.arange(-BRICK_HW, BRICK_HW + 1)) % NB
                    rho[idx] = np.maximum(RMIN, rho[idx] - prof); rho = settle(rho); hit = True
            v = v/np.linalg.norm(v)*(speed0 + accel*t)
        frames.append((p.copy(), rho.copy()))
        if hit: bricks.append(len(frames) - 1)
        if trap is None and free_area(rho) < TRAP_AREA:
            trap = t
            if stop_on_trap: break
        if t > max_t: break
    return dict(frames=frames, bricks=bricks, trap=trap)


def find_race(seed0=1, n=80, lo=32.0, hi=48.0, gap=(1.2, 4.5), tail=5.0):
    """Two seeds: the loser gets walled in between lo and hi seconds, the winner a bit later (but not too much later)."""
    times = {}
    for s in range(seed0, seed0 + n):
        r = simulate_arena(s); times[s] = r["trap"]
    best = None
    for s1, t1 in times.items():
        if t1 is None or not lo <= t1 <= hi: continue
        for s2, t2 in times.items():
            if s2 == s1 or t2 is None: continue
            g = t2 - t1
            if gap[0] <= g <= gap[1] and (best is None or abs(g - 2.2) < abs(best[2] - 2.2)): best = (s1, s2, g)
    if not best: raise RuntimeError("no close race found")
    s1, s2, _ = best
    lose = simulate_arena(s1); win = simulate_arena(s2, max_t=lose["trap"] + tail, stop_on_trap=False)
    return dict(lose=lose, win=win, end=lose["trap"], seeds=(s1, s2))


# ----------------------------------------------------------------------------------------------- drawing
class Wall:
    """Precomputed polar grid for drawing the bricks of one ring."""
    def __init__(self, cx, cy, brick, mortar):
        self.cx, self.cy = cx, cy; s = R + 4; self.box = (cx - s, cy - s)
        yy, xx = np.mgrid[-s:s + 1, -s:s + 1].astype(float); self.d = np.hypot(xx, yy)
        ang = np.arctan2(yy, xx) % (2*math.pi); self.bin = (np.round(ang/(2*math.pi)*NB).astype(int)) % NB
        depth = R - self.d; row = np.floor(depth/22.0)
        col = ang*R/44.0 + 0.5*row
        joint = ((depth % 22.0) < 2.6) | ((col % 1.0) < 2.4/44.0)
        self.inside = self.d < R
        self.rgb = np.empty(self.d.shape + (3,), np.uint8); self.rgb[:] = brick; self.rgb[joint] = mortar
        shade = np.clip(1 - 0.18*(depth/R), 0.75, 1)[..., None]; self.rgb = (self.rgb*shade).astype(np.uint8)

    def image(self, rho):
        r_at = rho[self.bin]; m = self.inside & (self.d > r_at)
        edge = self.inside & (self.d > r_at - 4) & ~m
        a = np.zeros(self.d.shape, np.uint8); a[m] = 255; a[edge] = 200
        rgb = self.rgb.copy(); rgb[edge] = (255, 255, 255)
        return Image.fromarray(np.dstack([rgb, a]), "RGBA")


def background():
    y = np.linspace(0, 1, H)[:, None]; top = np.array([18, 20, 46]); bot = np.array([44, 22, 58])
    img = (top*(1 - y[..., None]) + bot*y[..., None]).repeat(W, 1).astype(np.uint8)
    im = Image.fromarray(img, "RGB").convert("RGBA"); d = ImageDraw.Draw(im); rng = np.random.default_rng(7)
    for _ in range(140):
        x, yy, s = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(1, 3.0)
        d.ellipse((x - s, yy - s, x + s, yy + s), fill=(255, 255, 255, int(rng.uniform(40, 130))))
    for k, (cx, cy) in enumerate(ARENAS):
        glow = Image.new("L", (W, H), 0); ImageDraw.Draw(glow).ellipse((cx - R - 60, cy - R - 60, cx + R + 60, cy + R + 60), fill=130)
        glow = glow.filter(ImageFilter.GaussianBlur(50)); g = Image.new("RGBA", (W, H), COLORS[k][0] + (0,)); g.putalpha(Image.eval(glow, lambda v: v//2))
        im.alpha_composite(g); d = ImageDraw.Draw(im)
        d.ellipse((cx - R, cy - R, cx + R, cy + R), fill=(10, 10, 22, 255))
    return im


def ring(d, cx, cy, col=(255, 255, 255)):
    d.ellipse((cx - R - 9, cy - R - 9, cx + R + 9, cy + R + 9), outline=col + (255,), width=12)


# ----------------------------------------------------------------------------------------------- sound
def make_audio(race, n_frames, path, sr=44100):
    import news5
    N = int(sr*(n_frames/FPS + 0.3)); bed = news5.calm_bed(N, sr, seed=11)*0.2; fx = np.zeros(N)
    def add(sig, t):
        i = int(t*sr); m = min(len(sig), N - i)
        if m > 0 and i >= 0: fx[i:i + m] += sig[:m]
    def clack(f, a, dur=0.16):
        x = np.arange(int(dur*sr))/sr
        return a*(np.sin(2*np.pi*f*x) + 0.4*np.sin(2*np.pi*2.7*f*x))*np.exp(-x/0.035)*(1 - np.exp(-x*900))
    scales = [[523.25, 587.33, 659.25, 783.99, 880.0], [261.63, 293.66, 329.63, 392.0, 440.0]]
    rng = np.random.default_rng(2); end = race["end"]
    for k, key in enumerate(("lose", "win")):
        last = -1
        for fi in race[key]["bricks"]:
            t = fi/FPS
            if t > end + (0 if key == "lose" else 0.6): break
            if t - last > 0.07: add(clack(scales[k][rng.integers(5)], 0.16), t); last = t
    x = np.arange(int(0.9*sr))/sr; thud = 0.7*np.sin(2*np.pi*(90 + 60*np.exp(-x*8))*x)*np.exp(-x/0.18); add(thud, end)
    def pluck(f, a, dur=1.2):
        x = np.arange(int(dur*sr))/sr; return a*(np.sin(2*np.pi*f*x) + 0.3*np.sin(4*np.pi*f*x))*np.exp(-x/0.12)*(1 - np.exp(-x*400))
    for k, f in enumerate([523.25, 659.25, 783.99, 1046.5]): add(pluck(f, 0.3), end + 1.0 + k*0.13)
    g = np.ones(N); fo = int(1.0*sr); g[-fo:] *= np.linspace(1, 0, fo)
    out = (bed + fx[:, None])*g[:, None]; out = out/np.abs(out).max()*0.85
    with wave.open(path, "wb") as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes((out*32767).astype(np.int16).tobytes())


# ----------------------------------------------------------------------------------------------- render
def render(players, headline, race, out_mp4, sheet=None, stills=None):
    """players = [(name, emoji), (name, emoji)]: players[0] is drawn in the top ring, players[1] in the bottom ring.
    race["lose"] is drawn in ring race["loser_slot"] (0 top / 1 bottom)."""
    li = race["loser_slot"]; slots = {li: race["lose"], 1 - li: race["win"]}
    bg = background(); walls = [Wall(cx, cy, *COLORS[k]) for k, (cx, cy) in enumerate(ARENAS)]
    balls = [ball_sprite(e, BR, k*3) for k, (nm, e) in enumerate(players)]
    big = [ball_sprite(e, 62, k*3) for k, (nm, e) in enumerate(players)]
    l1 = fit_font(headline[0], BLACK, 66, W - 80, 6); l2 = fit_font(headline[1], BLACK, 66, W - 80, 6)
    h1 = text_sprite(headline[0], l1, WHITE, 6); h2 = text_sprite(headline[1], l2, GOLD, 6)
    name_f = [fit_font(nm.upper(), BLACK, 46, 270, 4) for nm, e in players]
    stat_f = font(XBOLD, 30); hook_f = font(XBOLD, 40); big_f = font(BLACK, 96); mid_f = font(BLACK, 62)
    hook = text_sprite("Pick your ball before it starts!", hook_f, WHITE, 4)
    end = race["end"]; tail = 4.6; nf = int((end + tail)*FPS); A0 = free_area(np.full(NB, float(R)))
    count = {k: np.cumsum([0] + [1 if i in set(slots[k]["bricks"]) else 0 for i in range(len(slots[k]["frames"]))]) for k in (0, 1)}
    tmp = out_mp4[:-4] + ".tmp.mp4"; wav = out_mp4[:-4] + ".wav"
    ff = None if stills else subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                           "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    st = [int(x*FPS) for x in stills] if stills else []
    sheet_at = {int(FPS*x) for x in (0.5, end*0.33, end*0.66, end - 0.3, end + 1.2)} | {nf - 10}; sheet_frames = []
    crng = np.random.default_rng(9)
    conf = [(crng.uniform(0, W), crng.uniform(-600, 0), crng.uniform(-80, 80), crng.uniform(250, 520),
             tuple(int(c) for c in crng.choice([(255, 196, 46), (255, 84, 84), (90, 200, 255), (130, 255, 150), (255, 140, 230)])),
             crng.uniform(0, 6.3)) for _ in range(150)]
    for fi in range(nf):
        if stills and fi > max(st): break
        t = fi/FPS; im = bg.copy(); d = ImageDraw.Draw(im)
        im.alpha_composite(h1, ((W - h1.size[0])//2, 95)); im.alpha_composite(h2, ((W - h2.size[0])//2, 95 + h1.size[1] + 8))
        for k, (cx, cy) in enumerate(ARENAS):
            run = slots[k]; j = min(fi, len(run["frames"]) - 1)
            if k == li: j = min(j, len(run["frames"]) - 1)
            p, rho = run["frames"][j]
            im.alpha_composite(walls[k].image(rho), walls[k].box)
            d = ImageDraw.Draw(im); trapped = k == li and t >= end
            ring(d, cx, cy, (255, 90, 90) if trapped else (255, 255, 255))
            jit = (np.sin(t*40)*2, np.cos(t*37)*2) if trapped else (0, 0)
            im.alpha_composite(balls[k], (int(cx + p[0] - BR + jit[0]), int(cy + p[1] - BR + jit[1])))
            # stats panel beside the ring
            sx = 40 if cx > W/2 else W - 310; sy = cy - 200; pw = 270
            im.alpha_composite(big[k], (sx + pw//2 - 62, sy))
            nm = text_sprite(players[k][0].upper(), name_f[k], WHITE, 4); im.alpha_composite(nm, (sx + (pw - nm.size[0])//2, sy + 140))
            nb = int(count[k][min(fi + 1, len(count[k]) - 1)])
            bt = text_sprite(f"BRICKS: {nb}", stat_f, COLORS[k][0], 3); im.alpha_composite(bt, (sx + (pw - bt.size[0])//2, sy + 205))
            left = 0.0 if trapped else max(0.0, (free_area(rho) - TRAP_AREA)/(A0 - TRAP_AREA))
            lt = text_sprite(f"SPACE LEFT: {int(round(left*100))}%", stat_f, WHITE, 3); im.alpha_composite(lt, (sx + (pw - lt.size[0])//2, sy + 255))
            d = ImageDraw.Draw(im); by = sy + 305
            d.rounded_rectangle((sx + 10, by, sx + pw - 10, by + 26), 13, fill=(255, 255, 255, 40), outline=(255, 255, 255, 160), width=2)
            if left > 0: d.rounded_rectangle((sx + 12, by + 2, sx + 12 + int((pw - 24)*left), by + 24), 11, fill=(255, 84, 84) if left < 0.25 else COLORS[k][0])
            if trapped:
                u = min(1, (t - end)/0.25); s = text_sprite("WALLED IN!", fit_font("WALLED IN!", BLACK, int(50 + 20*(1 - u)), pw + 20, 6), RED, 6)
                im.alpha_composite(s, (sx + (pw - s.size[0])//2, by + 50))
            if k != li and t >= end + 0.3:
                s = text_sprite("STILL FREE!", fit_font("STILL FREE!", BLACK, 50, pw + 20, 6), GOLD, 6)
                im.alpha_composite(s, (sx + (pw - s.size[0])//2, by + 50))
        if t < 3.0:
            im.alpha_composite(hook, ((W - hook.size[0])//2, 1810))
        else:
            vs = text_sprite("FIRST ONE WALLED IN LOSES", font(XBOLD, 34), (200, 200, 220), 3); im.alpha_composite(vs, ((W - vs.size[0])//2, 1815))
        if t > end + 1.0:
            u = min(1, (t - end - 1.0)/0.6); e3 = 1 - (1 - u)**3
            veil = Image.new("RGBA", (W, H), (8, 8, 20, int(225*e3))); im.alpha_composite(veil)
            wi = 1 - li; s = int(124 + 200*e3); b = big[wi].resize((s, s), Image.LANCZOS); im.alpha_composite(b, ((W - s)//2, 960 - s//2))
            if u >= 1:
                wt = text_sprite("WINNER!", big_f, GOLD, 8); im.alpha_composite(wt, ((W - wt.size[0])//2, 960 - s//2 - wt.size[1] - 30))
                nm = text_sprite(players[wi][0].upper(), fit_font(players[wi][0].upper(), BLACK, 72, W - 100, 6), WHITE, 6)
                im.alpha_composite(nm, ((W - nm.size[0])//2, 960 + s//2 + 30))
                cm = text_sprite("Did you pick it? Comment below!", hook_f, WHITE, 4); im.alpha_composite(cm, ((W - cm.size[0])//2, 960 + s//2 + 140))
            tc = t - end - 1.0; d = ImageDraw.Draw(im)
            for (x0, y0, vx, vy, col, ph) in conf:
                cx_, cy_ = x0 + vx*tc + 20*math.sin(tc*3 + ph), y0 + vy*tc
                if 0 < cy_ < H: d.rectangle((cx_ - 6, cy_ - 3, cx_ + 6, cy_ + 3), fill=col + (255,))
        frame = im.convert("RGB")
        if stills:
            if fi in st: frame.save(out_mp4[:-4] + f"_still_{fi}.jpg", quality=90)
            continue
        ff.stdin.write(frame.tobytes())
        if fi in sheet_at: sheet_frames.append(frame.resize((270, 480)))
    if stills: return None
    ff.stdin.close(); ff.wait()
    if ff.returncode: raise RuntimeError("ffmpeg video failed")
    make_audio(race, nf, wav)
    tmp2 = out_mp4[:-4] + ".tmp2.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", tmp, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
                    "-shortest", "-movflags", "+faststart", tmp2], check=True)
    os.replace(tmp2, out_mp4); os.remove(tmp); os.remove(wav)
    if sheet:
        sh = Image.new("RGB", (270*len(sheet_frames), 480), "grey")
        for k, f in enumerate(sheet_frames): sh.paste(f, (270*k, 0))
        sh.save(sheet)
    return nf/FPS
