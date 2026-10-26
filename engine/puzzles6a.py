"""Batch-6 genres, part A (spatial + number logic). Same dict contract as earlier puzzle modules."""
import math, random, itertools
from collections import deque
from PIL import Image, ImageDraw, ImageFont
from render import font, DARK
from v3 import CARD, blank, emoji, GREEN
from puzzles4 import shuffle_opts, num_wrong, explain, em, paste_c, BADGE, RED, BLUE, ORANGE, PURPLE, GREY, SOFT, CW, CH
from puzzles5 import text_block, option_tiles

DJ = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
def djf(sz): return ImageFont.truetype(DJ, sz)
YEL = (255, 205, 60); TEAL = (26, 188, 156)
def opts4(r, ans, wrong):
    o, k = shuffle_opts(r, ans, wrong); return [str(x) for x in o], k

# 1. MIRROR (reflection in water)
WORDS_M = ["PUZZLE", "GENIUS", "SMART", "NOGGIN", "QUIZ", "BRAIN", "TRICKY", "LOGIC"]
def mirror(seed, level):
    r = random.Random(seed); w = r.choice(WORDS_M)
    def word_img(sz):
        f = font(sz); d = ImageDraw.Draw(Image.new("L", (1, 1))); b = d.textbbox((0, 0), w, font=f)
        im = Image.new("RGBA", (b[2] - b[0] + 10, b[3] - b[1] + 10), (0, 0, 0, 0)); ImageDraw.Draw(im).text((5 - b[0], 5 - b[1]), w, font=f, fill=(40, 70, 160)); return im
    base = word_img(120)
    variants = [base.transpose(Image.FLIP_TOP_BOTTOM), base.transpose(Image.FLIP_LEFT_RIGHT), base.rotate(180), base]
    order = list(range(4)); r.shuffle(order); k = order.index(0)
    def fit(im, box=180):
        s = min(box/im.width, box/im.height); return im.resize((max(1, int(im.width*s)), max(1, int(im.height*s))), Image.LANCZOS)
    def card(rev):
        im = blank(); d = ImageDraw.Draw(im)
        d.rectangle((60, 250, CW - 60, 330), fill=(170, 215, 255)); d.rectangle((60, 245, CW - 60, 252), fill=(90, 150, 220))
        paste_c(im, base, CW/2, 170)
        for x in range(80, CW - 80, 60): d.arc((x, 262, x + 50, 282), 200, 340, fill=(255, 255, 255), width=4)
        d.text((CW/2, 360), "what does the water show?", font=font(34), fill=GREY, anchor="mm")
        option_tiles(im, [fit(variants[o]) for o in order], 560, hl=k if rev else None, box=200)
        if rev: explain(im, "a water reflection flips it UPSIDE DOWN", y=CH - 30, col=PURPLE, size=32)
        return im
    return dict(q=card(False), a=card(True), options=[f"Option {c}" for c in "ABCD"], correct=k, question="WHAT'S THE REFLECTION?",
                banner=f"OPTION {'ABCD'[k]}!", catch=False)

# 2. TETRIS FIT
TET = {"I": [(0, 0), (1, 0), (2, 0), (3, 0)], "O": [(0, 0), (1, 0), (0, 1), (1, 1)], "T": [(0, 0), (1, 0), (2, 0), (1, 1)],
       "S": [(1, 0), (2, 0), (0, 1), (1, 1)], "Z": [(0, 0), (1, 0), (1, 1), (2, 1)], "L": [(0, 0), (0, 1), (0, 2), (1, 2)], "J": [(1, 0), (1, 1), (1, 2), (0, 2)]}
TCOL = {"I": (60, 200, 230), "O": (250, 210, 60), "T": (170, 90, 210), "S": (90, 200, 90), "Z": (230, 70, 70), "L": (245, 150, 50), "J": (70, 110, 230)}
def nrm(c):
    mx = min(x for x, y in c); my = min(y for x, y in c); return frozenset((x - mx, y - my) for x, y in c)
def rots(c):
    out = [nrm(c)]
    for _ in range(3): out.append(nrm({(y, -x) for x, y in out[-1]}))
    return out
def tetris(seed, level):
    r = random.Random(seed); Wd, Hd = 10, 6
    while True:
        t = r.choice(list(TET)); shape = r.choice(rots(TET[t])); w = max(x for x, y in shape) + 1; h = max(y for x, y in shape) + 1
        ox = r.randint(0, Wd - w); oy = 3  # carve into rows 3..5 (filled area = rows 3..5)
        if oy + h > Hd: continue
        cells = {(ox + x, oy + y) for x, y in shape}
        # gap must be reachable from above: every filled-area cell above a carved cell is carved
        ok = all((x, yy) in cells for (x, y) in cells for yy in range(3, y))
        if ok: break
    filled = {(x, y) for x in range(Wd) for y in range(3, Hd)} - cells
    others = [k_ for k_ in TET if k_ != t]
    trap = {"L": "J", "J": "L", "S": "Z", "Z": "S"}.get(t)
    wrong = ([trap] if (trap and level >= 1) else []) + r.sample([o for o in others if o != trap], 3)
    pieces = wrong[:3] + [t]; r.shuffle(pieces); k = pieces.index(t)
    def piece_img(p, cell=34):
        sh = r.choice(rots(TET[p])) if False else rots(TET[p])[(seed + "IOTSZLJ".index(p)) % 4]
        w_ = max(x for x, y in sh) + 1; h_ = max(y for x, y in sh) + 1
        im = Image.new("RGBA", (w_*cell + 8, h_*cell + 8), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        for x, y in sh: d.rounded_rectangle((4 + x*cell, 4 + y*cell, 4 + (x + 1)*cell - 2, 4 + (y + 1)*cell - 2), 6, fill=TCOL[p], outline=DARK, width=3)
        return im
    def card(rev):
        im = blank(); d = ImageDraw.Draw(im); cs = 52; gx = (CW - Wd*cs)/2; gy = 20
        d.rectangle((gx - 6, gy + 2*cs, gx + Wd*cs + 6, gy + Hd*cs + 6), fill=(30, 32, 50))
        for (x, y) in filled: d.rounded_rectangle((gx + x*cs + 2, gy + y*cs + 2, gx + (x + 1)*cs - 2, gy + (y + 1)*cs - 2), 6, fill=(150, 155, 175))
        if rev:
            for (x, y) in cells: d.rounded_rectangle((gx + x*cs + 2, gy + y*cs + 2, gx + (x + 1)*cs - 2, gy + (y + 1)*cs - 2), 6, fill=TCOL[t], outline="white", width=3)
        d.text((CW/2, gy + 20 + cs), "which piece clears the lines?", font=font(32), fill=GREY, anchor="mm")
        option_tiles(im, [piece_img(p) for p in pieces], 540, hl=k if rev else None, box=190)
        if rev: explain(im, "you can rotate pieces, but not flip them!", y=CH - 30, col=PURPLE, size=30)
        return im
    return dict(q=card(False), a=card(True), options=[f"Piece {c}" for c in "ABCD"], correct=k, question="WHICH PIECE FITS THE GAP?",
                banner=f"PIECE {'ABCD'[k]}!", catch=False)

# 3. KNIGHT MOVES
def knight(seed, level):
    r = random.Random(seed); n = [5, 6, 6][level]
    def bfs(s):
        dist = {s: 0}; prev = {s: None}; dq = deque([s])
        while dq:
            c = dq.popleft()
            for dx, dy in ((1, 2), (2, 1), (-1, 2), (-2, 1), (1, -2), (2, -1), (-1, -2), (-2, -1)):
                m = (c[0] + dx, c[1] + dy)
                if 0 <= m[0] < n and 0 <= m[1] < n and m not in dist: dist[m] = dist[c] + 1; prev[m] = c; dq.append(m)
        return dist, prev
    want = [2, 3, 4][level]
    while True:
        s = (r.randrange(n), r.randrange(n)); dist, prev = bfs(s); cand = [c for c, v in dist.items() if v == want]
        if cand: t = r.choice(cand); break
    path = [t]
    while prev[path[-1]] is not None: path.append(prev[path[-1]])
    path = path[::-1]
    def card(rev):
        im = blank(); d = ImageDraw.Draw(im); cs = min(100, 640//n); gx = (CW - n*cs)/2; gy = 50
        for y in range(n):
            for x in range(n):
                d.rectangle((gx + x*cs, gy + y*cs, gx + (x + 1)*cs, gy + (y + 1)*cs), fill=(240, 217, 181) if (x + y) % 2 == 0 else (181, 136, 99))
        if rev:
            for i, c in enumerate(path[1:], 1):
                cx, cy = gx + (c[0] + 0.5)*cs, gy + (c[1] + 0.5)*cs
                d.ellipse((cx - cs*0.32, cy - cs*0.32, cx + cs*0.32, cy + cs*0.32), fill=GREEN, outline="white", width=3)
                d.text((cx, cy + 2), str(i), font=font(int(cs*0.36)), fill="white", anchor="mm")
            pts = [(gx + (c[0] + 0.5)*cs, gy + (c[1] + 0.5)*cs) for c in path]; d.line(pts, fill=(46, 160, 90), width=5)
        sx, sy = gx + (s[0] + 0.5)*cs, gy + (s[1] + 0.5)*cs
        d.text((sx, sy + 3), "♞", font=djf(int(cs*0.8)), fill=(20, 20, 30), anchor="mm")
        tx, ty = gx + (t[0] + 0.5)*cs, gy + (t[1] + 0.5)*cs
        if not rev: paste_c(im, em("⭐", int(cs*0.7)), tx, ty)
        d.text((CW/2, gy + n*cs + 50), "knights move in an L-shape", font=font(34), fill=GREY if not rev else PURPLE, anchor="mm")
        return im
    o, k = opts4(r, want, [want + 1, want - 1, want + 2, 1])
    return dict(q=card(False), a=card(True), options=o, correct=k, question="FEWEST KNIGHT MOVES TO THE STAR?", banner=f"{want} MOVES!", catch=False)

# 4. TIC-TAC-TOE
LINES = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]
def winner(b): return next((b[a] for a, c, e in LINES if b[a] != " " and b[a] == b[c] == b[e]), None)
def tictactoe(seed, level):
    r = random.Random(seed)
    while True:
        b = [" "]*9; cells = list(range(9)); r.shuffle(cells); nx = r.choice([3, 3, 4])
        for i in range(nx): b[cells[i]] = "X"
        for i in range(nx, nx + nx - (1 if level >= 2 else 0)): b[cells[i]] = "O"
        if winner(b): continue
        mover = "O" if level >= 2 else "X"
        if b.count("X") - b.count("O") != (1 if mover == "O" else 0): continue
        empt = [i for i in range(9) if b[i] == " "]
        def wins(p): return [i for i in empt if winner(b[:i] + [p] + b[i + 1:]) == p]
        if mover == "X":
            w = wins("X")
            if len(w) == 1: ans = w[0]; break
        else:
            if wins("O"): continue
            th = wins("X")
            if len(th) == 1: ans = th[0]; break
    q = "WHERE MUST O PLAY TO NOT LOSE?" if level >= 2 else "WHERE DOES X PLAY TO WIN?"
    def card(rev):
        im = blank(); d = ImageDraw.Draw(im); cs = 190; gx = (CW - 3*cs)/2; gy = 60
        for i in (1, 2):
            d.line((gx + i*cs, gy, gx + i*cs, gy + 3*cs), fill=DARK, width=10); d.line((gx, gy + i*cs, gx + 3*cs, gy + i*cs), fill=DARK, width=10)
        for i, v in enumerate(b):
            cx, cy = gx + (i % 3 + 0.5)*cs, gy + (i//3 + 0.5)*cs
            if v == "X":
                for s_ in (-1, 1): d.line((cx - 55, cy - 55*s_, cx + 55, cy + 55*s_), fill=(231, 76, 60), width=18)
            elif v == "O": d.ellipse((cx - 60, cy - 60, cx + 60, cy + 60), outline=(52, 152, 219), width=16)
            else:
                if rev and i == ans:
                    d.rounded_rectangle((cx - 85, cy - 85, cx + 85, cy + 85), 20, fill=(220, 250, 225))
                    if level >= 2: d.ellipse((cx - 60, cy - 60, cx + 60, cy + 60), outline=GREEN, width=16)
                    else:
                        for s_ in (-1, 1): d.line((cx - 55, cy - 55*s_, cx + 55, cy + 55*s_), fill=GREEN, width=18)
                d.text((cx, cy), str(i + 1), font=font(46), fill=(190, 190, 205) if not (rev and i == ans) else GREEN, anchor="mm")
        d.text((CW/2, CH - 70), ("X to move" if level < 2 else "O to move: block X!"), font=font(36), fill=GREY, anchor="mm")
        return im
    empt = [i for i in range(9) if b[i] == " "]
    wrong = [f"Square {i + 1}" for i in r.sample([e for e in empt if e != ans], min(3, len(empt) - 1))]
    while len(wrong) < 3: wrong.append(f"Square {r.choice([c for c in range(1, 10) if f'Square {c}' not in wrong and c != ans + 1])}")
    o, k = shuffle_opts(r, f"Square {ans + 1}", wrong)
    return dict(q=card(False), a=card(True), options=o, correct=k, question=q, banner=f"SQUARE {ans + 1}!", catch=False)

# 5. LASER + MIRRORS
def laser(seed, level):
    r = random.Random(seed); n = [4, 5, 5][level]; nm = [3, 5, 7][level]
    for _ in range(5000):
        M = {}
        for _m in range(nm): M[(r.randrange(n), r.randrange(n))] = r.choice("/\\")
        row = r.randrange(n); x, y, dx, dy = -1, row, 1, 0; path = [(x, y)]; hits = 0; steps = 0
        while True:
            x += dx; y += dy; steps += 1
            if not (0 <= x < n and 0 <= y < n): break
            path.append((x, y))
            if (x, y) in M:
                hits += 1
                if M[(x, y)] == "/": dx, dy = -dy, -dx
                else: dx, dy = dy, dx
        if hits >= [2, 3, 4][level] and not (y == row and x < 0): break
    exit_ = (x, y)
    edges = [(-1, j) for j in range(n) if j != row] + [(n, j) for j in range(n)] + [(i, -1) for i in range(n)] + [(i, n) for i in range(n)]
    edges = [e for e in edges if e != exit_]; tg = r.sample(edges, 3) + [exit_]; r.shuffle(tg); k = tg.index(exit_)
    def card(rev):
        im = blank(); d = ImageDraw.Draw(im); cs = 560//n; gx = (CW - n*cs)/2; gy = (CH - n*cs)/2
        d.rectangle((gx, gy, gx + n*cs, gy + n*cs), fill=(28, 30, 48))
        for i in range(n + 1):
            d.line((gx + i*cs, gy, gx + i*cs, gy + n*cs), fill=(60, 64, 90), width=2); d.line((gx, gy + i*cs, gx + n*cs, gy + i*cs), fill=(60, 64, 90), width=2)
        def C(c): return (gx + (c[0] + 0.5)*cs, gy + (c[1] + 0.5)*cs)
        if rev:
            pts = [C(p) for p in path] + [C(exit_)]
            d.line(pts, fill=(255, 60, 60), width=10); d.line(pts, fill=(255, 200, 200), width=3)
        else:
            pts = [C(path[0]), C((0, row))]; d.line(pts, fill=(255, 60, 60), width=10)
        for (mx, my), t_ in M.items():
            x0, y0 = gx + mx*cs + 10, gy + my*cs + 10; x1, y1 = gx + (mx + 1)*cs - 10, gy + (my + 1)*cs - 10
            if t_ == "/": d.line((x0, y1, x1, y0), fill=(200, 230, 255), width=10)
            else: d.line((x0, y0, x1, y1), fill=(200, 230, 255), width=10)
        sx, sy = C((-1, row)); d.rounded_rectangle((sx - 30, sy - 22, sx + 20, sy + 22), 8, fill=(80, 80, 100)); d.ellipse((sx + 10, sy - 8, sx + 26, sy + 8), fill=(255, 60, 60))
        for i, e in enumerate(tg):
            ex, ey = C(e); col = GREEN if (rev and i == k) else BADGE[i]
            d.ellipse((ex - 30, ey - 30, ex + 30, ey + 30), fill=col, outline="white", width=4); d.text((ex, ey + 2), "ABCD"[i], font=font(34), fill="white", anchor="mm")
        return im
    return dict(q=card(False), a=card(True), options=[f"Target {c}" for c in "ABCD"], correct=k, question="WHERE DOES THE LASER HIT?",
                banner=f"TARGET {'ABCD'[k]}!", catch=False)

# 6. CIRCUIT
def circuit(seed, level):
    r = random.Random(seed); nb = 4; nsw = [1, 2, 3][level]
    sw = [[r.random() < 0.55 for _ in range(nsw)] for _ in range(nb)]
    good = r.randrange(nb); sw[good] = [True]*nsw
    for i in range(nb):
        if i != good and all(sw[i]): sw[i][r.randrange(nsw)] = False
    def card(rev):
        im = blank(); d = ImageDraw.Draw(im); top, bot = 150, 640; xs = [200 + i*190 for i in range(nb)]
        d.line((90, top, xs[-1], top), fill=DARK, width=8); d.line((90, bot, xs[-1], bot), fill=DARK, width=8)
        d.line((90, top, 90, bot), fill=DARK, width=8)
        d.rectangle((60, 360, 120, 430), fill=(60, 60, 80)); d.rectangle((75, 345, 105, 360), fill=(60, 60, 80))
        d.text((90, 395), "+", font=font(40), fill="white", anchor="mm"); d.rectangle((70, 352, 110, 438), fill=None)
        for i, x in enumerate(xs):
            lit = all(sw[i]) and rev
            segs = nsw + 1; ys = [top + (bot - top - 130)*j/segs for j in range(segs + 1)]
            yb = bot - 80
            prev = top
            for j in range(nsw):
                y0 = top + 40 + j*((yb - 80 - top)/max(1, nsw)); y1 = y0 + 50
                d.line((x, prev, x, y0), fill=DARK, width=8)
                d.ellipse((x - 8, y0 - 8, x + 8, y0 + 8), fill=DARK); d.ellipse((x - 8, y1 - 8, x + 8, y1 + 8), fill=DARK)
                if sw[i][j]: d.line((x, y0, x, y1), fill=(46, 160, 90) if lit else DARK, width=8)
                else: d.line((x, y0, x + 38, y1 - 14), fill=(231, 76, 60), width=8)
                prev = y1
            d.line((x, prev, x, yb - 40), fill=DARK, width=8); d.line((x, yb + 40, x, bot), fill=DARK, width=8)
            if lit:
                gl = Image.new("RGBA", (220, 220), (0, 0, 0, 0)); ImageDraw.Draw(gl).ellipse((30, 30, 190, 190), fill=(255, 230, 80, 170))
                from PIL import ImageFilter; im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(20)), (int(x - 110), int(yb - 110)))
            d.ellipse((x - 40, yb - 40, x + 40, yb + 40), fill=(255, 230, 80) if lit else (235, 235, 240), outline=DARK, width=5)
            d.text((x, yb + 2), "ABCD"[i], font=font(36), fill=DARK, anchor="mm")
        d.text((CW/2, CH - 70), "a bulb lights only if ALL its switches are closed", font=font(30), fill=GREY, anchor="mm")
        return im
    return dict(q=card(False), a=card(True), options=[f"Bulb {c}" for c in "ABCD"], correct=good, question="WHICH BULB LIGHTS UP?",
                banner=f"BULB {'ABCD'[good]}!", catch=False)

# 7. ONE-LINE DRAWING (Euler path)
def one_line(seed, level):
    r = random.Random(seed)
    P = [(x, y) for y in range(3) for x in range(3)]
    cand_edges = [(a, b) for a in range(9) for b in range(a + 1, 9) if max(abs(P[a][0] - P[b][0]), abs(P[a][1] - P[b][1])) == 1]
    def gen(want_euler):
        for _ in range(5000):
            E = r.sample(cand_edges, r.randint(6, 9))
            # no crossing diagonals in same cell
            diag = {}
            bad = False
            for a, b in E:
                if P[a][0] != P[b][0] and P[a][1] != P[b][1]:
                    cell = (min(P[a][0], P[b][0]), min(P[a][1], P[b][1]))
                    if cell in diag: bad = True
                    diag[cell] = 1
            if bad: continue
            nodes = {a for e in E for a in e}; adj = {v: set() for v in nodes}
            for a, b in E: adj[a].add(b); adj[b].add(a)
            st = [next(iter(nodes))]; seen = set(st)
            while st:
                v = st.pop()
                for w in adj[v]:
                    if w not in seen: seen.add(w); st.append(w)
            if seen != nodes: continue
            odd = [v for v in nodes if len(adj[v]) % 2]
            if want_euler and len(odd) in (0, 2): return E, odd
            if not want_euler and len(odd) >= 4: return E, odd
    shapes = [gen(True)] + [gen(False) for _ in range(3)]
    order = list(range(4)); r.shuffle(order); k = order.index(0)
    def shape_img(E, odd, hl=False, cs=70):
        im = Image.new("RGBA", (2*cs + 40, 2*cs + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        for a, b in E: d.line((20 + P[a][0]*cs, 20 + P[a][1]*cs, 20 + P[b][0]*cs, 20 + P[b][1]*cs), fill=GREEN if hl is True else DARK, width=7)
        for v in {a for e in E for a in e}:
            c = (231, 76, 60) if (v in odd and hl is not None and hl != "q") else DARK
            d.ellipse((20 + P[v][0]*cs - 7, 20 + P[v][1]*cs - 7, 20 + P[v][0]*cs + 7, 20 + P[v][1]*cs + 7), fill=c)
        return im
    def card(rev):
        im = blank(); d = ImageDraw.Draw(im)
        text_block(im, "Which can you draw WITHOUT lifting your pen or going over a line twice?", 150, 46)
        option_tiles(im, [shape_img(*shapes[o], hl=(rev and i == k) if rev else "q") for i, o in enumerate(order)], 480, hl=k if rev else None, box=200)
        if rev: explain(im, "it needs 0 or 2 corners with an odd number of lines (red)", y=CH - 30, col=PURPLE, size=28)
        return im
    return dict(q=card(False), a=card(True), options=[f"Shape {c}" for c in "ABCD"], correct=k, question="DRAW IT IN ONE LINE!",
                banner=f"SHAPE {'ABCD'[k]}!", catch=False)

# 8. LAYERING (which is at the bottom)
LCOL = {"Red": (231, 76, 60), "Blue": (52, 120, 219), "Green": (46, 180, 100), "Yellow": (250, 205, 50), "Purple": (155, 89, 182), "Orange": (243, 140, 30)}
def layering(seed, level):
    r = random.Random(seed); n = [4, 5, 6][level]
    from PIL import ImageChops
    for _ in range(3000):
        names = r.sample(list(LCOL), n); shapes = []
        for nm in names:
            kind = r.choice(["rect", "circle"]); cx, cy = r.uniform(260, 700), r.uniform(200, 560); w, h = r.uniform(200, 330), r.uniform(180, 300)
            shapes.append((nm, kind, (cx - w/2, cy - h/2, cx + w/2, cy + h/2)))
        masks = []
        for nm, kind, box in shapes:
            m = Image.new("L", (CW, CH), 0); dm = ImageDraw.Draw(m)
            (dm.rounded_rectangle(box, 24, fill=255) if kind == "rect" else dm.ellipse(box, fill=255)); masks.append(m)
        def ov(i, j): return ImageChops.multiply(masks[i], masks[j]).getbbox() is not None
        # visible area of each shape must be decent
        vis_ok = True
        for i in range(n):
            above = Image.new("L", (CW, CH), 0)
            for j in range(i + 1, n): above = ImageChops.lighter(above, masks[j])
            vis = ImageChops.subtract(masks[i], above); area = sum(1 for p in vis.resize((96, 80)).getdata() if p > 128)
            if area < 260: vis_ok = False
        if not vis_ok: continue
        # unique bottom: every shape except index 0 sits on top of something it overlaps
        if all(any(ov(i, j) for j in range(i)) for i in range(1, n)) and sum(ov(0, j) for j in range(1, n)) >= 2: break
    def card(rev):
        im = blank(); d = ImageDraw.Draw(im)
        for idx, (nm, kind, box) in enumerate(shapes):
            col = LCOL[nm]
            (d.rounded_rectangle(box, 24, fill=col, outline=DARK, width=6) if kind == "rect" else d.ellipse(box, fill=col, outline=DARK, width=6))
        if rev:
            nm, kind, box = shapes[0]
            (d.rounded_rectangle(box, 24, outline=(255, 255, 255), width=8) if kind == "rect" else d.ellipse(box, outline=(255, 255, 255), width=8))
            explain(im, f"{nm} is under everything it touches", y=CH - 60, col=PURPLE, size=36)
        return im
    ans = shapes[0][0]; o, k = shuffle_opts(r, ans, [s[0] for s in shapes[1:]])
    return dict(q=card(False), a=card(True), options=o, correct=k, question="WHICH SHAPE IS AT THE BOTTOM?", banner=f"{ans.upper()}!", catch=False)

# 9. GRID PATHS
def grid_paths(seed, level):
    r = random.Random(seed); w, h = [(2, 2), (3, 2), (3, 3)][level]
    ans = math.comb(w + h, w)
    def card(rev):
        im = blank(); d = ImageDraw.Draw(im); cs = 150; gx = (CW - w*cs)/2; gy = 120
        for i in range(w + 1): d.line((gx + i*cs, gy, gx + i*cs, gy + h*cs), fill=DARK, width=8)
        for j in range(h + 1): d.line((gx, gy + j*cs, gx + w*cs, gy + j*cs), fill=DARK, width=8)
        for i in range(w + 1):
            for j in range(h + 1):
                x, y = gx + i*cs, gy + j*cs
                if rev:
                    v = math.comb(i + j, i)
                    d.ellipse((x - 30, y - 30, x + 30, y + 30), fill=(255, 245, 205), outline=PURPLE, width=4)
                    d.text((x, y + 2), str(v), font=font(30), fill=PURPLE, anchor="mm")
                else: d.ellipse((x - 10, y - 10, x + 10, y + 10), fill=DARK)
        for (x, y, lab, c) in ((gx, gy, "A", (52, 152, 219)), (gx + w*cs, gy + h*cs, "B", (231, 76, 60))):
            if not rev or True:
                d.ellipse((x - 40, y - 40, x + 40, y + 40), fill=c, outline="white", width=5); d.text((x, y + 2), lab if not rev else (lab if lab == "A" else str(ans)), font=font(36), fill="white", anchor="mm")
        if rev: explain(im, "each dot = the dot above + the dot to the left", y=CH - 90, col=PURPLE, size=34)
        else: d.text((CW/2, CH - 90), "only move RIGHT or DOWN along the lines", font=font(34), fill=GREY, anchor="mm")
        return im
    o, k = opts4(r, ans, [w*h, w + h, ans - 2, ans + 2, 2*(w + h)] + num_wrong(r, ans, (1, 3, 4)))
    return dict(q=card(False), a=card(True), options=o, correct=k, question="HOW MANY SHORTEST PATHS A TO B?", banner=f"{ans} PATHS!", catch=False)

# 10. DOMINO SEQUENCE
PIPS = {0: [], 1: [(.5, .5)], 2: [(.27, .27), (.73, .73)], 3: [(.27, .27), (.5, .5), (.73, .73)], 4: [(.27, .27), (.73, .27), (.27, .73), (.73, .73)],
        5: [(.27, .27), (.73, .27), (.5, .5), (.27, .73), (.73, .73)], 6: [(.27, .22), (.73, .22), (.27, .5), (.73, .5), (.27, .78), (.73, .78)]}
def domino_img(a, b, w=90, hl=False):
    h = 2*w; im = Image.new("RGBA", (w + 8, h + 8), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((4, 4, w + 4, h + 4), 14, fill=(255, 255, 255), outline=GREEN if hl else DARK, width=6 if hl else 4)
    d.line((14, 4 + w, w - 6, 4 + w), fill=DARK, width=3)
    for half, v in ((0, a), (1, b)):
        for px, py in PIPS[v]: x, y = 4 + px*w, 4 + half*w + py*w; d.ellipse((x - 7, y - 7, x + 7, y + 7), fill=DARK)
    return im
def domino(seed, level):
    r = random.Random(seed)
    TOP = {0: [0, 1, 2, 3, 4], 1: [0, 1, 2, 3, 4], 2: [0, 2, 1, 3, 2]}[level]
    BOT = {0: [0, 1, 2, 3, 4], 1: [4, 3, 2, 1, 0], 2: [4, 3, 2, 1, 0]}[level]
    dt, db = (1, 1) if level == 0 else ((1, -1) if level == 1 else ("+2, −1, +2, −1", -1))
    while True:
        t0, b0 = r.randint(0, 6), r.randint(0, 6); seq = [(t0 + TOP[i], b0 + BOT[i] - 4*(level >= 1)) for i in range(5)]
        if all(0 <= a <= 6 and 0 <= b <= 6 for a, b in seq): break
    ans = seq[4]
    cands = [(ans[1], ans[0]), (ans[0] + 1 if ans[0] < 6 else ans[0] - 1, ans[1]), (ans[0], ans[1] + 1 if ans[1] < 6 else ans[1] - 1), (seq[3][0], ans[1]), (ans[0], seq[3][1])]
    wrong = [c for c in dict.fromkeys(cands) if c != ans and all(0 <= v <= 6 for v in c)][:3]
    opts = wrong + [ans]; r.shuffle(opts); k = opts.index(ans)
    def card(rev):
        im = blank(); d = ImageDraw.Draw(im)
        for i in range(5):
            x = 110 + i*185
            if i < 4: paste_c(im, domino_img(*seq[i]), x, 210)
            elif rev: paste_c(im, domino_img(*ans, hl=True), x, 210)
            else:
                d.rounded_rectangle((x - 47, 116, x + 47, 304), 14, outline=RED, width=6); d.text((x, 212), "?", font=font(90), fill=RED, anchor="mm")
        option_tiles(im, [domino_img(*o, w=70, hl=rev and i == k) for i, o in enumerate(opts)], 530, hl=k if rev else None, box=190)
        if rev:
            tt = (f"top {dt},  bottom {db}" if isinstance(dt, str) else f"top {'+' if dt > 0 else ''}{dt},  bottom {'+' if db > 0 else ''}{db}")
            d.text((CW/2, 370), tt, font=font(38), fill=PURPLE, anchor="mm")
        return im
    return dict(q=card(False), a=card(True), options=[f"Domino {c}" for c in "ABCD"], correct=k, question="WHICH DOMINO COMES NEXT?",
                banner=f"DOMINO {'ABCD'[k]}!", catch=False)

# 11. MINI SUDOKU (4x4)
def sudoku(seed, level):
    r = random.Random(seed)
    base = [[1, 2, 3, 4], [3, 4, 1, 2], [2, 1, 4, 3], [4, 3, 2, 1]]
    perm = r.sample([1, 2, 3, 4], 4); G = [[perm[v - 1] for v in row] for row in base]
    rows = [0, 1] if r.random() < 0.5 else [1, 0]; rows += [2, 3] if r.random() < 0.5 else [3, 2]; G = [G[i] for i in rows]
    G = [list(c) for c in zip(*G)] if r.random() < 0.5 else G
    def count(Gp):
        cells = [(i, j) for i in range(4) for j in range(4) if Gp[i][j] == 0]; sols = 0
        def ok(Gp, i, j, v):
            if v in Gp[i] or v in [Gp[x][j] for x in range(4)]: return False
            bi, bj = i//2*2, j//2*2
            return all(Gp[x][y] != v for x in range(bi, bi + 2) for y in range(bj, bj + 2))
        def rec(k_):
            nonlocal sols
            if sols > 1: return
            if k_ == len(cells): sols += 1; return
            i, j = cells[k_]
            for v in range(1, 5):
                if ok(Gp, i, j, v): Gp[i][j] = v; rec(k_ + 1); Gp[i][j] = 0
        rec(0); return sols
    holes = [9, 10, 11][level]
    while True:
        P = [row[:] for row in G]; cells = r.sample([(i, j) for i in range(4) for j in range(4)], holes)
        for i, j in cells: P[i][j] = 0
        if count([row[:] for row in P]) == 1: break
    qi, qj = r.choice(cells); ans = G[qi][qj]
    def card(rev):
        im = blank(); d = ImageDraw.Draw(im); cs = 140; gx = (CW - 4*cs)/2; gy = 60
        for i in range(4):
            for j in range(4):
                x, y = gx + j*cs, gy + i*cs
                fill = (255, 245, 205) if (i, j) == (qi, qj) else ((245, 246, 252) if ((i//2) + (j//2)) % 2 == 0 else (232, 236, 250))
                d.rectangle((x, y, x + cs, y + cs), fill=fill, outline=(170, 175, 195), width=2)
                v = P[i][j]
                if (i, j) == (qi, qj): d.text((x + cs/2, y + cs/2 + 3), str(ans) if rev else "?", font=font(70), fill=GREEN if rev else RED, anchor="mm")
                elif v: d.text((x + cs/2, y + cs/2 + 3), str(v), font=font(64), fill=DARK, anchor="mm")
                elif rev: d.text((x + cs/2, y + cs/2 + 3), str(G[i][j]), font=font(52), fill=(180, 185, 205), anchor="mm")
        d.rectangle((gx, gy, gx + 4*cs, gy + 4*cs), outline=DARK, width=8)
        d.line((gx + 2*cs, gy, gx + 2*cs, gy + 4*cs), fill=DARK, width=8); d.line((gx, gy + 2*cs, gx + 4*cs, gy + 2*cs), fill=DARK, width=8)
        d.text((CW/2, CH - 80), "1-4 once in every row, column and box", font=font(34), fill=GREY, anchor="mm")
        return im
    opts = ["1", "2", "3", "4"]
    return dict(q=card(False), a=card(True), options=opts, correct=ans - 1, question="WHAT NUMBER GOES IN THE ?", banner=f"IT'S {ans}!", catch=False)

# 12. MAGIC SQUARE
def magic_square(seed, level):
    r = random.Random(seed); M = [[2, 7, 6], [9, 5, 1], [4, 3, 8]]
    for _ in range(r.randrange(4)): M = [list(x) for x in zip(*M[::-1])]
    if r.random() < 0.5: M = [row[::-1] for row in M]
    add = [0, r.randint(1, 5), r.randint(5, 15)][level]; mul = [1, 1, 2][level]
    M = [[v*mul + add for v in row] for row in M]; S = sum(M[0])
    qi, qj = r.randrange(3), r.randrange(3); ans = M[qi][qj]
    hide = {(qi, qj)}
    if level >= 1:
        others = [(i, j) for i in range(3) for j in range(3) if i != qi and j != qj]; hide.add(r.choice(others))
    def card(rev):
        im = blank(); d = ImageDraw.Draw(im); cs = 170; gx = (CW - 3*cs)/2; gy = 60
        for i in range(3):
            for j in range(3):
                x, y = gx + j*cs, gy + i*cs
                d.rounded_rectangle((x + 6, y + 6, x + cs - 6, y + cs - 6), 18, fill=(255, 245, 205) if (i, j) == (qi, qj) else (232, 240, 255), outline=DARK, width=4)
                if (i, j) == (qi, qj): t, c = (str(ans), GREEN) if rev else ("?", RED)
                elif (i, j) in hide: t, c = (str(M[i][j]), (170, 170, 190)) if rev else ("", DARK)
                else: t, c = str(M[i][j]), DARK
                d.text((x + cs/2, y + cs/2 + 3), t, font=font(66), fill=c, anchor="mm")
        msg = f"every row, column and diagonal adds to {S}" if level == 0 else "every row, column and diagonal adds to the SAME number"
        if rev and level >= 1: explain(im, f"every line adds to {S}", y=CH - 110, col=PURPLE, size=44)
        else: text_block(im, msg, CH - 120, 34, col=GREY)
        return im
    o, k = opts4(r, ans, num_wrong(r, ans, (1, 2, 3, 4)))
    return dict(q=card(False), a=card(True), options=o, correct=k, question="COMPLETE THE MAGIC SQUARE!", banner=f"IT'S {ans}!", catch=False)

# 13. NUMBER WHEEL
def number_wheel(seed, level):
    r = random.Random(seed)
    if level == 0:
        S = r.randint(15, 25); a = r.sample(range(2, S - 1), 4); pairs = [(x, S - x) for x in a]; rule = f"opposite numbers add up to {S}"
    elif level == 1:
        a = r.sample(range(2, 12), 4); pairs = [(x, 2*x) for x in a]; rule = "each number is DOUBLE the one opposite"
    else:
        a = r.sample(range(2, 10), 4); pairs = [(x, x*x) for x in a]; rule = "opposite = the number SQUARED"
    vals = [None]*8
    for i, (x, y) in enumerate(pairs): vals[i] = x; vals[i + 4] = y
    q = r.choice([4, 5, 6, 7]); ans = vals[q]
    def card(rev):
        im = blank(); d = ImageDraw.Draw(im); cx, cy, R = CW/2, 360, 300
        cols = [(255, 214, 226), (210, 235, 255), (220, 245, 210), (255, 236, 179)]
        for i in range(8):
            d.pieslice((cx - R, cy - R, cx + R, cy + R), i*45 - 112.5, i*45 - 67.5, fill=cols[i % 4], outline=DARK, width=5)
        d.ellipse((cx - 70, cy - 70, cx + 70, cy + 70), fill="white", outline=DARK, width=5)
        for i in range(8):
            a_ = math.radians(i*45 - 90); x, y = cx + math.cos(a_)*R*0.68, cy + math.sin(a_)*R*0.68
            t = str(vals[i]) if (i != q or rev) else "?"
            d.text((x, y + 3), t, font=font(58), fill=(GREEN if (rev and i == q) else (RED if i == q else DARK)), anchor="mm")
        if rev: explain(im, rule, y=CH - 60, col=PURPLE, size=36)
        else: d.text((CW/2, CH - 60), "look at the OPPOSITE slices", font=font(34), fill=GREY, anchor="mm")
        return im
    o, k = opts4(r, ans, num_wrong(r, ans, (1, 2, 3, 5)) if level < 2 else [ans + 1, ans - 1, vals[q - 4]*2, ans + 2])
    return dict(q=card(False), a=card(True), options=o, correct=k, question="WHAT'S THE MISSING NUMBER?", banner=f"IT'S {ans}!", catch=False)

# 14. BINARY BULBS
def binary(seed, level):
    r = random.Random(seed); n = [4, 5, 6][level]
    while True:
        bits = [r.random() < 0.5 for _ in range(n)]
        if 2 <= sum(bits) <= n - 1: break
    vals = [2**(n - 1 - i) for i in range(n)]; ans = sum(v for v, b in zip(vals, bits) if b)
    def card(rev):
        im = blank(); d = ImageDraw.Draw(im); gap = (CW - 80)/n
        for i, (v, b) in enumerate(zip(vals, bits)):
            x = 40 + gap*(i + 0.5); y = 280
            if b:
                from PIL import ImageFilter
                gl = Image.new("RGBA", (200, 200), (0, 0, 0, 0)); ImageDraw.Draw(gl).ellipse((30, 30, 170, 170), fill=(255, 220, 60, 170)); im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(18)), (int(x - 100), int(y - 120)))
            d.ellipse((x - 52, y - 72, x + 52, y + 32), fill=(255, 225, 70) if b else (225, 228, 238), outline=DARK, width=5)
            d.rectangle((x - 26, y + 30, x + 26, y + 70), fill=(150, 150, 165), outline=DARK, width=4)
            show = level < 2 or rev
            d.text((x, y + 140), str(v) if show else "?", font=font(48), fill=(PURPLE if (b and rev) else DARK), anchor="mm")
        hint = "the right bulb = 1, each bulb to the left is worth DOUBLE" if level == 2 else "add up the values of the bulbs that are ON"
        text_block(im, hint, 560, 36, col=GREY)
        if rev: explain(im, " + ".join(str(v) for v, b in zip(vals, bits) if b) + f" = {ans}", y=CH - 60, col=GREEN, size=44)
        return im
    o, k = opts4(r, ans, num_wrong(r, ans, (1, 2, 4, 8)))
    return dict(q=card(False), a=card(True), options=o, correct=k, question="WHAT NUMBER DO THE LIGHTS SHOW?", banner=f"{ans}!", catch=False)

# 15. PIZZA FRACTIONS
def pizza(seed, level):
    r = random.Random(seed); n = [4, 8, 6][level]; npz = 1 if level < 2 else 2
    total = n*npz; eaten = r.randint(1, total - 2); left = total - eaten
    g = math.gcd(left, total); ans = f"{left//g}/{total//g}"
    def frac(a, b): g_ = math.gcd(a, b); return f"{a//g_}/{b//g_}"
    def card(rev):
        im = blank(); d = ImageDraw.Draw(im); R = 210 if npz == 1 else 180
        eat = set(random.Random(seed + 1).sample(range(total), eaten))
        for p in range(npz):
            cx = CW/2 if npz == 1 else CW/2 + (p - 0.5)*430; cy = 320
            for i in range(n):
                gi = p*n + i; a0 = i*360/n - 90; a1 = (i + 1)*360/n - 90
                if gi in eat: d.pieslice((cx - R, cy - R, cx + R, cy + R), a0, a1, fill=(245, 240, 232), outline=(220, 210, 195), width=3); continue
                d.pieslice((cx - R, cy - R, cx + R, cy + R), a0, a1, fill=(235, 160, 70), outline=(150, 90, 40), width=5)
                d.pieslice((cx - R + 18, cy - R + 18, cx + R - 18, cy + R - 18), a0 + 1, a1 - 1, fill=(250, 210, 90))
                for t in range(2):
                    am = math.radians((a0 + a1)/2 + (t - 0.5)*(a1 - a0)*0.4); rr = R*(0.4 + 0.25*t)
                    px, py = cx + math.cos(am)*rr, cy + math.sin(am)*rr; d.ellipse((px - 16, py - 16, px + 16, py + 16), fill=(200, 50, 50))
        if rev: explain(im, f"{left} of {total} slices left = {ans}", y=CH - 80, col=GREEN, size=42)
        else: d.text((CW/2, CH - 80), f"{'each pizza was' if npz > 1 else 'it was'} cut into {n} equal slices", font=font(34), fill=GREY, anchor="mm")
        return im
    from fractions import Fraction as Fr
    cand = [Fr(eaten, total), Fr(max(1, left - 1), total), Fr(left + 1, total) if left + 1 < total else Fr(1, total), Fr(left, total + n), Fr(1, 2), Fr(1, 3), Fr(2, 3), Fr(1, 4), Fr(3, 4), Fr(1, 8)]
    seen = {Fr(left, total)}; wrong = []
    for c in cand:
        if c not in seen and 0 < c < 1: seen.add(c); wrong.append(f"{c.numerator}/{c.denominator}")
    o, k = shuffle_opts(r, ans, wrong)
    return dict(q=card(False), a=card(True), options=o, correct=k, question="HOW MUCH PIZZA IS LEFT?", banner=f"{ans} LEFT!", catch=False)

GENS = dict(mirror=mirror, tetris=tetris, knight=knight, tictactoe=tictactoe, laser=laser, circuit=circuit, one_line=one_line,
            layering=layering, grid_paths=grid_paths, domino=domino, sudoku=sudoku, magic_square=magic_square,
            number_wheel=number_wheel, binary=binary, pizza=pizza)
