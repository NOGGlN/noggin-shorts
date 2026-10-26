"""New puzzle generators for Noggin v4. Each returns a dict:
q, a (card images 960x800), options (4), correct, question, banner, catch, and optionally
pre (seconds of animation before the timer), anim(u)->card, pre_label."""
import math, random
from collections import deque
from PIL import Image, ImageDraw, ImageFont
from render import font, DARK
from v3 import CARD, blank, emoji, GREEN

CW, CH = CARD
RED = (231, 76, 60); BLUE = (52, 152, 219); ORANGE = (243, 156, 18); PURPLE = (155, 89, 182)
GREY = (150, 150, 170); SOFT = (244, 245, 250)
BADGE = [(231, 76, 60), (52, 152, 219), (243, 156, 18), (39, 174, 96)]

def shuffle_opts(r, ans, wrong):
    wrong = [w for w in dict.fromkeys(wrong) if w != ans][:3]
    o = wrong + [ans]; r.shuffle(o); return o, o.index(ans)

def num_wrong(r, ans, spread=(1, 2, 3, 4, 5), extra=()):
    pool = set(extra)
    for s in spread: pool.update({ans + s, ans - s})
    pool = [p for p in pool if p != ans and p >= 0]; r.shuffle(pool)
    # keep given 'extra' (trap) answers first
    ex = [e for e in extra if e != ans and e >= 0]
    return ex + [p for p in pool if p not in ex]

def explain(card, txt, y=CH - 46, col=(110, 110, 130), size=36):
    y = min(y, CH - 100)  # keep clear of the answer banner
    d = ImageDraw.Draw(card); f = font(size)
    while d.textlength(txt, font=f) > CW - 60 and size > 22: size -= 2; f = font(size)
    d.text((CW/2, y), txt, font=f, fill=col, anchor="mm")

_em = {}
def em(e, size):
    k = (e, size)
    if k not in _em: _em[k] = emoji(e, size)
    return _em[k]

def paste_c(dst, src, x, y):
    dst.alpha_composite(src, (int(x - src.width/2), int(y - src.height/2)))

# =====================================================================
# 1. EMOJI MATH
FRUIT = [["🍎", "🍌", "🍇"], ["🍓", "🍍", "🥝"], ["🍩", "🍪", "🧁"], ["🐶", "🐱", "🐭"], ["⭐", "🌙", "☀️"], ["🍕", "🍔", "🌭"]]
def row_img(parts, h=110):
    """parts: list of ('e', emoji) / ('t', text, color)"""
    ims = []
    for p in parts:
        if p[0] == "e": ims.append(em(p[1], int(h*0.92)))
        else:
            f = font(int(h*0.72)); d = ImageDraw.Draw(Image.new("L", (1, 1))); b = d.textbbox((0, 0), p[1], font=f)
            im = Image.new("RGBA", (b[2] - b[0] + 10, h), (0, 0, 0, 0))
            ImageDraw.Draw(im).text(((b[2] - b[0] + 10)/2, h/2), p[1], font=f, fill=p[2] if len(p) > 2 else DARK, anchor="mm")
            ims.append(im)
    gap = 14; w = sum(i.width for i in ims) + gap*(len(ims) - 1)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0)); x = 0
    for i in ims: out.alpha_composite(i, (x, int((h - i.height)/2))); x += i.width + gap
    return out

def emoji_math(seed, level):
    r = random.Random(seed); A, B, C = r.choice(FRUIT)
    if level == 0:
        a = r.randint(2, 6); b = r.randint(2, 9)
        rows = [([("e", A), ("t", "+"), ("e", A), ("t", "="), ("t", str(2*a))], None),
                ([("e", A), ("t", "+"), ("e", B), ("t", "="), ("t", str(a + b))], None),
                ([("e", B), ("t", "+"), ("e", B), ("t", "="), ("t", "?", RED)], None)]
        ans = 2*b; wrong = num_wrong(r, ans, extra=[a + b, b])
        exp = f"{A}={a} so {B}={b}  →  {b}+{b} = {ans}"
        vals = {A: a, B: b}
    else:
        a = r.randint(3, 9); b = r.randint(3, 8); c = r.randint(1, b - 1)
        rows = [([("e", A), ("t", "+"), ("e", A), ("t", "+"), ("e", A), ("t", "="), ("t", str(3*a))], None),
                ([("e", A), ("t", "+"), ("e", B), ("t", "+"), ("e", B), ("t", "="), ("t", str(a + 2*b))], None),
                ([("e", B), ("t", "−"), ("e", C), ("t", "="), ("t", str(b - c))], None)]
        if level == 1:
            last = [("e", C), ("t", "+"), ("e", B), ("t", "+"), ("e", A), ("t", "="), ("t", "?", RED)]; ans = a + b + c
            wrong = num_wrong(r, ans, extra=[a + b, ans + c])
        else:  # order of operations trap
            last = [("e", C), ("t", "+"), ("e", A), ("t", "×"), ("e", B), ("t", "="), ("t", "?", RED)]; ans = c + a*b
            wrong = num_wrong(r, ans, extra=[(c + a)*b, a*b])
        rows.append((last, None)); vals = {A: a, B: b, C: c}
    def card(show_vals):
        im = blank(); h = 112 if len(rows) == 4 else 130; gap = 22 if show_vals else 36
        tot = len(rows)*h + (len(rows) - 1)*gap; y = (CH - tot)/2 - (95 if show_vals else 0)
        for k, (parts, _) in enumerate(rows):
            if show_vals and k == len(rows) - 1: parts = parts[:-1] + [("t", str(ans), GREEN)]
            ri = row_img(parts, h); im.alpha_composite(ri, (int(CW/2 - ri.width/2), int(y))); y += h + gap
        if show_vals:
            parts = []
            for e_, v in vals.items(): parts += [("e", e_), ("t", f"={v}", (110, 110, 130)), ("t", "  ")]
            ri = row_img(parts[:-1], 70); im.alpha_composite(ri, (int(CW/2 - ri.width/2), CH - 165))
        return im
    opts, k = shuffle_opts(r, ans, wrong)
    q = card(False); a_ = card(True)
    if level >= 2: explain(a_, "multiply FIRST, then add!", y=CH - 196, col=RED, size=34)
    return dict(q=q, a=a_, options=[str(o) for o in opts], correct=k, question="SOLVE THE EMOJI MATH!",
                banner=f"THE ANSWER IS {ans}!", catch=level >= 2)

# =====================================================================
# 2. NUMBER SEQUENCE
def sequence(seed, level):
    r = random.Random(seed)
    if level == 0:
        s = r.randint(1, 9); d = r.choice([2, 3, 5, 10]); seq = [s + d*i for i in range(6)]; rule = f"+{d} each time"
        wrong = [seq[-1] + 1, seq[-1] - d, seq[-1] + 2*d]
    elif level == 1:
        kind = r.choice(["double", "minus"])
        if kind == "double":
            s = r.choice([1, 2, 3, 5]); seq = [s*2**i for i in range(6)]; rule = "×2 each time"
            wrong = [seq[-2] + seq[-3], seq[-1] + 2, seq[-1]*3//2]
        else:
            d = r.choice([3, 4, 6, 7]); s = d*6 + r.randint(1, 9); seq = [s - d*i for i in range(6)]; rule = f"−{d} each time"
            wrong = [seq[-1] - 1, seq[-1] + d, seq[-1] - 2*d]
    elif level == 2:
        kind = r.choice(["growing", "fib"])
        if kind == "growing":
            s = r.randint(1, 9); seq = [s]
            for i in range(1, 6): seq.append(seq[-1] + i)
            rule = "+1, +2, +3, +4, +5"; wrong = [seq[-2] + 4, seq[-1] + 1, seq[-1] + 5]
        else:
            a, b = r.choice([(1, 1), (1, 2), (2, 3), (1, 3)]); seq = [a, b]
            while len(seq) < 6: seq.append(seq[-1] + seq[-2])
            rule = "add the last two numbers"; wrong = [seq[-2]*2, seq[-1] - 1, seq[-1] + 3]
    else:
        kind = r.choice(["squares", "x2plus1", "alt"])
        if kind == "squares":
            o = r.randint(1, 3); seq = [(i + o)**2 for i in range(6)]; rule = "square numbers: n×n"
            wrong = [seq[-2] + 2*(o + 4) + 2, seq[-1] + 2, seq[-1] - 1]
        elif kind == "x2plus1":
            s = r.choice([1, 2, 3]); seq = [s]
            while len(seq) < 6: seq.append(seq[-1]*2 + 1)
            rule = "×2 then +1"; wrong = [seq[-1] - 1, seq[-2]*2, seq[-1] + 2]
        else:
            s = r.randint(2, 6); seq = [s]
            for i in range(5): seq.append(seq[-1] + 3 if i % 2 == 0 else seq[-1]*2)
            rule = "+3, ×2, +3, ×2..."; wrong = [seq[-2]*2, seq[-2] + 6, seq[-1] + 3]
    ans = seq[-1]; shown = seq[:-1]
    def card(rev):
        im = blank(); d = ImageDraw.Draw(im); n = len(seq)
        rr = 68; gap = (CW - 80 - 2*rr*n)/(n - 1); y = CH/2 - 30
        cols = [(255, 236, 179), (200, 230, 255), (220, 245, 210), (255, 214, 226), (232, 220, 255)]
        for i, v in enumerate(seq):
            x = 40 + rr + i*(2*rr + gap)
            last = i == n - 1
            fill = (GREEN if rev else (255, 255, 255)) if last else cols[i % len(cols)]
            d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=fill, outline=DARK, width=6)
            t = (str(v) if (rev or not last) else "?")
            sz = 62 if len(t) <= 2 else (48 if len(t) == 3 else 38)
            d.text((x, y + 3), t, font=font(sz), fill=("white" if (last and rev) else (RED if last else DARK)), anchor="mm")
            if i < n - 1 and rev:
                diff = seq[i + 1] - v
                lbl = f"+{diff}" if diff >= 0 else f"−{-diff}"
                if "×2" in rule and rule.startswith("×2 each"): lbl = "×2"
                d.text((x + rr + gap/2, y - rr - 30), lbl, font=font(30), fill=PURPLE, anchor="mm")
        if rev: explain(im, f"Rule: {rule}", y=CH - 150, col=PURPLE, size=44)
        return im
    opts, k = shuffle_opts(r, ans, [w for w in wrong if w > 0] + num_wrong(r, ans))
    return dict(q=card(False), a=card(True), options=[str(o) for o in opts], correct=k, question="WHAT NUMBER COMES NEXT?",
                banner=f"IT'S {ans}!", catch=False)

# =====================================================================
# 3. ORDER OF OPERATIONS (catch)
def order_ops(seed, level):
    r = random.Random(seed)
    while True:
        if level <= 1:
            a, b, c = r.randint(2, 9), r.randint(2, 9), r.randint(2, 6)
            expr = f"{a} + {b} × {c}"; ans = a + b*c; naive = (a + b)*c
            exp = f"{b} × {c} = {b*c} first, then + {a}"
        elif level == 2:
            a, b, c, d_ = r.randint(10, 20), r.randint(2, 6), r.randint(2, 5), r.randint(1, 9)
            expr = f"{a} − {b} × {c} + {d_}"; ans = a - b*c + d_; naive = (a - b)*c + d_
            exp = f"{b} × {c} = {b*c} first, then {a} − {b*c} + {d_}"
        elif r.random() < 0.5:
            c, d_ = r.randint(1, 4), r.randint(1, 4); b = r.choice([2, 3, 4, 5, 6]); a = b*r.randint(2, 6)*(c + d_)
            expr = f"{a} ÷ {b} × ({c} + {d_})"; ans = a//b*(c + d_); naive = a//(b*(c + d_))
            exp = f"brackets: {c+d_}, then LEFT to RIGHT: {a}÷{b}={a//b}, ×{c+d_}"
        else:
            b, d_ = r.randint(3, 9), r.choice([2, 3, 4, 5]); a = r.randint(2, 9); c = d_*r.randint(2, 6)
            expr = f"{a} × {b} − {c} ÷ {d_}"; ans = a*b - c//d_; naive = (a*b - c)//d_ if (a*b - c) % d_ == 0 else a*b - c
            exp = f"× and ÷ first: {a*b} − {c//d_}"
        if ans > 0 and naive != ans: break
    def card(rev):
        im = blank(); d = ImageDraw.Draw(im)
        sz = 120
        while d.textlength(expr + " = ?", font=font(sz)) > CW - 80: sz -= 4
        d.text((CW/2, CH/2 - 60), expr + " = " + (str(ans) if rev else "?"), font=font(sz), fill=DARK, anchor="mm")
        if rev:
            explain(im, exp, y=CH/2 + 90, col=PURPLE, size=40)
            explain(im, f"NOT {naive}!", y=CH/2 + 170, col=RED, size=56)
        else:
            d.text((CW/2, CH/2 + 120), "no calculator!", font=font(40), fill=GREY, anchor="mm")
        return im
    opts, k = shuffle_opts(r, ans, [naive] + num_wrong(r, ans, (1, 2, 10)))
    return dict(q=card(False), a=card(True), options=[str(o) for o in opts], correct=k, question="WHAT'S THE ANSWER?",
                banner=f"IT'S {ans}!", catch=True)

# =====================================================================
# 4. CUP SHUFFLE (animated pre-phase)
def cup_img(w=200, h=210, col=(220, 60, 70)):
    S = 3; im = Image.new("RGBA", (w*S, h*S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    top, bot = 0.18*w*S, 0.06*w*S
    d.polygon([(top, 10*S), (w*S - top, 10*S), (w*S - bot, h*S - 14*S), (bot, h*S - 14*S)], fill=col, outline=DARK, width=5*S)
    d.rounded_rectangle((bot - 6*S, h*S - 34*S, w*S - bot + 6*S, h*S - 4*S), 10*S, fill=tuple(int(c*0.8) for c in col), outline=DARK, width=5*S)
    for k in range(2):
        y = (0.35 + 0.22*k)*h*S
        d.line((top*0.8 + 14*S + k*4*S, y, w*S - top*0.8 - 14*S - k*4*S, y), fill=(255, 255, 255, 200), width=10*S)
    return im.resize((w, h), Image.LANCZOS)
CUP = None; BALL = None
def ball_img(r_=44):
    S = 3; im = Image.new("RGBA", (r_*2*S, r_*2*S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse((4*S, 4*S, (2*r_ - 4)*S, (2*r_ - 4)*S), fill=(255, 205, 50), outline=DARK, width=4*S)
    d.ellipse((18*S, 16*S, 36*S, 32*S), fill=(255, 245, 200))
    return im.resize((r_*2, r_*2), Image.LANCZOS)

def cups(seed, level):
    global CUP, BALL
    if CUP is None: CUP, BALL = cup_img(), ball_img()
    r = random.Random(seed)
    n_sw = [3, 5, 7, 9][level]; dur = [0.62, 0.5, 0.4, 0.32][level]
    xs = [190, 480, 770]; base = 600
    start = r.randrange(3); swaps = []
    for _ in range(n_sw):
        i, j = r.sample(range(3), 2); swaps.append((i, j))
    # cup identity per position over time; ball travels with cup 'start'
    pos = [0, 1, 2]  # pos[cup] = slot
    T_SHOW, T_DOWN = 0.9, 0.45
    pre = T_SHOW + T_DOWN + n_sw*dur + 0.25
    slots_after = []
    p = pos[:]
    for (i, j) in swaps:
        p[i], p[j] = p[j], p[i]; slots_after.append(p[:])  # swap cups i and j (cup -> slot map)
    final_slot = slots_after[-1][start] if swaps else start
    def draw(cup_xy, lift_cup=None, lift=0.0, show_ball_at=None, label=True, hl=None):
        im = blank(); d = ImageDraw.Draw(im)
        d.rounded_rectangle((60, base + 8, CW - 60, base + 40), 16, fill=(225, 200, 160))
        if show_ball_at is not None:
            paste_c(im, BALL, show_ball_at, base - 40)
        for c, (x, y) in enumerate(cup_xy):
            yy = y - (lift if c == lift_cup else 0)
            im.alpha_composite(CUP, (int(x - CUP.width/2), int(yy - CUP.height)))
        if label:
            for k, x in enumerate(xs):
                col = GREEN if hl == k else BADGE[k]
                d.ellipse((x - 36, base + 70, x + 36, base + 142), fill=col)
                d.text((x, base + 108), "ABC"[k], font=font(46), fill="white", anchor="mm")
        return im
    def anim(u):
        cur = [0, 1, 2]
        if u < T_SHOW:  # ball visible, its cup lifted
            lift = 170*(1 - max(0, (u - T_SHOW + 0.35)/0.35)) if u > T_SHOW - 0.35 else 170
            cxy = [(xs[c], base) for c in range(3)]
            return draw(cxy, start, lift, xs[start])
        if u < T_SHOW + T_DOWN:
            return draw([(xs[c], base) for c in range(3)], start, 0, None)
        v = u - T_SHOW - T_DOWN; k = min(int(v/dur), n_sw - 1) if n_sw else 0
        prev = [0, 1, 2] if k == 0 else slots_after[k - 1]
        frac = min(1, max(0, (v - k*dur)/dur)) if v < n_sw*dur else 1
        if v >= n_sw*dur: prev = slots_after[-1]; frac = 0; k = None
        cxy = []
        for c in range(3):
            sx = xs[prev[c]]; y = base
            if k is not None and c in swaps[k]:
                other = swaps[k][1] if c == swaps[k][0] else swaps[k][0]
                tx = xs[prev[other]]; e = 0.5 - 0.5*math.cos(math.pi*frac)
                x = sx + (tx - sx)*e; y = base - (90 if c == swaps[k][0] else -0)*math.sin(math.pi*frac) + (0 if c == swaps[k][0] else 25*math.sin(math.pi*frac))
                cxy.append((x, y))
            else: cxy.append((sx, y))
        return draw(cxy)
    final_xy = [(xs[slots_after[-1][c]], base) for c in range(3)]
    q = draw(final_xy)
    a = draw(final_xy, start, 170, xs[final_slot], hl=final_slot)
    opts = ["Cup A", "Cup B", "Cup C", "No ball"]
    return dict(q=q, a=a, options=opts, correct=final_slot, question="WHERE IS THE BALL?",
                banner=f"CUP {'ABC'[final_slot]}!", catch=False, pre=pre, anim=anim, pre_label="WATCH THE BALL!",
                sfx_times=[T_SHOW - 0.35] + [T_SHOW + T_DOWN + k*dur for k in range(n_sw)])

# =====================================================================
# 5. MAZE
def maze(seed, level):
    n = [7, 9, 11, 13][level]
    for attempt in range(200):
        r = random.Random(seed*1000 + attempt)
        walls = {}  # passages set
        pas = set(); vis = {(n//2, n//2)}; st = [(n//2, n//2)]
        while st:
            c = st[-1]; x, y = c
            nb = [(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)) if 0 <= x + dx < n and 0 <= y + dy < n and (x + dx, y + dy) not in vis]
            if nb:
                m = r.choice(nb); pas.add(frozenset((c, m))); vis.add(m); st.append(m)
            else: st.pop()
        ents = [(r.randrange(1, n - 1), 0, "T"), (n - 1, r.randrange(1, n - 1), "R"), (r.randrange(1, n - 1), n - 1, "B"), (0, r.randrange(1, n - 1), "L")]
        star = (n//2, n//2)
        def path(a, b, P):
            prev = {a: None}; dq = deque([a])
            while dq:
                c = dq.popleft()
                if c == b: break
                x, y = c
                for m in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    if m not in prev and frozenset((c, m)) in P: prev[m] = c; dq.append(m)
            if b not in prev: return None
            out = [b]
            while prev[out[-1]] is not None: out.append(prev[out[-1]])
            return out[::-1]
        good = r.randrange(4)
        pc = path(ents[good][:2], star, pas)
        if len(pc) < n*1.4: continue
        pce = {frozenset((pc[i], pc[i + 1])) for i in range(len(pc) - 1)}
        ok = True; P2 = set(pas)
        for k, e in enumerate(ents):
            if k == good: continue
            pw = path(e[:2], star, P2)
            if pw is None: continue
            cand = [frozenset((pw[i], pw[i + 1])) for i in range(len(pw) - 1) if frozenset((pw[i], pw[i + 1])) not in pce]
            if not cand: ok = False; break
            P2.discard(cand[len(cand)//2])
        if not ok: continue
        if path(ents[good][:2], star, P2) is None: continue
        if any(path(e[:2], star, P2) for k, e in enumerate(ents) if k != good): continue
        pas = P2; break
    side = 640; cs = side/n; ox = (CW - side)/2; oy = (CH - side)/2
    def C(x, y): return (ox + (x + 0.5)*cs, oy + (y + 0.5)*cs)
    def draw(rev):
        im = blank(); d = ImageDraw.Draw(im); w = max(6, int(cs*0.16))
        segs = []
        for x in range(n):
            for y in range(n):
                X0, Y0 = ox + x*cs, oy + y*cs
                if y == 0 and not (ents[0][0] == x and ents[0][1] == 0): segs.append((X0, Y0, X0 + cs, Y0))
                if x == 0 and not (ents[3][0] == 0 and ents[3][1] == y): segs.append((X0, Y0, X0, Y0 + cs))
                if x == n - 1 and not (ents[1][1] == y): segs.append((X0 + cs, Y0, X0 + cs, Y0 + cs))
                elif x < n - 1 and frozenset(((x, y), (x + 1, y))) not in pas: segs.append((X0 + cs, Y0, X0 + cs, Y0 + cs))
                if y == n - 1 and not (ents[2][0] == x): segs.append((X0, Y0 + cs, X0 + cs, Y0 + cs))
                elif y < n - 1 and frozenset(((x, y), (x, y + 1))) not in pas: segs.append((X0, Y0 + cs, X0 + cs, Y0 + cs))
        if rev:
            pc = None
            prev = {ents[good][:2]: None}; dq = deque([ents[good][:2]])
            while dq:
                c = dq.popleft(); x, y = c
                for m in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    if m not in prev and frozenset((c, m)) in pas: prev[m] = c; dq.append(m)
            p = [star]
            while prev[p[-1]] is not None: p.append(prev[p[-1]])
            pts = [C(*c) for c in p[::-1]]
            e = ents[good]; ex, ey = C(e[0], e[1])
            off = {"T": (0, -cs), "R": (cs, 0), "B": (0, cs), "L": (-cs, 0)}[e[2]]
            d.line([(ex + off[0], ey + off[1])] + pts, fill=(255, 120, 110), width=int(cs*0.4), joint="curve")
        for s in segs:
            d.line(s, fill=DARK, width=w)
            for px, py in ((s[0], s[1]), (s[2], s[3])): d.ellipse((px - w/2, py - w/2, px + w/2, py + w/2), fill=DARK)
        sx, sy = C(*star); sti = em("⭐", int(cs*0.9)); paste_c(im, sti, sx, sy)
        for k, e in enumerate(ents):
            ex, ey = C(e[0], e[1]); off = {"T": (0, -cs*1.05), "R": (cs*1.05, 0), "B": (0, cs*1.05), "L": (-cs*1.05, 0)}[e[2]]
            bx, by = ex + off[0], ey + off[1]; rr = 34
            col = GREEN if (rev and k == good) else BADGE[k]
            d.ellipse((bx - rr, by - rr, bx + rr, by + rr), fill=col, outline="white", width=4)
            d.text((bx, by + 2), "ABCD"[k], font=font(40), fill="white", anchor="mm")
        return im
    opts = ["Path A", "Path B", "Path C", "Path D"]
    return dict(q=draw(False), a=draw(True), options=opts, correct=good, question="WHICH PATH REACHES THE STAR?",
                banner=f"PATH {'ABCD'[good]}!", catch=False)

# =====================================================================
# 6. BALANCE SCALES
def scale_img(left, right, w=420, h=230, tilt=0.0):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    cx = w/2; d.polygon([(cx - 38, h - 6), (cx + 38, h - 6), (cx, 70)], fill=(130, 110, 150), outline=DARK)
    d.rounded_rectangle((cx - 80, h - 20, cx + 80, h - 4), 8, fill=(110, 90, 130))
    by = 70; d.line((26, by, w - 26, by), fill=DARK, width=10); d.ellipse((cx - 12, by - 12, cx + 12, by + 12), fill=(255, 200, 70), outline=DARK, width=4)
    for side, items in ((0, left), (1, right)):
        px = 26 + 64 if side == 0 else w - 26 - 64; py = by + 90
        d.line((px - 56, py, px, by), fill=(120, 120, 140), width=4); d.line((px + 56, py, px, by), fill=(120, 120, 140), width=4)
        d.chord((px - 74, py - 30, px + 74, py + 30), 0, 180, fill=(200, 200, 215), outline=DARK, width=4)
        n = len(items); sz = 54 if n <= 3 else 44
        per = 3 if n > 3 else n
        for i, e in enumerate(items):
            row = i//per; col = i % per; cnt = min(per, n - row*per)
            x = px + (col - (cnt - 1)/2)*sz*0.92; y = py - sz*0.45 - row*sz*0.8
            paste_c(im, em(e, sz), x, y)
    return im

def balance(seed, level):
    r = random.Random(seed); A, B, C = r.choice([["🍉", "🍍", "🍒"], ["🐘", "🐷", "🐭"], ["🎃", "🍎", "🍓"], ["🦁", "🐶", "🐥"]])
    if level <= 1:
        x, y = r.randint(2, 3), r.randint(2, 3)
        s1 = ([A], [B]*x); s2 = ([B], [C]*y); ans = x*y; exp = f"1 {A} = {x} {B} = {x}×{y} {C}"
        wrong = [x + y, ans + 1, ans - 2]
    else:
        x = r.randint(2, 3); y = r.randint(2, 4)
        s1 = ([A, A], [B]*(2*x)); s2 = ([B, B], [C]*(2*y)) if 2*y <= 6 else ([B], [C]*y); ans = x*y
        exp = f"{A} = {x}{B},  {B} = {y}{C}  →  {x}×{y}"
        wrong = [x + y, 2*x*y, ans + 2, ans - 1]
    def card(rev):
        im = blank(); d = ImageDraw.Draw(im)
        for k, (l, rr) in enumerate((s1, s2)):
            si = scale_img(l, rr); si = si.resize((int(si.width*1.06), int(si.height*1.06)), Image.LANCZOS); im.alpha_composite(si, (int(CW/4 + k*CW/2 - si.width/2), 60))
        parts = [("t", "1"), ("e", A), ("t", "="), ("t", str(ans) if rev else "?", GREEN if rev else RED), ("e", C)]
        ri = row_img(parts, 150); im.alpha_composite(ri, (int(CW/2 - ri.width/2), 390))
        if rev: explain(im, f"{x} × {y} = {ans}", y=CH - 120, col=PURPLE, size=48)
        else: d.text((CW/2, CH - 110), "the scales are balanced", font=font(36), fill=GREY, anchor="mm")
        return im
    opts, k = shuffle_opts(r, ans, wrong + num_wrong(r, ans))
    return dict(q=card(False), a=card(True), options=[str(o) for o in opts], correct=k, question="HOW MANY BALANCE IT?",
                banner=f"{ans}!", catch=False)

# =====================================================================
# 7. SHAPE ROTATION (polyomino)
def norm(cells):
    mx = min(x for x, y in cells); my = min(y for x, y in cells); return frozenset((x - mx, y - my) for x, y in cells)
def rot(cells): return norm({(y, -x) for x, y in cells})
def mir(cells): return norm({(-x, y) for x, y in cells})
def rots(c):
    out = [norm(c)]
    for _ in range(3): out.append(rot(out[-1]))
    return out
def poly(r, n):
    while True:
        cells = {(0, 0)}
        while len(cells) < n:
            x, y = r.choice(list(cells)); dx, dy = r.choice(((1, 0), (-1, 0), (0, 1), (0, -1))); cells.add((x + dx, y + dy))
        c = norm(cells); R = rots(c)
        if len(set(R)) == 4 and mir(c) not in R:
            w = max(x for x, y in c) + 1; h = max(y for x, y in c) + 1
            if w <= 4 and h <= 4: return c

def shape_rotate(seed, level):
    r = random.Random(seed); n = [5, 6, 6, 7][level]
    base = poly(r, n); R = rots(base)
    correct_shape = R[r.choice([1, 2, 3])]
    M = rots(mir(base))
    distract = r.sample(M, 2)
    # third: one cell moved
    while True:
        cells = set(base); cells.remove(r.choice(list(cells)))
        x, y = r.choice(list(cells)); dx, dy = r.choice(((1, 0), (-1, 0), (0, 1), (0, -1)))
        cells.add((x + dx, y + dy))
        if len(cells) == n:
            c = norm(cells)
            # connected?
            st = [next(iter(c))]; seen = set(st)
            while st:
                a, b = st.pop()
                for m in ((a + 1, b), (a - 1, b), (a, b + 1), (a, b - 1)):
                    if m in c and m not in seen: seen.add(m); st.append(m)
            if len(seen) == n and c not in R and c not in M:
                distract.append(r.choice(rots(c))); break
    shapes = distract + [correct_shape]; r.shuffle(shapes); k = shapes.index(correct_shape)
    col = r.choice([(52, 152, 219), (155, 89, 182), (243, 156, 18), (26, 188, 156)])
    def draw_shape(d, cells, cx, cy, cell):
        w = max(x for x, y in cells) + 1; h = max(y for x, y in cells) + 1
        x0 = cx - w*cell/2; y0 = cy - h*cell/2
        for x, y in cells:
            d.rounded_rectangle((x0 + x*cell + 2, y0 + y*cell + 2, x0 + (x + 1)*cell - 2, y0 + (y + 1)*cell - 2), int(cell*0.18), fill=col, outline=DARK, width=4)
    def card(rev):
        im = blank(); d = ImageDraw.Draw(im)
        d.rounded_rectangle((CW/2 - 170, 24, CW/2 + 170, 350), 30, fill=SOFT)
        d.text((CW/2, 60), "THIS SHAPE", font=font(30), fill=GREY, anchor="mm")
        draw_shape(d, base, CW/2, 200, 58)
        for i, s in enumerate(shapes):
            cx = 125 + i*237; cy = 560
            if rev and i == k: d.rounded_rectangle((cx - 112, cy - 150, cx + 112, cy + 150), 26, outline=GREEN, width=10)
            draw_shape(d, s, cx, cy - 10, 48)
            d.ellipse((cx - 30, cy + 100, cx + 30, cy + 160), fill=GREEN if (rev and i == k) else BADGE[i])
            d.text((cx, cy + 132), "ABCD"[i], font=font(36), fill="white", anchor="mm")
        if rev: explain(im, "the others are MIRRORED or changed!", y=CH - 30, col=RED, size=34)
        return im
    return dict(q=card(False), a=card(True), options=[f"Shape {c}" for c in "ABCD"], correct=k,
                question="WHICH IS THE SAME SHAPE, JUST ROTATED?", banner=f"SHAPE {'ABCD'[k]}!", catch=False)

# =====================================================================
# 8. CLOCK
def clock_card(h, m, label=None, hl=False):
    im = blank(); d = ImageDraw.Draw(im); cx, cy, R = CW/2, CH/2 - 20, 300
    d.ellipse((cx - R - 16, cy - R - 16, cx + R + 16, cy + R + 16), fill=(255, 140, 120) if not hl else GREEN)
    d.ellipse((cx - R, cy - R, cx + R, cy + R), fill="white", outline=DARK, width=8)
    for k in range(60):
        a = math.radians(k*6 - 90); r1 = R - (34 if k % 5 == 0 else 18)
        d.line((cx + math.cos(a)*r1, cy + math.sin(a)*r1, cx + math.cos(a)*(R - 8), cy + math.sin(a)*(R - 8)), fill=DARK, width=7 if k % 5 == 0 else 3)
    for k in range(1, 13):
        a = math.radians(k*30 - 90); d.text((cx + math.cos(a)*(R - 72), cy + math.sin(a)*(R - 72) + 3), str(k), font=font(48), fill=DARK, anchor="mm")
    ah = math.radians((h % 12 + m/60)*30 - 90); am = math.radians(m*6 - 90)
    d.line((cx, cy, cx + math.cos(ah)*R*0.5, cy + math.sin(ah)*R*0.5), fill=DARK, width=20)
    d.line((cx, cy, cx + math.cos(am)*R*0.78, cy + math.sin(am)*R*0.78), fill=(60, 120, 220), width=12)
    d.ellipse((cx - 18, cy - 18, cx + 18, cy + 18), fill=RED)
    if label: explain(im, label, y=CH - 34, col=PURPLE if not hl else GREEN, size=40)
    return im

def fmt(h, m): h = h % 12; h = 12 if h == 0 else h; return f"{h}:{m:02d}"
def clock(seed, level):
    r = random.Random(seed)
    h = r.randint(1, 12); m = r.choice([0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55])
    delta = [r.choice([15, 30]), r.choice([45, 50, 40]), r.choice([95, 105, 135]), -r.choice([155, 170, 125])][level]
    tot = (h*60 + m + delta) % 720; ah, am = tot//60, tot % 60
    ans = fmt(ah, am)
    word = (f"IN {delta} MIN" if delta < 60 else f"IN {delta//60}H {delta%60}MIN") if delta > 0 else f"{-delta//60}H {(-delta)%60}MIN AGO"
    wrong = []
    for dd in (60, -60, 15, -15, 30, 10):
        t2 = (tot + dd) % 720; wrong.append(fmt(t2//60, t2 % 60))
    t3 = (h*60 + m - delta) % 720; wrong.insert(0, fmt(t3//60, t3 % 60))  # wrong direction trap
    opts, k = shuffle_opts(r, ans, wrong)
    return dict(q=clock_card(h, m, f"what time will it be {word.lower()}?" if delta > 0 else f"what time was it {word.lower()}?"),
                a=clock_card(ah, am, f"{fmt(h, m)}  {'+' if delta > 0 else '−'} {abs(delta)//60}h {abs(delta)%60}m  =  {ans}", hl=True),
                options=opts, correct=k, question=f"WHAT TIME {('IN ' + word[3:]) if delta > 0 else ('WAS IT ' + word)}?",
                banner=f"{ans}!", catch=False)

# =====================================================================
# 9. SPOT THE DIFFERENCE (count)
SCENE = ["🌳", "🏠", "🚗", "🐶", "🌻", "☁️", "🎈", "🐱", "🌵", "🍄", "🐝", "🦋", "🚲", "⚽", "🐸", "🍎", "🌙", "⭐"]
def spot_diff(seed, level):
    r = random.Random(seed); k = [2, 3, 3, 4][level]; n = [8, 10, 12, 14][level]; sz = [96, 86, 76, 70][level]
    PW, PH = 900, 350
    items = []
    for _ in range(4000):
        if len(items) >= n: break
        x, y = r.uniform(60, PW - 60), r.uniform(55, PH - 55)
        if all(math.hypot(x - a, y - b) > sz*1.05 for _, a, b, _f, _s in items): items.append([r.choice(SCENE), x, y, False, 1.0])
    alt = [list(it) for it in items]; idx = r.sample(range(len(items)), k); marks = []
    kinds = r.sample(["swap", "remove", "flip", "size", "swap", "remove"], k)
    for i, kd in zip(idx, kinds):
        if kd == "swap": alt[i][0] = r.choice([e for e in SCENE if e != items[i][0]])
        elif kd == "remove": alt[i][0] = None
        elif kd == "flip":
            if items[i][0] in ("⚽", "☁️", "🌙", "⭐", "🍎", "🌻", "🍄"): alt[i][0] = r.choice([e for e in SCENE if e != items[i][0]])
            else: alt[i][3] = True
        else: alt[i][4] = 0.62
        marks.append((items[i][1], items[i][2]))
    def panel(its, top):
        p = Image.new("RGBA", (PW, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(p)
        d.rounded_rectangle((0, 0, PW - 1, PH - 1), 30, fill=(226, 244, 255) if top else (226, 244, 255), outline=(190, 205, 225), width=4)
        d.rounded_rectangle((0, PH*0.72, PW - 1, PH - 1), 30, fill=(205, 236, 190))
        for e, x, y, fl, s in its:
            if e is None: continue
            im = em(e, int(sz*s))
            if fl: im = im.transpose(Image.FLIP_LEFT_RIGHT)
            paste_c(p, im, x, y)
        return p
    def card(rev):
        im = blank(); d = ImageDraw.Draw(im)
        im.alpha_composite(panel(items, True), (30, 30)); im.alpha_composite(panel(alt, False), (30, 30 + PH + 40))
        if rev:
            for x, y in marks:
                for oy in (30, 30 + PH + 40):
                    d.ellipse((30 + x - sz*0.75, oy + y - sz*0.75, 30 + x + sz*0.75, oy + y + sz*0.75), outline=RED, width=9)
        return im
    opts, kk = shuffle_opts(r, k, [k - 1, k + 1, k + 2, k - 2])
    return dict(q=card(False), a=card(True), options=[str(o) for o in opts], correct=kk, question="HOW MANY DIFFERENCES?",
                banner=f"{k} DIFFERENCES!", catch=False)

# =====================================================================
# 10. MEMORY (animated pre-phase)
MEM = ["🐸", "🦊", "🐼", "🐙", "🦄", "🐳", "🍓", "🚀", "🎸", "🍦", "🐢", "🌈", "🦒", "⚡"]
def memory(seed, level):
    r = random.Random(seed); n = [4, 6, 6, 9][level]; show = [4.0, 3.5, 2.8, 3.2][level]
    cols = 2 if n == 4 else 3; rows = n//cols
    items = r.sample(MEM, n); target = r.randrange(n)
    cell = 230 if n <= 6 else 210; gx = (CW - cols*cell)/2; gy = 140 + (CH - 140 - rows*cell)/2 - 10
    def draw(mode, flip=1.0):
        im = blank(); d = ImageDraw.Draw(im)
        if mode != "show":
            d.text((CW/2 - 70, 75), "FIND:", font=font(48), fill=DARK, anchor="mm"); paste_c(im, em(items[target], 92), CW/2 + 80, 75)
        else:
            d.text((CW/2, 75), "REMEMBER THEM!", font=font(48), fill=PURPLE, anchor="mm")
        for i, e in enumerate(items):
            c, rr = i % cols, i//cols; x0 = gx + c*cell + 12; y0 = gy + rr*cell + 12; w = cell - 24
            face = mode in ("show", "ans") if flip >= 0 else False
            sx = abs(flip)
            cx = x0 + w/2
            hl = mode == "ans" and i == target
            fill = (255, 255, 255) if face else (125, 95, 220)
            d.rounded_rectangle((cx - w/2*sx, y0, cx + w/2*sx, y0 + w), 28, fill=fill, outline=GREEN if hl else DARK, width=12 if hl else 5)
            if sx > 0.3:
                if face: paste_c(im, em(e, int(w*0.62*sx) or 1), cx, y0 + w/2)
                else: d.text((cx, y0 + w/2 + 4), "?", font=font(int(90*sx) or 1), fill="white", anchor="mm")
            d.ellipse((x0 - 6, y0 - 6, x0 + 46, y0 + 46), fill=GREEN if hl else BADGE[i % 4])
            d.text((x0 + 20, y0 + 21), str(i + 1), font=font(32), fill="white", anchor="mm")
        return im
    pre = show + 0.45
    def anim(u):
        if u < show: return draw("show")
        f = (u - show)/0.45; fl = math.cos(f*math.pi)  # 1 → -1
        return draw("show" if fl > 0 else "hide", fl if fl > 0 else -fl)
    wrong = r.sample([i for i in range(n) if i != target], 3)
    opts = [f"Tile {i + 1}" for i in wrong] + [f"Tile {target + 1}"]; r.shuffle(opts)
    return dict(q=draw("hide"), a=draw("ans"), options=opts, correct=opts.index(f"Tile {target + 1}"),
                question="WHERE WAS IT?", banner=f"TILE {target + 1}!", catch=False, pre=pre, anim=anim, pre_label="MEMORIZE!", sfx_times=[show])

# =====================================================================
# 11. COUNT TRIANGLES (catch)
def triangles(seed, level):
    r = random.Random(seed)
    m, h = [(1, 0), (2, 0), (2, 1), (3, 1)][level]
    per = (m + 2)*(m + 1)//2; ans = per*(h + 1)
    apex = (CW/2, 70); bl = (CW/2 - 380, CH - 110); br = (CW/2 + 380, CH - 110)
    fr = sorted(r.sample([0.22, 0.3, 0.42, 0.5, 0.6, 0.7, 0.78], m))
    hs = [0.55] if h == 1 else []
    def lerp(a, b, t): return (a[0] + (b[0] - a[0])*t, a[1] + (b[1] - a[1])*t)
    def card(rev):
        im = blank(); d = ImageDraw.Draw(im)
        if rev:
            cols = [(255, 214, 226), (210, 235, 255), (220, 245, 210)]
            d.polygon([apex, bl, br], fill=(255, 245, 205))
        d.polygon([apex, bl, br], outline=DARK, width=12)
        for f in fr: d.line([apex, lerp(bl, br, f)], fill=DARK, width=10)
        for f in hs: d.line([lerp(apex, bl, f), lerp(apex, br, f)], fill=DARK, width=10)
        for p in [apex, bl, br]: d.ellipse((p[0] - 6, p[1] - 6, p[0] + 6, p[1] + 6), fill=DARK)
        if rev:
            t = f"{per} triangles per base line" + (f" × {h + 1} lines = {ans}" if h else f" = {ans}")
            explain(im, t, y=CH - 40, col=RED, size=40)
        return im
    wrong = ([m + 2, ans - 2, ans - 1, ans + 2, per + m] if h else [m + 2, m + 1, ans + 1, ans - 1]) + num_wrong(r, ans, (1, 2, 3))
    opts, k = shuffle_opts(r, ans, wrong)
    return dict(q=card(False), a=card(True), options=[str(o) for o in opts], correct=k, question="HOW MANY TRIANGLES?",
                banner=f"{ans} TRIANGLES!", catch=True)

# =====================================================================
# 12. DICE
def die_face(v, s=200, col=(255, 255, 255)):
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((4, 4, s - 4, s - 4), int(s*0.17), fill=col, outline=DARK, width=max(4, s//30))
    P = {1: [(.5, .5)], 2: [(.27, .27), (.73, .73)], 3: [(.27, .27), (.5, .5), (.73, .73)], 4: [(.27, .27), (.73, .27), (.27, .73), (.73, .73)],
         5: [(.27, .27), (.73, .27), (.5, .5), (.27, .73), (.73, .73)], 6: [(.27, .25), (.73, .25), (.27, .5), (.73, .5), (.27, .75), (.73, .75)]}
    rr = s*0.085
    for x, y in P[v]: d.ellipse((x*s - rr, y*s - rr, x*s + rr, y*s + rr), fill=RED if v == 1 else DARK)
    return im

def dice(seed, level):
    r = random.Random(seed)
    if level <= 1:
        n = [2, 3][level]; vals = [r.randint(1, 6) for _ in range(n)]; ans = sum(vals)
        def card(rev):
            im = blank(); d = ImageDraw.Draw(im); s = 230 if n == 2 else 210
            for i, v in enumerate(vals):
                f = die_face(v, s).rotate(r.Random(seed + i).uniform(-14, 14) if False else (i*9 - 9), expand=True, resample=Image.BICUBIC)
                paste_c(im, f, CW/2 + (i - (n - 1)/2)*(s + 70), CH/2 - 40)
            if rev: explain(im, " + ".join(map(str, vals)) + f" = {ans}", y=CH - 120, col=GREEN, size=60)
            return im
        opts, k = shuffle_opts(r, ans, num_wrong(r, ans, (1, 2, 3)))
        return dict(q=card(False), a=card(True), options=[str(o) for o in opts], correct=k, question="HOW MANY DOTS IN TOTAL?",
                    banner=f"{ans} DOTS!", catch=False)
    # bottom-of-stack trick: 3 dice stacked, hidden faces (touching + bottom) total = 21 - top
    top = r.randint(1, 6); ans = 21 - top
    def card(rev):
        im = blank(); d = ImageDraw.Draw(im)
        for i in range(3):
            paste_c(im, die_face(r.Random(i).randint(1, 6) if False else [3, 5, 2][i], 170, (235, 235, 245)), CW/2 - 160, 610 - i*175)
        paste_c(im, die_face(top, 170), CW/2 - 160, 610 - 2*175)
        d.text((CW/2 + 210, 250), "add the dots", font=font(40), fill=DARK, anchor="mm")
        d.text((CW/2 + 210, 305), "you CAN'T see:", font=font(40), fill=DARK, anchor="mm")
        d.text((CW/2 + 210, 370), "between the dice", font=font(34), fill=GREY, anchor="mm")
        d.text((CW/2 + 210, 415), "+ the very bottom", font=font(34), fill=GREY, anchor="mm")
        if rev:
            explain(im, "opposite sides always add to 7", y=CH - 140, col=PURPLE, size=40)
            explain(im, f"7 + 7 + 7 − {top} (top) = {ans}", y=CH - 80, col=GREEN, size=48)
        return im
    opts, k = shuffle_opts(r, ans, [ans + 1, ans - 2, 7 - top, ans + 3])
    return dict(q=card(False), a=card(True), options=[str(o) for o in opts], correct=k, question="HOW MANY HIDDEN DOTS?",
                banner=f"{ans} HIDDEN DOTS!", catch=True)

# =====================================================================
# 13. ANAGRAM
WORDS = {5: ["APPLE", "TIGER", "HOUSE", "PIZZA", "ROBOT", "SNAKE", "CLOUD", "LEMON", "HORSE", "TRAIN", "MOUSE", "PLANT"],
         6: ["ORANGE", "GUITAR", "PENCIL", "CASTLE", "ROCKET", "GARDEN", "MONKEY", "PIRATE", "PLANET", "BUTTER", "CANDLE", "DRAGON"],
         7: ["KITCHEN", "DOLPHIN", "PICTURE", "RAINBOW", "TEACHER", "BALLOON", "CHICKEN", "MONSTER", "PENGUIN", "BLANKET"]}
def anagram(seed, level):
    r = random.Random(seed); L = [5, 6, 7, 7][level]; w = r.choice(WORDS[L])
    while True:
        s = list(w); r.shuffle(s); s = "".join(s)
        if s != w and all(s[i:i + 3] not in w for i in range(len(s) - 2)): break
    wrong = r.sample([x for x in WORDS[L] if x != w], 3)
    def card(rev):
        im = blank(); d = ImageDraw.Draw(im); n = len(w); tw = min(118, (CW - 80)//n - 10)
        cols = [(255, 214, 226), (210, 235, 255), (220, 245, 210), (255, 236, 179), (232, 220, 255)]
        for row, txt in enumerate([s] + ([w] if rev else [])):
            y = CH/2 - 60 + row*170 - (60 if rev else 0)
            x0 = CW/2 - (n*tw + (n - 1)*10)/2
            for i, ch in enumerate(txt):
                x = x0 + i*(tw + 10)
                fill = (GREEN if row else cols[i % 5])
                d.rounded_rectangle((x, y - tw/2, x + tw, y + tw/2), 20, fill=fill, outline=DARK, width=5)
                d.text((x + tw/2, y + 4), ch, font=font(int(tw*0.62)), fill="white" if row else DARK, anchor="mm")
        if not rev: d.text((CW/2, CH/2 + 120), "unscramble the letters", font=font(40), fill=GREY, anchor="mm")
        return im
    opts, k = shuffle_opts(r, w.title(), [x.title() for x in wrong])
    return dict(q=card(False), a=card(True), options=opts, correct=k, question="WHAT'S THE WORD?",
                banner=f"{w}!", catch=False)

# =====================================================================
# 14. ARROW TURNS
def arrow_img(size, ang, col):
    S = 3; s = size*S; im = Image.new("RGBA", (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.polygon([(s*0.5, s*0.08), (s*0.88, s*0.48), (s*0.64, s*0.48), (s*0.64, s*0.9), (s*0.36, s*0.9), (s*0.36, s*0.48), (s*0.12, s*0.48)],
              fill=col, outline=DARK)
    im = im.rotate(-ang, resample=Image.BICUBIC)
    return im.resize((size, size), Image.LANCZOS)

def turn_icon(dirn, size=110):
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    col = (52, 152, 219) if dirn == "R" else (243, 156, 18)
    d.rounded_rectangle((0, 0, size - 1, size - 1), 26, fill=col)
    c = size/2; rr = size*0.28
    if dirn == "R": a0, a1 = 200, 450
    else: a0, a1 = 90, 340
    d.arc((c - rr, c - rr, c + rr, c + rr), a0, a1, fill="white", width=10)
    a = math.radians(a1 if dirn == "R" else a0); P = (c + rr*math.cos(a), c + rr*math.sin(a))
    t = (-math.sin(a), math.cos(a)) if dirn == "R" else (math.sin(a), -math.cos(a)); nn = (math.cos(a), math.sin(a))
    d.polygon([(P[0] + t[0]*16, P[1] + t[1]*16), (P[0] + nn[0]*14, P[1] + nn[1]*14), (P[0] - nn[0]*14, P[1] - nn[1]*14)], fill="white")
    d.text((size - 18, size - 18), dirn, font=font(26), fill="white", anchor="mm")
    return im

def arrows(seed, level):
    r = random.Random(seed); n = [2, 4, 5, 7][level]
    start = r.choice([0, 90, 180, 270]); steps = [r.choice("RRL") for _ in range(n)]
    ang = (start + sum(90 if s == "R" else -90 for s in steps)) % 360
    NAMES = {0: "Up", 90: "Right", 180: "Down", 270: "Left"}
    def card(rev):
        im = blank(); d = ImageDraw.Draw(im)
        d.text((240, 70), "START", font=font(34), fill=GREY, anchor="mm")
        paste_c(im, arrow_img(260, start, (255, 205, 60)), 240, 270)
        d.text((240, 440), "turn 90° each step", font=font(28), fill=GREY, anchor="mm")
        if rev:
            d.text((CW - 220, 70), "END", font=font(34), fill=GREEN, anchor="mm")
            paste_c(im, arrow_img(260, ang, GREEN), CW - 220, 270)
        else:
            d.text((CW - 220, 270), "?", font=font(200), fill=(220, 220, 232), anchor="mm")
        icons = [turn_icon(s, 100 if n <= 5 else 88) for s in steps]
        tot = sum(i.width for i in icons) + 16*(n - 1); x = CW/2 - tot/2
        for i in icons: im.alpha_composite(i, (int(x), 560)); x += i.width + 16
        d.text((CW/2, 720), "R = turn right    L = turn left", font=font(32), fill=GREY, anchor="mm")
        return im
    opts = ["Up", "Right", "Down", "Left"]
    return dict(q=card(False), a=card(True), options=opts, correct=opts.index(NAMES[ang]), question="WHERE DOES THE ARROW POINT?",
                banner=f"{NAMES[ang].upper()}!", catch=False)

GENS = dict(emoji_math=emoji_math, sequence=sequence, order_ops=order_ops, cups=cups, maze=maze, balance=balance,
            shape_rotate=shape_rotate, clock=clock, spot_diff=spot_diff, memory=memory, triangles=triangles,
            dice=dice, anagram=anagram, arrows=arrows)
CATCH = {"order_ops", "triangles"}
# which puzzle types fit which level (0 easy .. 3 genius)
LEVEL_POOL = [
    ["anagram", "dice", "sequence", "clock", "emoji_math", "arrows", "spot_diff", "memory", "cups", "maze"],
    ["emoji_math", "balance", "cups", "maze", "shape_rotate", "sequence", "memory", "arrows", "order_ops", "triangles", "spot_diff", "clock", "anagram", "dice"],
    ["maze", "balance", "order_ops", "triangles", "spot_diff", "shape_rotate", "clock", "sequence", "cups", "emoji_math", "memory", "dice", "arrows"],
    ["emoji_math", "sequence", "cups", "memory", "maze", "shape_rotate", "triangles", "order_ops", "spot_diff", "clock", "dice", "arrows"],
]
