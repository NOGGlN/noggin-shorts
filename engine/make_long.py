"""Noggin LONG video (landscape 1920x1080, 30 fps, H.264 veryfast + AAC): a multi-round quiz the viewer plays and scores themselves.

Usage:  python3 make_long.py long/long_YYYY_MM_DD.py YYYY-MM-DD [--stills | --preview [SECONDS]] [--crf N]
  --stills   only a check sheet: /tmp/long_check_<date>.jpg (intro, round card, question, reveal, score check, boss, outro, end screen)
  --preview  a low-res 960x540 preview of the first SECONDS (default 45) with sound: /tmp/long_preview_<date>.mp4
  (none)     the full video: videos/<date>/long-video.mp4 + videos/<date>/long_manifest.json, appends the questions to
             data/used_questions.json (refuses questions already in there).
Episode file (see long/long_2026_11_07.py): TITLE, HOOK (2 lines for the description), TAGS, ROUNDS = [dict(name, topic, level,
timer (s), color, boss?, questions=[dict(q, opts (4), a (index), fact, emojis)])].
Owner's rule: the viewer just plays. Noggin is only a friendly host/decoration: never competes, guesses, answers or keeps a score.
Sound: no music; a quiet synthesized ambient bed + ticks, whooshes and reveal dings (genres/gcommon.py Mix).
Rendering runs on all CPU cores in chunks, then ffmpeg concatenates the chunks and muxes the audio (sync is frame-exact).
"""
import importlib.util, json, math, os, subprocess, sys, multiprocessing as mp
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "genres"))
import gcommon as g
from mascot import mascot

W, H, FPS = 1920, 1080, 30
RAW = "https://raw.githubusercontent.com/NOGGlN/noggin-shorts/main/videos/{date}/{file}"
XB = g.XB; INK = g.INK; WHITE = g.WHITE; YEL = g.YEL; GRN = g.GRN; RED = g.RED
QIN, REV, REV_BOSS = 1.0, 3.4, 4.0              # question entrance, reveal hold (seconds)
INTRO, CARD, CHECK, OUTRO, END = 6.0, 3.5, 3.5, 8.0, 10.0
BG_TOP, BG_BOT = (22, 14, 44), (46, 22, 70)
LET = "ABCD"

# ------------------------------------------------------------------ helpers
def rr(d, box, r, **kw): d.rounded_rectangle([int(v) for v in box], r, **kw)

def wrap(txt, path, size, maxw):
    f = g.font(path, size); words = txt.split(); lines = [""]
    for w in words:
        t = (lines[-1] + " " + w).strip()
        if f.getlength(t) <= maxw: lines[-1] = t
        else: lines.append(w)
    return lines

def textblock(txt, size, fill, maxw, max_lines=2, path=XB, spacing=1.18, stroke=0, sc=INK):
    while True:
        lines = wrap(txt, path, size, maxw)
        if len(lines) <= max_lines or size <= 30: break
        size -= 4
    f = g.font(path, size); lh = int(size*spacing)
    im = Image.new("RGBA", (int(maxw) + 2*stroke + 8, lh*len(lines) + 2*stroke + 16), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for i, ln in enumerate(lines):
        x = (im.width - f.getlength(ln))/2
        d.text((x, stroke + 4 + i*lh), ln, font=f, fill=fill, stroke_width=stroke, stroke_fill=sc)
    return im.crop(im.getbbox() or (0, 0, 1, 1))

def check_mark(size, col=WHITE):
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0)); d = ImageDraw.Draw(im); s = size
    d.line([(s*0.18, s*0.55), (s*0.42, s*0.78), (s*0.84, s*0.24)], fill=col, width=max(4, int(s*0.16)), joint="curve"); return im

_bg = {}
def background(col):
    if col not in _bg:
        im = g.gradient(BG_TOP, BG_BOT); im.alpha_composite(g.stripes(7).crop((0, 0, W, H)))
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(glow)
        d.rectangle((0, 0, W, 8), fill=col + (255,)); im.alpha_composite(glow); _bg[col] = im
    return _bg[col]

def put_noggin(im, t, pose, x, y, s):
    m = mascot(pose, (0, -1), (t % 3.1) < 0.12); g.paste(im, m, x, y + 8*math.sin(t*4.0), s*(1 + 0.025*math.sin(t*6)))

def fade(im, a):
    if a > 0: im.alpha_composite(Image.new("RGBA", (W, H), (10, 6, 22, int(255*min(1, a)))))

# ------------------------------------------------------------------ episode -> timeline
def load(path):
    spec = importlib.util.spec_from_file_location("ep", path); ep = importlib.util.module_from_spec(spec); spec.loader.exec_module(ep); return ep

def timeline(ep):
    segs = []; t = 0.0; total = sum(len(r["questions"]) for r in ep.ROUNDS); n = 0; done = 0
    segs.append(dict(kind="intro", t0=t, dur=INTRO, total=total)); t += INTRO
    for ri, R in enumerate(ep.ROUNDS):
        segs.append(dict(kind="card", t0=t, dur=CARD, R=R, ri=ri, chapter=True)); t += CARD
        for qi, Q in enumerate(R["questions"]):
            n += 1; dur = QIN + R["timer"] + (REV_BOSS if R.get("boss") else REV)
            segs.append(dict(kind="q", t0=t, dur=dur, R=R, Q=Q, n=n, qi=qi, total=total)); t += dur
        done += len(R["questions"])
        segs.append(dict(kind="check", t0=t, dur=CHECK, R=R, ri=ri, done=done, total=total)); t += CHECK
    segs.append(dict(kind="outro", t0=t, dur=OUTRO, total=total, chapter=True)); t += OUTRO
    segs.append(dict(kind="end", t0=t, dur=END)); t += END
    return segs, t

def tc(s):
    small = {"and", "the", "of", "to"}
    return " ".join(w.lower() if i and w.lower() in small else w.capitalize() for i, w in enumerate(s.replace("&", "and").split()))

def chapters(segs):
    out = [("0:00", "Intro: grab a pen")]
    for s in segs:
        if not s.get("chapter"): continue
        m, sec = divmod(int(s["t0"]), 60)
        if s["kind"] == "card":
            R = s["R"]; lab = f"Final boss: {tc(R['topic']).lower()} questions" if R.get("boss") else f"{tc(R['name'])}: {tc(R['topic'])} ({tc(R['level'])})"
        else: lab = "Your score + rating"
        out.append((f"{m}:{sec:02d}", lab.replace("&", "and")))
    return out

# ------------------------------------------------------------------ drawing
class Painter:
    def __init__(self, ep):
        self.ep = ep; self.segs, self.dur = timeline(ep); self.cache = {}

    def seg(self, t):
        for s in self.segs:
            if s["t0"] <= t < s["t0"] + s["dur"]: return s
        return self.segs[-1]

    # ---- question parts (cached)
    def q_parts(self, s):
        k = id(s["Q"])
        if k in self.cache: return self.cache[k]
        R, Q = s["R"], s["Q"]; col = R["color"]
        base = background(col).copy(); d = ImageDraw.Draw(base)
        lab = f"{R['name']}  -  {R['topic']}"; f = g.font(XB, 38); w = f.getlength(lab) + 60
        rr(d, (110, 34, 110 + w, 96), 31, fill=col + (255,)); d.text((140, 41), lab, font=f, fill=INK)
        qtxt = f"QUESTION {s['n']} / {s['total']}"; d.text((1590 - f.getlength(qtxt), 41), qtxt, font=f, fill=WHITE)
        f2 = g.font(XB, 36); kt = "KEEP SCORE: +1 FOR EVERY RIGHT ANSWER"; d.text((110, 962), kt, font=f2, fill=(200, 190, 230))
        rr(d, (110, 1026, 1590, 1040), 7, fill=(255, 255, 255, 40))
        rr(d, (110, 1026, 110 + 1480*s["n"]/s["total"], 1040), 7, fill=col + (255,))
        # emoji row
        em = Image.new("RGBA", (900, 150), (0, 0, 0, 0)); es = Q.get("emojis", [])[:3]
        for i, e in enumerate(es):
            pic = g.emoji(e, 128); x = 450 + (i - (len(es) - 1)/2)*150; em.alpha_composite(pic, (int(x - pic.width/2), int(75 - pic.height/2)))
        # question card
        card = Image.new("RGBA", (1480, 210), (0, 0, 0, 0)); cd = ImageDraw.Draw(card)
        rr(cd, (0, 8, 1480, 210), 34, fill=(0, 0, 0, 90)); rr(cd, (0, 0, 1480, 200), 34, fill=(255, 255, 255, 255))
        qt = textblock(Q["q"], 66, INK, 1380, 2); card.alpha_composite(qt, ((1480 - qt.width)//2, (200 - qt.height)//2))
        # options in 3 states
        opts = {}
        for i, o in enumerate(Q["opts"]):
            for st in ("n", "ok", "no"):
                b = Image.new("RGBA", (720, 124), (0, 0, 0, 0)); bd = ImageDraw.Draw(b)
                fill = (40, 30, 76) if st != "ok" else (52, 168, 83); outl = col if st == "n" else (GRN if st == "ok" else (90, 80, 120))
                rr(bd, (0, 0, 719, 123), 26, fill=fill + (255,), outline=outl + (255,), width=5)
                bd.ellipse((18, 22, 98, 102), fill=(outl if st != "ok" else WHITE) + (255,))
                lf = g.font(XB, 48); L = LET[i]; bd.text((58 - lf.getlength(L)/2, 33), L, font=lf, fill=INK if st != "ok" else (52, 168, 83))
                ot = textblock(o, 50, WHITE if st != "no" else (150, 140, 175), 560, 2, spacing=1.08)
                b.alpha_composite(ot, (int(120 + (580 - ot.width)/2), int((124 - ot.height)/2)))
                if st == "ok": b.alpha_composite(check_mark(70), (640, 27))
                opts[(i, st)] = b
        fact = Image.new("RGBA", (1480, 110), (0, 0, 0, 0)); fd = ImageDraw.Draw(fact)
        rr(fd, (0, 0, 1479, 109), 26, fill=YEL + (255,))
        ft = textblock(Q["fact"], 44, INK, 1400, 1); fact.alpha_composite(ft, ((1480 - ft.width)//2, (110 - ft.height)//2))
        self.cache[k] = (base, em, card, opts, fact); return self.cache[k]

    def timer(self, im, cx, cy, left, total, col, revealed, lt):
        d = ImageDraw.Draw(im); r = 118
        if not revealed:
            d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(18, 12, 36), outline=(255, 255, 255, 60), width=6)
            ac = RED if left <= 2 else col
            if left > 0: d.arc((cx - r, cy - r, cx + r, cy + r), -90, -90 + 360*left/total, fill=ac, width=16)
            g.paste(im, g.T(str(max(1, math.ceil(left))), 110, WHITE, 0), cx, cy, 1 + (0.08*(1 - (left % 1)) if left <= 3 else 0))
            g.paste(im, g.T("SECONDS", 26, (190, 180, 220), 0), cx, cy + 165)
        else:
            k = g.back(lt/0.3); d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(52, 168, 83), outline=WHITE, width=6)
            g.paste(im, g.T("+1", 100, WHITE, 0), cx, cy, k)
            g.paste(im, g.T("GOT IT?", 40, GRN, 6), cx, cy + 170, k)

    def frame(self, t):
        s = self.seg(t); lt = t - s["t0"]; kind = s["kind"]
        if kind == "q": return self.f_question(s, lt, t)
        im = background((255, 200, 90) if kind in ("intro", "outro", "end") else s["R"]["color"]).copy()
        getattr(self, "f_" + kind)(im, s, lt, t)
        fade(im, 1 - g.ease(lt/0.3) if kind != "intro" else 1 - g.ease(lt/0.25))
        if kind == "end" and lt > s["dur"] - 0.6: fade(im, (lt - (s["dur"] - 0.6))/0.6)
        return im

    def f_question(self, s, lt, t):
        R, Q = s["R"], s["Q"]; col = R["color"]; base, em, card, opts, fact = self.q_parts(s)
        im = base.copy(); T = R["timer"]; rv = QIN + T; revealed = lt >= rv; rt = lt - rv
        k = g.back(lt/0.4); g.paste(im, em, 850, 192, max(0.01, k))
        g.paste(im, card, 850, 375, 0.9 + 0.1*k, alpha=g.ease(lt/0.3))
        for i in range(4):
            x = 110 + (i % 2)*760 + 360; y = 515 + (i//2)*150 + 62; ki = g.ease((lt - 0.25 - 0.1*i)/0.35)
            if ki <= 0: continue
            st = "n" if not revealed else ("ok" if i == Q["a"] else "no")
            sc = 1.0 + (0.05*math.sin(min(1, rt/0.35)*math.pi) if st == "ok" else 0)
            g.paste(im, opts[(i, st)], x + (1 - ki)*(-120 if i % 2 == 0 else 120), y, sc, alpha=ki)
        self.timer(im, 1750, 360, max(0, T - max(0, lt - QIN)), T, col, revealed, rt)
        if revealed: g.paste(im, fact, 850, 875 + 30*(1 - g.ease(rt/0.35)), alpha=g.ease((rt - 0.15)/0.35))
        put_noggin(im, t, "laugh" if revealed else "idle", 1770, 905, 0.5)
        if lt > s["dur"] - 0.25: fade(im, (lt - (s["dur"] - 0.25))/0.25*0.6)
        if lt < 0.2: fade(im, 0.6*(1 - lt/0.2))
        return im

    def f_intro(self, im, s, lt, t):
        g.paste(im, g.T(f"{s['total']} QUESTIONS", 190, WHITE, 16), W/2, 250, g.back(lt/0.35))
        g.paste(im, g.T("EASY TO IMPOSSIBLE", 110, YEL, 12), W/2, 430, g.back((lt - 0.5)/0.35), rot=-3)
        g.paste(im, g.T("GRAB A PEN AND KEEP SCORE", 80, WHITE, 10), W/2, 640, g.back((lt - 1.4)/0.35))
        g.paste(im, g.T("+1 POINT FOR EVERY RIGHT ANSWER", 56, GRN, 8), W/2, 760, g.back((lt - 2.2)/0.35))
        g.paste(im, g.T("5 ROUNDS  -  A TIMER ON EVERY QUESTION  -  FINAL BOSS AT THE END", 42, (210, 200, 240), 6, maxw=1400), W/2 - 120, 870, g.back((lt - 3.0)/0.35))
        put_noggin(im, t, "wave", 1770, 930, 0.65)

    def f_card(self, im, s, lt, t):
        R = s["R"]; col = R["color"]; boss = R.get("boss")
        g.paste(im, g.T(R["name"], 230 if boss else 200, col if boss else WHITE, 18), W/2 + (math.sin(t*70)*8*max(0, 1 - lt) if boss else 0), 330, g.back(lt/0.35))
        g.paste(im, g.T(R["topic"], 110, YEL if not boss else WHITE, 12), W/2, 540, g.back((lt - 0.4)/0.35), rot=-2)
        n = len(R["questions"]); info = f"{n} {'IMPOSSIBLE ' if boss else ''}QUESTIONS  -  {R['timer']} SECONDS EACH  -  {R['level']}"
        g.paste(im, g.T(info, 46, (215, 205, 245), 7), W/2, 700, g.back((lt - 0.9)/0.35))
        if boss: g.paste(im, g.T("NO SHAME IN GETTING ZERO HERE", 50, GRN, 7), W/2, 800, g.back((lt - 1.4)/0.35))
        put_noggin(im, t, "shock" if boss else "wave", 1700, 900, 0.7)

    def f_check(self, im, s, lt, t):
        R = s["R"]; n = len(R["questions"])
        g.paste(im, g.T(f"{R['name']} DONE" if not R.get("boss") else "YOU BEAT THE FINAL BOSS", 130, WHITE, 14), W/2, 290, g.back(lt/0.35))
        g.paste(im, g.T(f"HOW MANY DID YOU GET OUT OF {n}?", 84, YEL, 10), W/2, 480, g.back((lt - 0.4)/0.35))
        if s["done"] > n: g.paste(im, g.T(f"YOUR RUNNING TOTAL IS OUT OF {s['done']}", 60, GRN, 8), W/2, 630, g.back((lt - 0.9)/0.35))
        g.paste(im, g.T("WRITE IT DOWN", 52, (215, 205, 245), 7), W/2, 760, g.back((lt - 1.3)/0.35))
        put_noggin(im, t, "laugh", 1700, 900, 0.7)

    def f_outro(self, im, s, lt, t):
        g.paste(im, g.T(f"WHAT'S YOUR SCORE OUT OF {s['total']}?", 110, WHITE, 12), W/2, 170, g.back(lt/0.35))
        rows = [("0 - 15", "WARMING UP", (150, 200, 255)), ("16 - 30", "SHARP", GRN), ("31 - 40", "BIG BRAIN", YEL), ("41 - 45", "GENIUS", (255, 120, 170))]
        for i, (a, b, c) in enumerate(rows):
            k = g.back((lt - 0.6 - 0.35*i)/0.3); y = 360 + i*120
            g.paste(im, g.T(a, 70, WHITE, 9), 760, y, k, anchor="r"); g.paste(im, g.T(b, 70, c, 9), 840, y, k, anchor="l")
        g.paste(im, g.T("COMMENT YOUR SCORE BELOW", 92, YEL, 11), W/2, 900, g.back((lt - 2.4)/0.35), rot=-2)
        put_noggin(im, t, "laugh", 1710, 760, 0.7)

    def f_end(self, im, s, lt, t):
        g.paste(im, g.T("THANKS FOR PLAYING!", 140, WHITE, 14), W/2, 260, g.back(lt/0.35))
        g.paste(im, g.T("SUBSCRIBE FOR A NEW QUIZ EVERY SATURDAY", 76, YEL, 10), W/2, 430, g.back((lt - 0.5)/0.35))
        put_noggin(im, t, "wave", W/2, 760, 1.0)

    # ---- sound
    def audio(self, path):
        M = g.Mix(self.dur, bed=0, seed=7); N = M.N; x = np.arange(N)/g.SR
        noise = M.rr.normal(0, 1, N); c = np.cumsum(noise); lp = (c[1200:] - c[:-1200])/1200; noise = np.concatenate([lp, np.zeros(1200)])
        pad = sum(a*np.sin(2*np.pi*f*x + p) for f, a, p in ((55, 0.5, 0), (82.41, 0.35, 1), (110, 0.25, 2), (164.81, 0.12, 3)))
        M.out += (noise*1.6 + pad*0.5*(0.7 + 0.3*np.sin(2*np.pi*0.05*x)))*0.05
        for s in self.segs:
            t0 = s["t0"]; k = s["kind"]
            if k == "intro":
                M.add(M.thud(80), 0.05, 0.7); M.add(M.ding(1046.5), 0.55, 0.6); M.add(M.pop(600), 1.45, 0.6); M.add(M.pop(700), 2.25, 0.5)
            elif k == "card":
                M.add(M.riser(0.9), t0, 0.7); M.add(M.boom() if s["R"].get("boss") else M.thud(70), t0 + 0.05, 0.6); M.add(M.ding(880), t0 + 0.45, 0.5)
            elif k == "q":
                T = s["R"]["timer"]; M.add(M.whoosh(0.35), t0, 0.35)
                for i in range(4): M.add(M.pop(520 + 60*i), t0 + 0.3 + 0.1*i, 0.22)
                for j in range(T): M.add(M.tick(2000 if T - j <= 3 else 1500), t0 + QIN + j, 0.5)
                rv = t0 + QIN + T; M.add(M.ding(1318.5, 1.2), rv, 0.7); M.add(M.ding(1975.5, 0.8), rv + 0.08, 0.35)
            elif k == "check": M.fanfare(t0 + 0.1)
            elif k == "outro":
                M.fanfare(t0 + 0.1)
                for i in range(4): M.add(M.pop(500 + 80*i), t0 + 0.6 + 0.35*i, 0.4)
            elif k == "end": M.add(M.ding(1046.5, 1.5), t0 + 0.1, 0.5); M.add(M.ding(1568, 1.5), t0 + 0.5, 0.4)
        M.save(path)

# ------------------------------------------------------------------ render
P = None
def _chunk(args):
    i0, i1, path, scale = args
    vf = ["-vf", f"scale={scale}"] if scale else []
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          *vf, "-c:v", "libx264", "-preset", "veryfast", "-crf", str(CRF), "-pix_fmt", "yuv420p", "-g", "60", "-threads", "2", path],
                         stdin=subprocess.PIPE)
    for i in range(i0, i1): p.stdin.write(P.frame(i/FPS).convert("RGB").tobytes())
    p.stdin.close(); p.wait(); return p.returncode

def render(nframes, wav, out, tmpdir, scale=None, workers=None):
    workers = workers or os.cpu_count() or 2; nch = workers*3; step = math.ceil(nframes/nch)
    jobs = [(a, min(nframes, a + step), os.path.join(tmpdir, f"chunk_{j:03d}.mp4"), scale) for j, a in enumerate(range(0, nframes, step))]
    with mp.get_context("fork").Pool(workers) as pool: rc = pool.map(_chunk, jobs)
    if any(rc): raise SystemExit(f"chunk render failed: {rc}")
    lst = os.path.join(tmpdir, "list.txt"); open(lst, "w").write("".join(f"file '{j[2]}'\n" for j in jobs))
    r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-i", wav, "-map", "0:v", "-map", "1:a",
                        "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-t", f"{nframes/FPS:.3f}", "-movflags", "+faststart", out])
    if r.returncode: raise SystemExit("ffmpeg concat/mux failed")
    for j in jobs: os.remove(j[2])

CRF = 23
if __name__ == "__main__":
    path, date = sys.argv[1], sys.argv[2]; a = sys.argv[3:]
    if "--crf" in a: CRF = int(a[a.index("--crf") + 1])
    ep = load(path); P = Painter(ep); total = sum(len(r["questions"]) for r in ep.ROUNDS)
    for R in ep.ROUNDS:
        for Q in R["questions"]:
            assert len(Q["opts"]) == 4 and len(set(Q["opts"])) == 4 and 0 <= Q["a"] < 4 and Q["fact"] and Q["q"], f"bad question {Q}"
    print(f"{total} questions, {P.dur:.1f} s = {int(P.dur//60)}:{int(P.dur % 60):02d}")
    for c in chapters(P.segs): print(" ", *c)
    tmp = f"/tmp/long_{date}"; os.makedirs(tmp, exist_ok=True)
    if "--stills" in a:
        want = ["intro", "card", "q", "qr", "check", "boss", "outro", "end"]; times = []
        for s in P.segs:
            if s["kind"] == "intro" and "intro" in want: times.append(s["t0"] + 4.0); want.remove("intro")
            elif s["kind"] == "card" and s["R"].get("boss") and "boss" in want: times.append(s["t0"] + 2.5); want.remove("boss")
            elif s["kind"] == "card" and "card" in want: times.append(s["t0"] + 2.5); want.remove("card")
            elif s["kind"] == "q" and s["n"] in (2, 14) and "q" in want: times.append(s["t0"] + QIN + 2.2); want.remove("q")
            elif s["kind"] == "q" and s["n"] == 37 and "qr" in want: times.append(s["t0"] + s["dur"] - 1.0); want.remove("qr")
            elif s["kind"] == "check" and s["ri"] == 1 and "check" in want: times.append(s["t0"] + 2.5); want.remove("check")
            elif s["kind"] in ("outro", "end") and s["kind"] in want: times.append(s["t0"] + s["dur"] - 2.0); want.remove(s["kind"])
        extra = [s["t0"] + s["dur"] - 1.0 for s in P.segs if s["kind"] == "q" and s["R"].get("boss")][:2]
        ims = [P.frame(t).convert("RGB").resize((960, 540)) for t in times + extra]; cols = 2
        sheet = Image.new("RGB", (960*cols, 540*((len(ims) + cols - 1)//cols)))
        for i, im in enumerate(ims): sheet.paste(im, ((i % cols)*960, (i//cols)*540))
        sp = f"/tmp/long_check_{date}.jpg"; sheet.save(sp, quality=85); print("check sheet:", sp); sys.exit()
    wav = os.path.join(tmp, "audio.wav"); P.audio(wav)
    if "--preview" in a:
        i = a.index("--preview"); secs = float(a[i + 1]) if i + 1 < len(a) and not a[i + 1].startswith("-") else 45.0
        out = f"/tmp/long_preview_{date}.mp4"; CRF = 28; render(int(secs*FPS), wav, out, tmp, scale="960:540"); print("preview:", out); sys.exit()
    # ---- full render
    used_p = os.path.join(HERE, "data", "used_questions.json"); used = json.load(open(used_p))
    seen = {" ".join(u["question"].lower().split()) for u in used}
    entries = []
    for ri, R in enumerate(ep.ROUNDS):
        for qi, Q in enumerate(R["questions"]):
            qs = f"long r{ri + 1}: {Q['q']} -> {Q['opts'][Q['a']]}"
            if " ".join(qs.lower().split()) in seen: raise SystemExit(f"DUPLICATE question: {Q['q']}")
            entries.append(dict(date=date, gen=f"long{date[5:7]}{date[8:10]}_r{ri + 1}q{qi + 1}", question=qs, answer=Q["opts"][Q["a"]]))
    outdir = os.path.join(HERE, "..", "videos", date); os.makedirs(outdir, exist_ok=True)
    fname = "long-video.mp4"; mp4 = os.path.join(outdir, fname)
    render(int(P.dur*FPS), wav, mp4, tmp)
    chs = chapters(P.segs)
    desc = "\n".join(ep.HOOK) + "\n\n" + "\n".join(f"{a} {b}" for a, b in chs) + "\n\nComment your score 👇\n\n#trivia #quiz #noggin"
    man = [dict(file=fname, url=RAW.format(date=date, file=fname), kind="long", format="video", title=ep.TITLE, description=desc,
                tags=ep.TAGS, seconds=round(P.dur, 1), questions=total, chapters=chs)]
    json.dump(man, open(os.path.join(outdir, "long_manifest.json"), "w"), ensure_ascii=False, indent=1)
    used += entries; json.dump(used, open(used_p, "w"), ensure_ascii=False, indent=1)
    print("done", mp4, round(P.dur, 1), "s", os.path.getsize(mp4)//1_000_000, "MB")
