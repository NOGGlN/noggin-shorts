"""Batch-5 puzzle generators (all new types). Same dict contract as puzzles4."""
import math, random, itertools
from collections import deque
from PIL import Image, ImageDraw
from render import font, DARK
from v3 import CARD, blank, emoji, GREEN
from puzzles4 import (shuffle_opts, num_wrong, explain, em, paste_c, row_img, BADGE, RED, BLUE, ORANGE, PURPLE, GREY, SOFT, CW, CH)

def wrap(d, txt, f, maxw):
    words = txt.split(); lines = [""]
    for w in words:
        t = (lines[-1] + " " + w).strip()
        if d.textlength(t, font=f) <= maxw: lines[-1] = t
        else: lines.append(w)
    return lines

def text_block(im, txt, y, size, col=DARK, maxw=CW - 100, spacing=1.18):
    d = ImageDraw.Draw(im)
    while True:
        f = font(size); lines = wrap(d, txt, f, maxw)
        if len(lines) <= 4 or size <= 34: break
        size -= 4
    lh = size*spacing; y0 = y - lh*(len(lines) - 1)/2
    for k, ln in enumerate(lines): d.text((CW/2, y0 + k*lh), ln, font=f, fill=col, anchor="mm")
    return y0 + lh*len(lines)

def option_tiles(im, imgs, y, hl=None, box=200):
    d = ImageDraw.Draw(im); n = len(imgs); gap = (CW - n*box)/(n + 1)
    for i, g in enumerate(imgs):
        cx = gap + box/2 + i*(box + gap)
        d.rounded_rectangle((cx - box/2, y - box/2, cx + box/2, y + box/2), 24, fill=SOFT,
                            outline=GREEN if hl == i else (210, 212, 225), width=10 if hl == i else 4)
        paste_c(im, g, cx, y)
        d.ellipse((cx - 28, y + box/2 + 10, cx + 28, y + box/2 + 66), fill=GREEN if hl == i else BADGE[i])
        d.text((cx, y + box/2 + 39), "ABCD"[i], font=font(34), fill="white", anchor="mm")

# =====================================================================
# 1. MATCHSTICK EQUATIONS (move one match)
SEG = {0: set("abcdef"), 1: set("bc"), 2: set("abged"), 3: set("abgcd"), 4: set("fgbc"), 5: set("afgcd"),
       6: set("afgedc"), 7: set("abc"), 8: set("abcdefg"), 9: set("abcdfg")}
DIG = {frozenset(v): k for k, v in SEG.items()}
OPS = {frozenset("h"): "-", frozenset("hv"): "+"}

def eq_true(a, op, b, c): return (a + b if op == "+" else a - b) == c

def one_move_fixes(a, op, b, c):
    syms = [("d", SEG[a]), ("o", set("h") if op == "-" else set("hv")), ("d", SEG[b]), ("d", SEG[c])]
    allseg = [set("abcdefg"), set("hv"), set("abcdefg"), set("abcdefg")]
    out = set()
    for i, (ti, si) in enumerate(syms):
        for s in si:
            for j in range(4):
                for t in allseg[j] - (syms[j][1] - ({s} if i == j else set())):
                    if i == j and t == s: continue
                    new = [set(x[1]) for x in syms]; new[i].discard(s); new[j].add(t)
                    vals = []
                    ok = True
                    for k, (tk, _) in enumerate(syms):
                        fs = frozenset(new[k])
                        if tk == "d":
                            if fs not in DIG: ok = False; break
                            vals.append(DIG[fs])
                        else:
                            if fs not in OPS: ok = False; break
                            vals.append(OPS[fs])
                    if ok and eq_true(*vals): out.add((tuple(vals), (i, s, j, t)))
    return out

def draw_digit(d, segs, x, y, w, h, col_map=None):
    """seven-seg matches. x,y top-left."""
    P = {"a": ((x, y), (x + w, y)), "b": ((x + w, y), (x + w, y + h/2)), "c": ((x + w, y + h/2), (x + w, y + h)),
         "d": ((x, y + h), (x + w, y + h)), "e": ((x, y + h/2), (x, y + h)), "f": ((x, y), (x, y + h/2)), "g": ((x, y + h/2), (x + w, y + h/2))}
    for s in "abcdefg":
        if s in segs or (col_map and s in col_map): stick(d, *P[s], (col_map or {}).get(s))

def stick(d, p0, p1, mark=None):
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]; L = math.hypot(dx, dy); ux, uy = dx/L, dy/L; pad = 14
    a = (p0[0] + ux*pad, p0[1] + uy*pad); b = (p1[0] - ux*pad, p1[1] - uy*pad)
    if mark == "ghost":
        for k in range(6):
            t0, t1 = k/6, (k + 0.5)/6
            d.line((a[0] + (b[0] - a[0])*t0, a[1] + (b[1] - a[1])*t0, a[0] + (b[0] - a[0])*t1, a[1] + (b[1] - a[1])*t1), fill=(231, 76, 60), width=10)
        return
    wood = (236, 196, 120) if mark != "new" else (120, 220, 140)
    d.line((a, b), fill=(150, 110, 60), width=19); d.line((a, b), fill=wood, width=13)
    d.ellipse((b[0] - 10, b[1] - 10, b[0] + 10, b[1] + 10), fill=(215, 45, 45), outline=(120, 20, 20), width=2)

def draw_eq(im, vals, ghost=None, new=None):
    d = ImageDraw.Draw(im); a, op, b, c = vals
    w, h = 130, 250; y = CH/2 - h/2 - 50
    xs = [50, 220, 380, 560, 720]  # A, op, B, =, C
    marks = [{} for _ in range(4)]
    if ghost: marks[ghost[0]][ghost[1]] = "ghost"
    if new: marks[new[0]][new[1]] = "new"
    draw_digit(d, SEG[a] - set(marks[0]) if marks[0] else SEG[a], xs[0], y, w, h, marks[0] or None)
    cx = xs[1] + 60; cy = y + h/2
    opseg = {"h"} | ({"v"} if op == "+" else set())
    for s, ((p0, p1)) in (("h", ((cx - 55, cy), (cx + 55, cy))), ("v", ((cx, cy - 55), (cx, cy + 55)))):
        m = marks[1].get(s)
        if s in opseg and m != "ghost": stick(d, p0, p1, m)
        elif m: stick(d, p0, p1, m)
    draw_digit(d, SEG[b] - set(marks[2]) if marks[2] else SEG[b], xs[2], y, w, h, marks[2] or None)
    ex = xs[3] + 55
    for dy in (-26, 26): stick(d, (ex - 50, cy + dy), (ex + 50, cy + dy))
    draw_digit(d, SEG[c] - set(marks[3]) if marks[3] else SEG[c], xs[4], y, w, h, marks[3] or None)

def matchstick(seed, level):
    r = random.Random(seed)
    for _ in range(20000):
        a, b, c = r.randint(0, 9), r.randint(0, 9), r.randint(0, 9); op = r.choice("+-")
        if eq_true(a, op, b, c): continue
        fixes = one_move_fixes(a, op, b, c)
        sols = {f[0] for f in fixes}
        if len(sols) != 1: continue
        sol = next(iter(sols)); mv = next(f[1] for f in fixes if f[0] == sol)
        # harder levels: the fix changes the operator or two different symbols far apart
        if level >= 2 and mv[0] == mv[2]: continue
        break
    fmt = lambda v: f"{v[0]} {'+' if v[1] == '+' else '−'} {v[2]} = {v[3]}"
    wrong = set()
    while len(wrong) < 3:
        x, y = r.randint(0, 9), r.randint(0, 9); o = r.choice("+-"); z = x + y if o == "+" else x - y
        if 0 <= z <= 9 and (x, o, y, z) != sol: wrong.add((x, o, y, z))
    q = blank(); draw_eq(q, (a, op, b, c))
    ImageDraw.Draw(q).text((CW/2, CH - 110), "move ONE match to make it true", font=font(40), fill=GREY, anchor="mm")
    an = blank()
    # answer: show the solved equation, the moved match green and a red ghost where it was
    i, s, j, t = mv; vals = list((a, op, b, c))
    draw_eq(an, sol, ghost=None, new=(j, t))
    # ghost: draw the removed stick location on the solved layout
    d = ImageDraw.Draw(an); w, h = 130, 250; y0 = CH/2 - h/2 - 50; xs = [50, 220, 380, 560, 720]
    if i in (0, 2, 3):
        x0 = xs[[0, None, 2, 4][i]]
        P = {"a": ((x0, y0), (x0 + w, y0)), "b": ((x0 + w, y0), (x0 + w, y0 + h/2)), "c": ((x0 + w, y0 + h/2), (x0 + w, y0 + h)),
             "d": ((x0, y0 + h), (x0 + w, y0 + h)), "e": ((x0, y0 + h/2), (x0, y0 + h)), "f": ((x0, y0), (x0, y0 + h/2)), "g": ((x0, y0 + h/2), (x0 + w, y0 + h/2))}
        stick(d, *P[s], "ghost")
    else:
        cx = xs[1] + 60; cy = y0 + h/2; stick(d, (cx, cy - 55), (cx, cy + 55), "ghost")
    explain(an, "red = where it was,  green = where it goes", y=CH - 110, col=PURPLE, size=36)
    opts = [fmt(w_) for w_ in wrong] + [fmt(sol)]; r.shuffle(opts)
    return dict(q=q, a=an, options=opts, correct=opts.index(fmt(sol)), question="MOVE 1 MATCH TO FIX IT!",
                banner="FIXED: " + fmt(sol), catch=False)

# =====================================================================
# 2. CUBE NET
def norm(c):
    mx = min(x for x, y in c); my = min(y for x, y in c); return frozenset((x - mx, y - my) for x, y in c)
def variants(c):
    out = set(); cur = set(c)
    for m in range(2):
        for k in range(4):
            out.add(norm(cur)); cur = {(y, -x) for x, y in cur}
        cur = {(-x, y) for x, y in cur}
    return out
def is_net(cells):
    cells = set(cells)
    for x, y in cells:
        if {(x + 1, y), (x, y + 1), (x + 1, y + 1)} <= cells: return False
    start = next(iter(cells)); orient = {start: dict(D="0", U="1", N="2", S="3", E="4", W="5")}
    dq = deque([start])
    def roll(o, dirn):
        o = dict(o)
        if dirn == "E": o["D"], o["E"], o["U"], o["W"] = o["E"], o["U"], o["W"], o["D"]
        if dirn == "W": o["D"], o["W"], o["U"], o["E"] = o["W"], o["U"], o["E"], o["D"]
        if dirn == "S": o["D"], o["S"], o["U"], o["N"] = o["S"], o["U"], o["N"], o["D"]
        if dirn == "N": o["D"], o["N"], o["U"], o["S"] = o["N"], o["U"], o["S"], o["D"]
        return o
    while dq:
        c = dq.popleft(); x, y = c
        for dirn, m in (("E", (x + 1, y)), ("W", (x - 1, y)), ("S", (x, y + 1)), ("N", (x, y - 1))):
            if m in cells and m not in orient: orient[m] = roll(orient[c], dirn); dq.append(m)
    return len({o["D"] for o in orient.values()}) == 6

def all_hexominoes():
    shapes = {frozenset({(0, 0)})}
    for n in range(2, 7):
        new = set()
        for s in shapes:
            for x, y in s:
                for m in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    if m not in s:
                        v = min(variants(s | {m}), key=lambda z: sorted(z)); new.add(v)
        shapes = new
    return list(shapes)
HEX = None
def cube_net(seed, level):
    global HEX
    if HEX is None: HEX = sorted(all_hexominoes(), key=lambda z: sorted(z))
    r = random.Random(seed)
    nets = [h for h in HEX if is_net(h)]; non = [h for h in HEX if not is_net(h) and max(x for x, y in h) <= 4 and max(y for x, y in h) <= 4]
    # prefer tricky non-nets: no 2x2 block (look plausible)
    tricky = [h for h in non if not any({(x + 1, y), (x, y + 1), (x + 1, y + 1)} <= set(h) for x, y in h)]
    good = r.choice(nets); bad = r.sample(tricky if level >= 2 else non, 3)
    shapes = [r.choice(list(variants(s))) for s in bad + [good]]; r.shuffle(shapes)
    k = [is_net(s) for s in shapes].index(True)
    col = r.choice([(52, 152, 219), (243, 156, 18), (155, 89, 182), (26, 188, 156)])
    def shape_img(cells, cell=34, hl=False):
        w = max(x for x, y in cells) + 1; h = max(y for x, y in cells) + 1
        im = Image.new("RGBA", (int(w*cell) + 8, int(h*cell) + 8), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        for x, y in cells: d.rectangle((4 + x*cell, 4 + y*cell, 4 + (x + 1)*cell, 4 + (y + 1)*cell), fill=GREEN if hl else col, outline=DARK, width=4)
        return im
    def card(rev):
        im = blank(); d = ImageDraw.Draw(im)
        # small cube icon
        cx, cy, s = CW/2, 150, 70
        top = [(cx, cy - s), (cx + s*0.9, cy - s*0.5), (cx, cy), (cx - s*0.9, cy - s*0.5)]
        d.polygon(top, fill=tuple(min(255, int(v*1.15)) for v in col), outline=DARK)
        d.polygon([(cx - s*0.9, cy - s*0.5), (cx, cy), (cx, cy + s), (cx - s*0.9, cy + s*0.5)], fill=col, outline=DARK)
        d.polygon([(cx + s*0.9, cy - s*0.5), (cx, cy), (cx, cy + s), (cx + s*0.9, cy + s*0.5)], fill=tuple(int(v*0.75) for v in col), outline=DARK)
        option_tiles(im, [shape_img(s, 32, rev and i == k) for i, s in enumerate(shapes)], 470, hl=k if rev else None, box=205)
        if rev: explain(im, "the others overlap when you fold them!", y=CH - 110, col=RED, size=34)
        return im
    return dict(q=card(False), a=card(True), options=[f"Net {c}" for c in "ABCD"], correct=k,
                question="WHICH ONE FOLDS INTO A CUBE?", banner=f"NET {'ABCD'[k]}!", catch=False)

# =====================================================================
# 3. CODE LOCK
PH = {(1, 0): "One number is correct and well placed", (0, 1): "One number is correct but wrongly placed",
      (0, 2): "Two numbers are correct but wrongly placed", (0, 0): "Nothing is correct", (1, 1): "One well placed, one wrongly placed"}
def fb(g, c): p = sum(a == b for a, b in zip(g, c)); w = len(set(g) & set(c)) - p; return (p, w)
CODES = [p for p in itertools.permutations(range(10), 3)]
def code_lock(seed, level):
    r = random.Random(seed)
    for _ in range(5000):
        code = r.choice(CODES); clues = []; cand = CODES[:]
        for _t in range(400):
            if len(cand) == 1 or len(clues) >= 5: break
            g = r.choice(CODES); f = fb(g, code)
            if f not in PH or g in [c_[0] for c_ in clues]: continue
            nc = [c for c in cand if fb(g, c) == f]
            if len(nc) < len(cand): clues.append((g, f)); cand = nc
        if len(cand) == 1 and len(clues) == (4 if level >= 2 else 3): break
    near = sorted(CODES, key=lambda c: -sum(fb(g, c) == f for g, f in clues))
    wrong = [c for c in near if c != code][:12]; r.shuffle(wrong)
    fmt = lambda c: "".join(map(str, c))
    def card(rev):
        im = blank(); d = ImageDraw.Draw(im); n = len(clues); rowh = 150 if n == 4 else 175
        y0 = (CH - (n*rowh + (110 if rev else 0)))/2 + rowh/2
        for k, (g, f) in enumerate(clues):
            y = y0 + k*rowh
            for i, v in enumerate(g):
                x = 60 + i*92; d.rounded_rectangle((x, y - 40, x + 80, y + 40), 14, fill=(255, 255, 255), outline=DARK, width=5)
                d.text((x + 40, y + 3), str(v), font=font(52), fill=DARK, anchor="mm")
            txt = PH[f]; f_ = font(34)
            lines = wrap(d, txt, f_, CW - 380)
            for li, ln in enumerate(lines): d.text((350, y - 20*(len(lines) - 1) + 40*li), ln, font=f_, fill=(70, 70, 90), anchor="lm")
        if rev:
            y = y0 + n*rowh - 20
            for i, v in enumerate(code):
                x = CW/2 - 140 + i*100; d.rounded_rectangle((x, y - 46, x + 86, y + 46), 16, fill=GREEN, outline=DARK, width=5)
                d.text((x + 43, y + 4), str(v), font=font(60), fill="white", anchor="mm")
        return im
    opts = [fmt(c) for c in wrong[:3]] + [fmt(code)]; r.shuffle(opts)
    return dict(q=card(False), a=card(True), options=opts, correct=opts.index(fmt(code)), question="CRACK THE 3-DIGIT CODE!",
                banner=f"CODE: {fmt(code)}", catch=False)

# =====================================================================
# 4. PAPER FOLD + PUNCH
def grid_img(holes, n=4, cell=40, paper=(255, 248, 225), hole_col=DARK, part=None, hl=False):
    W_ = n*cell if not part else part[0]*cell; H_ = n*cell if not part else part[1]*cell
    im = Image.new("RGBA", (W_ + 8, H_ + 8), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle((4, 4, 4 + W_, 4 + H_), fill=paper, outline=GREEN if hl else DARK, width=6 if hl else 4)
    for (c, r_) in holes:
        x, y = 4 + (c + 0.5)*cell, 4 + (r_ + 0.5)*cell; rr = cell*0.28
        d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=hole_col)
    return im

def paper_fold(seed, level):
    r = random.Random(seed); n = 4; two = level >= 2
    c, rr = r.choice([2, 3]), (r.choice([2, 3]) if two else r.randrange(4))
    holes = {(c, rr), (3 - c, rr)}
    if two: holes |= {(c, 3 - rr), (3 - c, 3 - rr)}
    wrongs = []
    wrongs.append({(c, rr)} if not two else {(c, rr), (3 - c, rr)})
    wrongs.append({(c, rr), (c, 3 - rr)} if not two else {(c, rr), (c, 3 - rr)})
    sh = {(min(3, max(0, x + (1 if x < 2 else -1))), y) for x, y in holes}
    wrongs.append(sh if sh != holes else {(x, (y + 1) % 4) for x, y in holes})
    wrongs = [w for w in wrongs if w != holes][:3]
    while len(wrongs) < 3: wrongs.append({(r.randrange(4), r.randrange(4)) for _ in range(len(holes))})
    opts = wrongs + [holes]; r.shuffle(opts); k = opts.index(holes)
    def arrow(d, x0, y0, x1, y1):
        d.line((x0, y0, x1, y1), fill=PURPLE, width=10); a = math.atan2(y1 - y0, x1 - x0)
        d.polygon([(x1 + 18*math.cos(a), y1 + 18*math.sin(a)), (x1 + 16*math.cos(a + 2.2), y1 + 16*math.sin(a + 2.2)), (x1 + 16*math.cos(a - 2.2), y1 + 16*math.sin(a - 2.2))], fill=PURPLE)
    def card(rev):
        im = blank(); d = ImageDraw.Draw(im); cell = 38; y = 175
        steps = [grid_img(set(), cell=cell)]
        steps.append(grid_img(set(), cell=cell, part=(2, 4)))
        if two: steps.append(grid_img(set(), cell=cell, part=(2, 2)))
        punched = grid_img({(c - 2, rr if not two else rr - 2)}, cell=cell, part=(2, 2 if two else 4))
        steps[-1] = punched
        xs = [130, 400, 640] if two else [190, 520]
        for i, st in enumerate(steps):
            paste_c(im, st, xs[i], y)
            if i < len(steps) - 1: arrow(d, xs[i] + st.width/2 + 18, y, xs[i + 1] - steps[i + 1].width/2 - 30, y)
        dl = ImageDraw.Draw(im)
        # fold lines on first sheet
        x0 = xs[0] - 2*cell; y0 = y - 2*cell
        for k_ in range(0, 4*cell, 14): dl.line((x0 + 2*cell, y0 + k_, x0 + 2*cell, y0 + k_ + 7), fill=RED, width=4)
        d.text((xs[0], y + 2*cell + 34), "fold left → right" if False else "fold in half", font=font(28), fill=GREY, anchor="mm")
        if two: d.text((xs[1], y + 2*cell + 34), "fold again", font=font(28), fill=GREY, anchor="mm")
        d.text((xs[-1], y + (2 if two else 2)*cell + 34), "punch!", font=font(28), fill=RED, anchor="mm")
        if two:
            for k_ in range(0, 2*cell, 14): dl.line((xs[1] - cell + k_, y, xs[1] - cell + k_ + 7, y), fill=RED, width=4)
        d.text((CW/2, 385), "unfold it... what do you see?", font=font(34), fill=DARK, anchor="mm")
        option_tiles(im, [grid_img(o, cell=36, hl=rev and i == k) for i, o in enumerate(opts)], 560, hl=k if rev else None, box=190)
        return im
    return dict(q=card(False), a=card(True), options=[f"Paper {ch}" for ch in "ABCD"], correct=k,
                question="WHAT DOES IT LOOK LIKE UNFOLDED?", banner=f"PAPER {'ABCD'[k]}!", catch=False)

# =====================================================================
# 5. COUNT THE CUBES (hidden ones count!)
def cube_count(seed, level):
    r = random.Random(seed); nx, ny = (2, 3) if level <= 1 else (3, 3); hmax = 3 if level <= 1 else 4
    while True:
        h = [[0]*ny for _ in range(nx)]
        for x in range(nx):
            for y in range(ny):
                lim = min([hmax] + ([h[x - 1][y]] if x else []) + ([h[x][y - 1]] if y else []))
                h[x][y] = r.randint(max(1, lim - 2), lim)
        tot = sum(map(sum, h)); vis = sum(1 for x in range(nx) for y in range(ny) if True)
        if tot >= nx*ny + 4: break
    col = r.choice([(255, 170, 60), (90, 170, 240), (240, 110, 130), (120, 200, 120)])
    def card(rev):
        im = blank(); d = ImageDraw.Draw(im); s = 78 if level <= 1 else 66; a_ = s*0.866; b_ = s*0.5
        ox = CW/2 + (nx - ny)*a_/2*-1 + (ny - nx)*0; oy = 250 + (hmax - 1)*s*0.35
        def P(x, y, z): return (ox + (y - x)*a_, oy + (x + y)*b_ - z*s)
        cubes = sorted([(x, y, z) for x in range(nx) for y in range(ny) for z in range(h[x][y])], key=lambda c: (c[0] + c[1], c[2]))
        for (x, y, z) in cubes:
            top = [P(x, y, z + 1), P(x, y + 1, z + 1), P(x + 1, y + 1, z + 1), P(x + 1, y, z + 1)]
            left = [P(x + 1, y, z), P(x + 1, y + 1, z), P(x + 1, y + 1, z + 1), P(x + 1, y, z + 1)]
            right = [P(x, y + 1, z), P(x + 1, y + 1, z), P(x + 1, y + 1, z + 1), P(x, y + 1, z + 1)]
            for poly, f in ((top, 1.18), (left, 0.95), (right, 0.75)):
                d.polygon(poly, fill=tuple(min(255, int(v*f)) for v in col), outline=DARK, width=3)
        if rev:
            # height map from above
            cs = 54; gx = CW - 60 - ny*cs; gy = 60
            d.text((gx + ny*cs/2, gy - 22), "from above", font=font(26), fill=GREY, anchor="mm")
            for x in range(nx):
                for y in range(ny):
                    d.rectangle((gx + y*cs, gy + x*cs, gx + (y + 1)*cs, gy + (x + 1)*cs), fill=(255, 245, 205), outline=DARK, width=3)
                    d.text((gx + (y + 0.5)*cs, gy + (x + 0.5)*cs + 2), str(h[x][y]), font=font(30), fill=DARK, anchor="mm")
            explain(im, " + ".join(str(h[x][y]) for x in range(nx) for y in range(ny)) + f" = {tot}", y=CH - 110, col=GREEN, size=40)
        else:
            d.text((CW/2, CH - 110), "count the hidden ones too!", font=font(36), fill=GREY, anchor="mm")
        return im
    visible_guess = sum(1 for x in range(nx) for y in range(ny))  # tops only
    opts, k = shuffle_opts(r, tot, [visible_guess + nx + ny - 1, tot - 2, tot - 1, tot + 2])
    return dict(q=card(False), a=card(True), options=[str(o) for o in opts], correct=k, question="HOW MANY CUBES?",
                banner=f"{tot} CUBES!", catch=True)

# =====================================================================
# 6. WHICH KEY FITS
TW_ = 46
def blade(d, teeth, x0, y0, S, fill, outline=None):
    n = len(teeth); tw = TW_*S
    poly = [(x0, y0), (x0 + n*tw + 14*S, y0), (x0 + n*tw + 14*S, y0 + 28*S)]
    for i in range(n - 1, -1, -1):
        dep = 12*S + teeth[i]*17*S
        poly += [(x0 + (i + 1)*tw, y0 + 28*S), (x0 + (i + 0.78)*tw, y0 + 28*S + dep), (x0 + (i + 0.22)*tw, y0 + 28*S + dep), (x0 + i*tw, y0 + 28*S)]
    d.polygon(poly, fill=fill)
    if outline: d.line(poly + [poly[0]], fill=outline, width=4*S)

def key_img(teeth, col=(250, 200, 70)):
    S = 2; n = len(teeth); w = 120 + n*TW_ + 30; h = 152
    im = Image.new("RGBA", (w*S, h*S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    blade(d, teeth, 104*S, 34*S, S, col, DARK)
    d.ellipse((4*S, 14*S, 112*S, 122*S), fill=col, outline=DARK, width=5*S); d.ellipse((34*S, 50*S, 66*S, 82*S), fill=(255, 255, 255), outline=DARK, width=4*S)
    return im.resize((w, h), Image.LANCZOS)

def lock_img(teeth):
    S = 2; n = len(teeth); w = 120 + n*TW_ + 30; h = 156
    im = Image.new("RGBA", (w*S, h*S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w*S - 1, h*S - 1), 26*S, fill=(120, 130, 160), outline=DARK, width=5*S)
    blade(d, teeth, 104*S, 34*S, S, (35, 35, 55))
    d.text((52*S, 75*S), "🔒" if False else "LOCK", font=font(24*S), fill=(230, 232, 245), anchor="mm")
    return im.resize((w, h), Image.LANCZOS)

def key_fit(seed, level):
    r = random.Random(seed); n = [4, 5, 6][level]
    teeth = [r.randint(0, 4) for _ in range(n)]
    keys = [teeth]
    while len(keys) < 4:
        k_ = teeth[:]
        for _ in range(1 if level >= 1 else 2):
            i = r.randrange(n); k_[i] = r.choice([v for v in range(5) if v != k_[i]])
        if level >= 2 and r.random() < 0.4: k_ = teeth[::-1] if teeth[::-1] != teeth else k_
        if k_ not in keys: keys.append(k_)
    r.shuffle(keys); k = keys.index(teeth)
    def card(rev):
        im = blank(); d = ImageDraw.Draw(im)
        SC = 1.15
        li = lock_img(teeth); li = li.resize((int(li.width*SC), int(li.height*SC)), Image.LANCZOS); lx = CW/2 - li.width/2 + 30; im.alpha_composite(li, (int(lx), 18))
        for i, t in enumerate(keys):
            y = 200 + i*146
            ki = key_img(t, (120, 220, 140) if (rev and i == k) else (250, 200, 70)); ki = ki.resize((int(ki.width*SC), int(ki.height*SC)), Image.LANCZOS)
            if rev and i == k: d.rounded_rectangle((lx - 90, y - 8, lx + ki.width + 16, y + ki.height + 2), 24, outline=GREEN, width=8)
            im.alpha_composite(ki, (int(lx), int(y)))
            d.ellipse((lx - 80, y + 50, lx - 20, y + 110), fill=GREEN if (rev and i == k) else BADGE[i])
            d.text((lx - 50, y + 80), "ABCD"[i], font=font(34), fill="white", anchor="mm")
        return im
    return dict(q=card(False), a=card(True), options=[f"Key {c}" for c in "ABCD"], correct=k, question="WHICH KEY OPENS THE LOCK?",
                banner=f"KEY {'ABCD'[k]}!", catch=False)

# =====================================================================
# 7. NUMBER PYRAMID (block = sum of the two below)
def pyramid(seed, level):
    r = random.Random(seed); rows = 3 if level == 0 else 4
    base = [r.randint(1, 9 if level < 2 else 12) for _ in range(rows)]
    P = [base]
    while len(P[-1]) > 1: P.append([P[-1][i] + P[-1][i + 1] for i in range(len(P[-1]) - 1)])
    if level == 0: ask = (rows - 1, 0)
    elif level == 1: ask = (2, r.randrange(2))
    else: ask = (0, r.choice([0, rows - 1]))
    ans = P[ask[0]][ask[1]]
    def card(rev):
        im = blank(); d = ImageDraw.Draw(im); bw, bh = 170, 110; ybase = 560 if rows == 4 else 520
        for lv, row in enumerate(P):
            n = len(row); y = ybase - lv*bh
            for i, v in enumerate(row):
                x = CW/2 + (i - (n - 1)/2)*bw
                asked = (lv, i) == ask
                fill = (GREEN if rev else (255, 255, 255)) if asked else [(255, 236, 179), (210, 235, 255), (220, 245, 210), (255, 214, 226)][lv]
                d.rounded_rectangle((x - bw/2 + 4, y - bh/2 + 4, x + bw/2 - 4, y + bh/2 - 4), 16, fill=fill, outline=DARK, width=5)
                t = str(v) if (rev or not asked) else "?"
                d.text((x, y + 3), t, font=font(54), fill=("white" if asked and rev else (RED if asked else DARK)), anchor="mm")
        if rev and level >= 2:
            lv, i = ask; above = P[1][0 if i == 0 else len(P[1]) - 1]; nb = P[0][1 if i == 0 else rows - 2]
            explain(im, f"{above} − {nb} = {ans}", y=CH - 115, col=PURPLE, size=48)
        else:
            d.text((CW/2, CH - 115), "each block = the two below added", font=font(36), fill=GREY if not rev else PURPLE, anchor="mm")
        return im
    opts, k = shuffle_opts(r, ans, num_wrong(r, ans, (1, 2, 3, 5)))
    return dict(q=card(False), a=card(True), options=[str(o) for o in opts], correct=k, question="WHAT'S THE MISSING NUMBER?",
                banner=f"IT'S {ans}!", catch=False)

# =====================================================================
# 8. COINS
COIN = {1: ((200, 120, 70), 74), 2: ((200, 120, 70), 82), 5: ((200, 120, 70), 92), 10: ((235, 190, 60), 86), 20: ((235, 190, 60), 96), 50: ((235, 190, 60), 106)}
def coin_img(v):
    col, rr = COIN[v]; S = 3; s = rr*2*S + 12; im = Image.new("RGBA", (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse((6, 6, s - 6, s - 6), fill=tuple(int(c*0.8) for c in col), outline=DARK, width=4*S)
    d.ellipse((6 + 9*S, 6 + 9*S, s - 6 - 9*S, s - 6 - 9*S), fill=col)
    d.text((s/2, s/2 + 2*S), f"{v}", font=font(int(rr*0.9*S)), fill=(255, 255, 255), anchor="mm", stroke_width=2*S, stroke_fill=tuple(int(c*0.6) for c in col))
    return im.resize((s//S, s//S), Image.LANCZOS)
def coins(seed, level):
    r = random.Random(seed); n = [4, 6, 8][level]; pool = [[1, 2, 5, 10], [1, 2, 5, 10, 20], [2, 5, 10, 20, 50]][level]
    vals = [r.choice(pool) for _ in range(n)]; ans = sum(vals)
    def card(rev):
        im = blank(); d = ImageDraw.Draw(im); rr_ = random.Random(seed + 5); pts = []
        for v in vals:
            for _ in range(500):
                x, y = rr_.uniform(130, CW - 130), rr_.uniform(130, 570)
                if all(math.hypot(x - a, y - b) > 215 for a, b in pts): break
            pts.append((x, y)); paste_c(im, coin_img(v).rotate(rr_.uniform(-25, 25), expand=True, resample=Image.BICUBIC), x, y)
        if rev: explain(im, " + ".join(map(str, sorted(vals, reverse=True))) + f" = {ans}¢", y=CH - 110, col=GREEN, size=40)
        else: d.text((CW/2, CH - 110), "add up all the coins", font=font(36), fill=GREY, anchor="mm")
        return im
    opts, k = shuffle_opts(r, ans, num_wrong(r, ans, (1, 2, 5, 10)))
    return dict(q=card(False), a=card(True), options=[f"{o}¢" for o in opts], correct=k, question="HOW MUCH MONEY?",
                banner=f"{ans}¢!", catch=False)

# =====================================================================
# 9. COUNT THE LEGS
LEGS = {"🐔": 2, "🐶": 4, "🕷️": 8, "🐜": 6, "🐄": 4, "🦆": 2, "🐝": 6, "🐞": 6, "🐧": 2, "🦒": 4, "🐍": 0, "🐟": 0, "🐌": 0, "🐸": 4}
def legs(seed, level):
    r = random.Random(seed)
    if level == 0: kinds = r.sample(["🐔", "🐶", "🐄", "🦆", "🐧", "🦒"], 2); counts = [r.randint(1, 3) for _ in kinds]
    elif level == 1: kinds = r.sample(["🐔", "🐶", "🐜", "🐞", "🦆"], 2) + [r.choice(["🐍", "🐟", "🐌"])]; counts = [r.randint(1, 3) for _ in kinds]
    else: kinds = r.sample(["🕷️", "🐜", "🐝", "🐔", "🐶"], 2) + [r.choice(["🐍", "🐟"])] + [r.choice(["🦆", "🐸"])]; counts = [r.randint(1, 2) for _ in kinds]
    ans = sum(LEGS[e]*c for e, c in zip(kinds, counts)); catch = any(LEGS[e] == 0 for e in kinds)
    def card(rev):
        im = blank(); d = ImageDraw.Draw(im); n = len(kinds); rowh = 175 if n <= 3 else 140
        y0 = (CH - 120 - n*rowh)/2 + rowh/2 + 10
        for i, (e, c) in enumerate(zip(kinds, counts)):
            y = y0 + i*rowh
            for j in range(c): paste_c(im, em(e, 128 if n <= 3 else 108), 130 + j*150, y)
            if rev:
                t = f"{c} × {LEGS[e]} = {c*LEGS[e]}"
                d.text((CW - 70, y), t, font=font(44), fill=RED if LEGS[e] == 0 else PURPLE, anchor="rm")
        if rev: explain(im, f"total = {ans} legs", y=CH - 110, col=GREEN, size=50)
        else: d.text((CW/2, CH - 110), "count EVERY leg", font=font(36), fill=GREY, anchor="mm")
        return im
    opts, k = shuffle_opts(r, ans, num_wrong(r, ans, (2, 4, 6)))
    return dict(q=card(False), a=card(True), options=[str(o) for o in opts], correct=k, question="HOW MANY LEGS IN TOTAL?",
                banner=f"{ans} LEGS!", catch=catch)

# =====================================================================
# 10. COLOR MIXING
MIX = [(("Red", (230, 50, 50)), ("Blue", (50, 90, 230)), ("Purple", (140, 60, 190))),
       (("Red", (230, 50, 50)), ("Yellow", (250, 210, 40)), ("Orange", (250, 140, 30))),
       (("Blue", (50, 90, 230)), ("Yellow", (250, 210, 40)), ("Green", (60, 170, 70))),
       (("Red", (230, 50, 50)), ("White", (255, 255, 255)), ("Pink", (255, 160, 190))),
       (("Black", (30, 30, 35)), ("White", (255, 255, 255)), ("Grey", (150, 150, 155)))]
def blob(col, s=230):
    S = 2; im = Image.new("RGBA", (s*S, s*S), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = s*S/2; rr = random.Random(sum(col))
    pts = []
    for k in range(14):
        a = k*2*math.pi/14; R = c*0.8*(0.85 + 0.15*rr.random()); pts.append((c + R*math.cos(a), c + R*math.sin(a)))
    d.polygon(pts, fill=col, outline=DARK); d.line(pts + [pts[0]], fill=DARK, width=5*S, joint="curve")
    d.ellipse((c - c*0.45, c - c*0.5, c - c*0.2, c - c*0.25), fill=(255, 255, 255, 120))
    return im.resize((s, s), Image.LANCZOS)
def color_mix(seed, level):
    r = random.Random(seed); (n1, c1), (n2, c2), (n3, c3) = r.choice(MIX)
    allc = ["Purple", "Orange", "Green", "Pink", "Grey", "Brown", "Blue", "Red", "Yellow"]
    def card(rev):
        im = blank(); d = ImageDraw.Draw(im); y = 330
        paste_c(im, blob(c1, 220), 160, y); d.text((300, y), "+", font=font(110), fill=DARK, anchor="mm")
        paste_c(im, blob(c2, 220), 440, y); d.text((590, y), "=", font=font(110), fill=DARK, anchor="mm")
        if rev: paste_c(im, blob(c3, 240), 780, y)
        else: d.text((780, y), "?", font=font(200), fill=RED, anchor="mm")
        d.text((160, y + 150), n1, font=font(40), fill=DARK, anchor="mm"); d.text((440, y + 150), n2, font=font(40), fill=DARK, anchor="mm")
        if rev: d.text((780, y + 160), n3, font=font(44), fill=GREEN, anchor="mm")
        d.text((CW/2, CH - 140), "mix the paint!", font=font(36), fill=GREY, anchor="mm")
        return im
    opts, k = shuffle_opts(r, n3, r.sample([c for c in allc if c not in (n1, n2, n3)], 3))
    return dict(q=card(False), a=card(True), options=opts, correct=k, question="WHAT COLOR DO YOU GET?", banner=f"{n3.upper()}!", catch=False)

# =====================================================================
# 11. CALENDAR
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
def calendar(seed, level):
    r = random.Random(seed); today = r.randrange(7)
    if level == 0:
        n = r.choice([2, 3, 4]); ans = (today + n) % 7; q1 = f"Today is {DAYS[today]}."; q2 = f"What day is it in {n} days?"
        exp = f"{DAYS[today]} + {n} days"
    elif level == 1:
        n = r.choice([9, 10, 12, 15]); ans = (today + n) % 7; q1 = f"Today is {DAYS[today]}."; q2 = f"What day will it be in {n} days?"
        exp = f"{n} days = 1 week + {n - 7} days" if n < 14 else f"{n} days = 2 weeks + {n - 14} day{'s' if n - 14 != 1 else ''}"
    else:
        dat = r.randrange(7); ans = (dat - 3) % 7
        q1 = f"The day after tomorrow is {DAYS[dat]}."; q2 = "What day was yesterday?"; exp = f"today = {DAYS[(dat - 2) % 7]}, so yesterday = {DAYS[ans]}"
    def card(rev):
        im = blank(); d = ImageDraw.Draw(im)
        d.rounded_rectangle((CW/2 - 150, 40, CW/2 + 150, 250), 30, fill="white", outline=DARK, width=6)
        d.rounded_rectangle((CW/2 - 150, 40, CW/2 + 150, 105), 30, fill=RED); d.rectangle((CW/2 - 147, 80, CW/2 + 147, 105), fill=RED)
        for k_ in (-80, 80): d.rounded_rectangle((CW/2 + k_ - 10, 20, CW/2 + k_ + 10, 70), 8, fill=DARK)
        d.text((CW/2, 180), "?" if not rev else DAYS[ans][:3].upper(), font=font(90), fill=DARK if not rev else GREEN, anchor="mm")
        text_block(im, q1, 340, 50); text_block(im, q2, 440, 50, col=PURPLE)
        for i, dn in enumerate(DAYS):
            x = 75 + i*135; y = 580
            hl = rev and i == ans
            d.rounded_rectangle((x - 58, y - 40, x + 58, y + 40), 18, fill=GREEN if hl else SOFT, outline=DARK if hl else (210, 212, 225), width=4)
            d.text((x, y + 2), dn[:3], font=font(34), fill="white" if hl else DARK, anchor="mm")
        if rev: explain(im, exp, y=CH - 110, col=PURPLE, size=36)
        return im
    opts, k = shuffle_opts(r, DAYS[ans], [DAYS[(ans + d_) % 7] for d_ in (1, -1, 2, 3)])
    return dict(q=card(False), a=card(True), options=opts, correct=k, question="WHAT DAY IS IT?", banner=f"{DAYS[ans].upper()}!", catch=False)

# =====================================================================
# 12. WHAT COMES NEXT (visual pattern)
PCOL = [(231, 76, 60), (52, 152, 219), (243, 156, 18), (46, 204, 113), (155, 89, 182)]
def glyph(ang, dots, col, size=150, hl=False):
    S = 2; s = size*S; im = Image.new("RGBA", (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = s/2
    d.rounded_rectangle((4, 4, s - 4, s - 4), 22*S, fill=(255, 255, 255), outline=GREEN if hl else DARK, width=(8 if hl else 4)*S)
    R = s*0.32; a0 = ang - 35; a1 = ang + 35
    d.pieslice((c - R, c - R, c + R, c + R), a1 - 360 + 360, a0 + 360, fill=col)  # pac-man mouth facing 'ang'
    for k in range(dots):
        a = math.radians(ang + 180 + (k - (dots - 1)/2)*28); x, y = c + R*1.32*math.cos(a), c + R*1.32*math.sin(a)
        d.ellipse((x - 7*S, y - 7*S, x + 7*S, y + 7*S), fill=DARK)
    return im.resize((size, size), Image.LANCZOS)
def pattern_next(seed, level):
    r = random.Random(seed)
    st = r.choice([0, 90, 180, 270]); cols = r.sample(PCOL, 2)
    if level == 0: dang, ddot, alt, d0 = 90, 0, False, 1
    elif level == 1: dang, ddot, alt, d0 = 45, 1, False, 1
    else: dang, ddot, alt, d0 = -135, 1, True, 1
    seq = [((st + i*dang) % 360, min(5, d0 + i*ddot), cols[i % 2] if alt else cols[0]) for i in range(5)]
    ans = seq[4]
    cands = [ans, ((ans[0] + 90) % 360, ans[1], ans[2]), (ans[0], max(0, ans[1] - 1) if ddot else ans[1] + 1, ans[2]),
             ((ans[0] + 180) % 360, ans[1], ans[2]), (ans[0], ans[1], cols[1] if ans[2] == cols[0] else cols[0]), ((ans[0] - 45) % 360, ans[1], ans[2])]
    uniq = []
    for c in cands:
        if c not in uniq: uniq.append(c)
    opts = [uniq[0]] + r.sample(uniq[1:], 3); r.shuffle(opts); k = opts.index(ans)
    def card(rev):
        im = blank(); d = ImageDraw.Draw(im)
        for i in range(5):
            x = 100 + i*190; y = 190
            if i < 4: paste_c(im, glyph(seq[i][0], seq[i][1], seq[i][2], 160), x, y)
            else:
                if rev: paste_c(im, glyph(*ans, 160, hl=True), x, y)
                else:
                    d.rounded_rectangle((x - 80, y - 80, x + 80, y + 80), 22, outline=RED, width=6); d.text((x, y + 4), "?", font=font(100), fill=RED, anchor="mm")
        d.text((CW/2, 340), "what comes next?", font=font(34), fill=GREY, anchor="mm")
        option_tiles(im, [glyph(*o, 170, hl=rev and i == k) for i, o in enumerate(opts)], 520, hl=k if rev else None, box=200)
        return im
    return dict(q=card(False), a=card(True), options=[f"Option {c}" for c in "ABCD"], correct=k, question="WHAT COMES NEXT?",
                banner=f"OPTION {'ABCD'[k]}!", catch=False)

# =====================================================================
# 13. TRICK RIDDLES (all are GOTCHAs)
RIDDLES = [
    [("How many months have 28 days?", "12", ["1", "2", "0"], "ALL of them have at least 28!"),
     ("You have 3 apples and take away 2. How many apples do YOU have?", "2", ["1", "3", "0"], "you TOOK 2, so you have 2"),
     ("What weighs more: 1 kg of feathers or 1 kg of iron?", "Same", ["Iron", "Feathers", "Can't tell"], "a kilo is a kilo!"),
     ("How many birthdays does the average person have?", "1", ["70", "80", "365"], "you're only BORN once!")],
    [("A farmer has 17 sheep. All but 9 run away. How many are left?", "9", ["8", "17", "0"], "ALL BUT 9 = 9 stay"),
     ("You pass the person in 2nd place. What place are you in now?", "2nd", ["1st", "3rd", "Last"], "you took THEIR place: 2nd"),
     ("How many times can you subtract 5 from 25?", "Once", ["5", "4", "20"], "after once, it's 20, not 25!"),
     ("A doctor gives you 3 pills, one every 30 minutes. How long until they're gone?", "1 hour", ["1.5 hours", "2 hours", "30 min"], "now, +30 min, +60 min"),
     ("Mia's mum has 4 kids: April, May, June and...?", "Mia", ["July", "March", "August"], "it's MIA'S mum!")],
    [("Divide 30 by a half, then add 10. What do you get?", "70", ["25", "40", "20"], "30 ÷ ½ = 60, + 10 = 70"),
     ("A bat and ball cost $1.10. The bat costs $1 more than the ball. How much is the ball?", "5¢", ["10¢", "1¢", "15¢"], "ball 5¢ + bat $1.05 = $1.10"),
     ("How many times does the digit 9 appear from 1 to 100?", "20", ["10", "11", "19"], "9,19...89 = 9, plus 90-99 = 11"),
     ("J, F, M, A, M, J, J, A, ... what comes next?", "S", ["O", "N", "J"], "months: Jan, Feb... SEPTEMBER")],
]
def riddle(seed, level):
    r = random.Random(seed); q, ans, wrong, why = r.choice(RIDDLES[min(level, 2)])
    def card(rev):
        im = blank(); d = ImageDraw.Draw(im)
        paste_c(im, em("🤔" if not rev else "😜", 120), CW/2, 110)
        text_block(im, q, 380, 64)
        if rev: explain(im, why, y=CH - 110, col=RED, size=42)
        else: d.text((CW/2, CH - 110), "read it carefully...", font=font(36), fill=GREY, anchor="mm")
        return im
    opts, k = shuffle_opts(r, ans, wrong)
    return dict(q=card(False), a=card(True), options=opts, correct=k, question="TRICK QUESTION!", banner=f"{ans.upper()}!", catch=True)

GENS = dict(matchstick=matchstick, cube_net=cube_net, code_lock=code_lock, paper_fold=paper_fold, cube_count=cube_count,
            key_fit=key_fit, pyramid=pyramid, coins=coins, legs=legs, color_mix=color_mix, calendar=calendar,
            pattern_next=pattern_next, riddle=riddle)
LEVEL_POOL = [
    ["color_mix", "legs", "coins", "pyramid", "riddle", "calendar", "pattern_next", "key_fit"],
    ["legs", "coins", "pyramid", "riddle", "calendar", "pattern_next", "key_fit", "paper_fold", "cube_count", "matchstick"],
    ["code_lock", "cube_net", "matchstick", "paper_fold", "cube_count", "pyramid", "riddle", "key_fit", "pattern_next", "calendar"],
]
NICE = dict(matchstick="Matchstick fix", cube_net="Cube net", code_lock="Code lock", paper_fold="Paper fold", cube_count="Count the cubes",
            key_fit="Which key", pyramid="Number pyramid", coins="Coin count", legs="Count the legs", color_mix="Color mixing",
            calendar="Calendar", pattern_next="What comes next", riddle="Trick question")
