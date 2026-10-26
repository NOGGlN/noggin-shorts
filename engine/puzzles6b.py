"""Batch-6 genres, part B (math & logic word puzzles, probability, geometry)."""
import math, random, itertools
from PIL import Image, ImageDraw, ImageFilter
from render import font, DARK
from v3 import CARD, blank, emoji, GREEN
from puzzles4 import shuffle_opts, num_wrong, explain, em, paste_c, BADGE, RED, BLUE, ORANGE, PURPLE, GREY, SOFT, CW, CH
from puzzles5 import text_block, option_tiles

def opts4(r, ans, wrong, fmt=str):
    o, k = shuffle_opts(r, ans, [w for w in wrong if w != ans] + num_wrong(r, ans, (1, 2, 3, 4, 5, 6)) if isinstance(ans, int) else wrong)
    return [fmt(x) for x in o], k

def scene(im, emojis, y=150, size=120):
    n = len(emojis); gap = (CW - 120)/n
    for i, e in enumerate(emojis): paste_c(im, em(e, size), 60 + gap*(i + 0.5), y)

# 16. MISSING ANGLE
def angle(seed, level):
    r = random.Random(seed)
    if level == 0:
        a, b = r.randint(35, 80), r.randint(35, 80); ans = 180 - a - b; known = [a, b]; shape = "tri"; rule = "a triangle's angles add up to 180°"
    elif level == 1:
        a, b, c = r.randint(70, 110), r.randint(70, 110), r.randint(60, 100); ans = 360 - a - b - c; known = [a, b, c]; shape = "quad"; rule = "a 4-sided shape's angles add up to 360°"
    else:
        a = r.randint(40, 70); b = r.randint(40, 70); ans = a + b; known = [a, b]; shape = "ext"; rule = f"x = 180° − (180° − {a}° − {b}°) = {a}° + {b}°"
    def card(rev):
        im = blank(); d = ImageDraw.Draw(im); lab = (str(ans) + "°") if rev else "x"
        if shape == "tri":
            A, B, C = (180, 600), (780, 600), (420, 130)
            d.polygon([A, B, C], fill=(232, 240, 255), outline=DARK); d.line([A, B, C, A], fill=DARK, width=8)
            for p, t, c in ((A, f"{known[0]}°", DARK), (B, f"{known[1]}°", DARK), (C, lab, GREEN if rev else RED)):
                cx, cy = (p[0] + (480 - p[0])*0.22, p[1] + (443 - p[1])*0.22); d.text((cx, cy), t, font=font(54), fill=c, anchor="mm")
        elif shape == "quad":
            P = [(170, 580), (800, 620), (720, 160), (250, 210)]
            d.polygon(P, fill=(232, 240, 255)); d.line(P + [P[0]], fill=DARK, width=8)
            labs = [f"{known[0]}°", f"{known[1]}°", f"{known[2]}°", lab]
            cx0, cy0 = sum(p[0] for p in P)/4, sum(p[1] for p in P)/4
            for p, t, i in zip(P, labs, range(4)):
                d.text((p[0] + (cx0 - p[0])*0.22, p[1] + (cy0 - p[1])*0.22), t, font=font(50), fill=(GREEN if rev else RED) if i == 3 else DARK, anchor="mm")
        else:
            A, B, C, D = (150, 600), (620, 600), (420, 170), (860, 600)
            d.line([A, D], fill=DARK, width=8); d.line([A, C, B], fill=DARK, width=8)
            d.polygon([A, B, C], fill=(232, 240, 255)); d.line([A, C, B, A], fill=DARK, width=8); d.line([B, D], fill=DARK, width=8)
            d.text((A[0] + 90, A[1] - 40), f"{known[0]}°", font=font(50), fill=DARK, anchor="mm")
            d.text((C[0], C[1] + 80), f"{known[1]}°", font=font(50), fill=DARK, anchor="mm")
            d.text((B[0] + 80, B[1] - 40), lab, font=font(54), fill=GREEN if rev else RED, anchor="mm")
        if rev: explain(im, rule, y=CH - 60, col=PURPLE, size=34)
        return im
    o, k = opts4(r, ans, [ans + 10, ans - 10, 180 - ans if ans < 180 else ans - 20, ans + 5], fmt=lambda v: f"{v}°")
    return dict(q=card(False), a=card(True), options=o, correct=k, question="WHAT'S ANGLE x?", banner=f"x = {ans}°!", catch=False)

# 17. PERCENT TRAP
def percent(seed, level):
    r = random.Random(seed)
    if level == 0:
        p = r.choice([10, 20, 25, 50]); v = r.choice([40, 60, 80, 120, 200]); ans = v - v*p//100
        q = f"A ${v} game is {p}% off. What do you pay?"; why = f"{p}% of {v} = {v*p//100}, so {v} − {v*p//100}"; wrong = [v*p//100, v - p, ans + 10]; catch = False
    else:
        p = r.choice([20, 50]) if level == 1 else r.choice([10, 25, 40]); v = r.choice([100, 200])
        up = v + v*p//100; ans = up - up*p//100
        q = f"A ${v} jacket goes UP {p}%, then DOWN {p}%. What does it cost now?"; why = f"${v} up {p}% = ${up}, then {p}% of ${up} comes off = ${ans}"; wrong = [v, v + p, up]; catch = True
    def card(rev):
        im = blank(); d = ImageDraw.Draw(im); scene(im, ["🧥" if level else "🎮", "🏷️"], y=140, size=130)
        text_block(im, q, 400, 54)
        if rev: explain(im, why, y=CH - 60, col=PURPLE, size=32)
        return im
    o, k = opts4(r, ans, wrong, fmt=lambda x: f"${x}")
    return dict(q=card(False), a=card(True), options=o, correct=k, question="DO THE MATH!", banner=f"${ans}!", catch=catch)

# 18. HEX COLOR
HEXES = [("#FF0000", (255, 0, 0)), ("#00FF00", (0, 255, 0)), ("#0000FF", (0, 0, 255)), ("#FFFF00", (255, 255, 0)),
         ("#00FFFF", (0, 255, 255)), ("#FF00FF", (255, 0, 255)), ("#000000", (0, 0, 0)), ("#FFFFFF", (255, 255, 255))]
def hex_color(seed, level):
    r = random.Random(seed); hx, rgb = r.choice(HEXES if level < 2 else HEXES[3:6])
    def card(rev):
        im = blank(); d = ImageDraw.Draw(im)
        d.rounded_rectangle((CW/2 - 230, 60, CW/2 + 230, 400), 40, fill=rgb, outline=DARK, width=6)
        text_block(im, "Colour codes go #RRGGBB  (red, green, blue: 00 = none, FF = full)", 520, 36, col=GREY)
        if rev: explain(im, f"{hx}: " + ", ".join(f"{n} {'FULL' if hx[1 + 2*i:3 + 2*i] == 'FF' else 'none'}" for i, n in enumerate(("red", "green", "blue"))), y=CH - 70, col=PURPLE, size=32)
        return im
    o, k = shuffle_opts(r, hx, r.sample([h for h, _ in HEXES if h != hx], 3))
    return dict(q=card(False), a=card(True), options=o, correct=k, question="WHICH COLOUR CODE IS THIS?", banner=f"{hx}!", catch=False)

# 19. UNIT CONVERSION
def unit_convert(seed, level):
    r = random.Random(seed)
    items = [("How many minutes are in 2.5 hours?", 150, [125, 250, 90], "2.5 × 60 = 150", "⏰"),
             ("How many seconds are in 4 minutes?", 240, [400, 160, 200], "4 × 60 = 240", "⏱️"),
             ("How many centimetres are in 3.2 metres?", 320, [32, 3200, 302], "3.2 × 100 = 320", "📏"),
             ("How many grams are in 1.5 kg?", 1500, [150, 15000, 1050], "1.5 × 1000 = 1500", "⚖️")]
    q, ans, wrong, why, e = r.choice(items)
    def card(rev):
        im = blank(); paste_c(im, em(e, 150), CW/2, 150); text_block(im, q, 420, 58)
        if rev: explain(im, why, y=CH - 80, col=GREEN, size=48)
        return im
    o, k = opts4(r, ans, wrong)
    return dict(q=card(False), a=card(True), options=o, correct=k, question="QUICK CONVERSION!", banner=f"{ans}!", catch=False)

# 20. AGE PUZZLE
def age(seed, level):
    r = random.Random(seed)
    if level <= 1:
        s = r.choice([6, 8, 10, 12]); sis = s//2; later = s + r.choice([10, 14, 20])
        q = f"When I was {s}, my sister was half my age. Now I'm {later}. How old is she?"; ans = later - (s - sis)
        why = f"she's always {s - sis} years younger: {later} − {s - sis}"; wrong = [later//2, ans + 2, ans - 2]; catch = True
    else:
        n = r.choice([4, 5, 6, 8]); ann = n; tom = 3*ann
        q = f"Tom is 3× Ann's age. In {n} years he'll be only 2× her age. How old is Ann now?"; ans = ann
        why = f"3a + {n} = 2(a + {n}), so a = {n}"; wrong = [2*n, n + 2, 3*n]; catch = False
    def card(rev):
        im = blank(); scene(im, ["👦", "👧"], y=140, size=130); text_block(im, q, 420, 52)
        if rev: explain(im, why, y=CH - 60, col=PURPLE, size=36)
        return im
    o, k = opts4(r, ans, wrong)
    return dict(q=card(False), a=card(True), options=o, correct=k, question="HOW OLD?", banner=f"{ans} YEARS OLD!", catch=catch)

# 21. RANKING
NAMES = ["Ava", "Ben", "Cara", "Dan", "Eve", "Finn", "Gia", "Hugo"]
def ranking(seed, level):
    r = random.Random(seed); n = [4, 4, 5][level]; ppl = r.sample(NAMES, n)  # ppl[0] tallest
    pairs = [(ppl[i], ppl[i + 1]) for i in range(n - 1)]; r.shuffle(pairs)
    sents = []
    for a, b in pairs: sents.append(f"{a} is taller than {b}." if r.random() < 0.5 else f"{b} is shorter than {a}.")
    ask_short = r.random() < 0.5; ans = ppl[-1] if ask_short else ppl[0]
    def card(rev):
        im = blank(); d = ImageDraw.Draw(im); y = 90
        for s_ in sents: d.text((CW/2, y), s_, font=font(46), fill=DARK, anchor="mm"); y += 80
        d.text((CW/2, y + 30), f"Who is the {'SHORTEST' if ask_short else 'TALLEST'}?", font=font(52), fill=PURPLE, anchor="mm")
        if rev:
            x0 = 120; gap = (CW - 240)/(n - 1)
            for i, p in enumerate(ppl):
                h = 170 - i*24; x = x0 + i*gap; yb = CH - 40
                d.rounded_rectangle((x - 40, yb - h, x + 40, yb), 18, fill=GREEN if p == ans else (190, 200, 225))
                d.text((x, yb - h - 24), p, font=font(32), fill=DARK, anchor="mm")
        return im
    o, k = shuffle_opts(r, ans, [p for p in ppl if p != ans])
    return dict(q=card(False), a=card(True), options=o, correct=k, question=f"WHO IS THE {'SHORTEST' if ask_short else 'TALLEST'}?",
                banner=f"{ans.upper()}!", catch=False)

# 22. FAMILY RELATIONS
FAM = [("Your brother's son is your...?", "Nephew", ["Cousin", "Uncle", "Grandson"], "your sibling's son = nephew"),
       ("Your mum's brother's daughter is your...?", "Cousin", ["Niece", "Aunt", "Sister"], "your uncle's kid = cousin"),
       ("Your mum's mum's ONLY daughter is...?", "Your mum", ["Your aunt", "Your sister", "Your grandma"], "grandma's only daughter = mum!")]
def family(seed, level):
    r = random.Random(seed); q, ans, wrong, why = FAM[min(level, 2)]
    def card(rev):
        im = blank(); scene(im, ["👵", "👩", "🧒"], y=140, size=120); text_block(im, q, 420, 60)
        if rev: explain(im, why, y=CH - 70, col=PURPLE, size=40)
        return im
    o, k = shuffle_opts(r, ans, wrong)
    return dict(q=card(False), a=card(True), options=o, correct=k, question="WHO ARE THEY?", banner=f"{ans.upper()}!", catch=level >= 2)

# 23. QUEUE POSITION
def queue(seed, level):
    r = random.Random(seed); f, b = r.randint(3, 8), r.randint(3, 9); ans = f + b - 1
    def card(rev):
        im = blank(); d = ImageDraw.Draw(im)
        row = ["🧍", "🧍", "…", "🙋", "…", "🧍", "🧍"]
        for i, e in enumerate(row):
            x = 140 + i*(CW - 280)/6
            if e == "…": d.text((x, 170), "• • •", font=font(40), fill=GREY, anchor="mm")
            else: paste_c(im, em(e, 90), x, 170)
        d.text((140 + 3*(CW - 280)/6, 250), "Mia", font=font(34), fill=PURPLE, anchor="mm")
        text_block(im, f"Mia is {f}th from the FRONT and {b}th from the BACK of the line. How many people are in the line?", 430, 50)
        if rev: explain(im, f"{f} + {b} − 1 (don't count Mia twice!)", y=CH - 60, col=RED, size=40)
        return im
    o, k = opts4(r, ans, [f + b, f + b + 1, ans - 1])
    return dict(q=card(False), a=card(True), options=o, correct=k, question="HOW MANY PEOPLE?", banner=f"{ans} PEOPLE!", catch=True)

# 24. BUS DRIVER
def bus(seed, level):
    r = random.Random(seed); start = r.randint(6, 12); steps = []; cur = start
    for s_ in range(3):
        off = r.randint(1, min(5, cur)); on = r.randint(1, 6); steps.append((off, on)); cur = cur - off + on
    ans = cur + 1
    def card(rev):
        im = blank(); d = ImageDraw.Draw(im); paste_c(im, em("🚌", 140), CW/2, 110)
        y = 230; d.text((CW/2, y), f"YOU are driving a bus with {start} passengers.", font=font(40), fill=DARK, anchor="mm")
        for i, (off, on) in enumerate(steps):
            y += 70; d.text((CW/2, y), f"Stop {i + 1}:  {off} get off,  {on} get on", font=font(42), fill=(70, 70, 95), anchor="mm")
        d.text((CW/2, y + 100), "How many PEOPLE are on the bus?", font=font(48), fill=PURPLE, anchor="mm")
        if rev: explain(im, f"{cur} passengers + YOU, the driver = {ans}", y=CH - 50, col=RED, size=38)
        return im
    o, k = opts4(r, ans, [cur, cur - 1, ans + 1])
    return dict(q=card(False), a=card(True), options=o, correct=k, question="COUNT THE PEOPLE!", banner=f"{ans} PEOPLE!", catch=True)

# 25. SNAIL IN A WELL
def snail(seed, level):
    r = random.Random(seed)
    while True:
        D = r.randint(8, 20); u = r.randint(3, 5); dn = r.randint(1, u - 1)
        if D > u: break
    ans = math.ceil((D - u)/(u - dn)) + 1; naive = math.ceil(D/(u - dn))
    if naive == ans: naive = ans + 1
    def card(rev):
        im = blank(); d = ImageDraw.Draw(im)
        d.rectangle((90, 70, 330, 620), fill=(205, 195, 180), outline=DARK, width=6); d.rectangle((120, 70, 300, 620), fill=(120, 170, 220))
        paste_c(im, em("🐌", 90), 210, 560)
        text_block(im, f"A snail climbs {u} m up a {D} m well each day, but slides {dn} m back each night.", 260, 44, maxw=560)
        im2 = ImageDraw.Draw(im); im2.text((640, 520), "How many days to get OUT?", font=font(40), fill=PURPLE, anchor="mm")
        if rev: explain(im, f"on day {ans} it climbs out before sliding back!", y=CH - 50, col=RED, size=38)
        return im
    # text_block centres on CW/2; shift by drawing into a sub-canvas
    def card2(rev):
        im = blank(); d = ImageDraw.Draw(im)
        d.rectangle((70, 60, 300, 620), fill=(205, 195, 180), outline=DARK, width=6); d.rectangle((100, 60, 270, 620), fill=(120, 170, 220))
        for y in range(80, 620, 60): d.line((100, y, 270, y), fill=(150, 195, 235), width=2)
        paste_c(im, em("🐌", 90), 185, 570 if not rev else 90)
        sub = Image.new("RGBA", (CW, 520), (0, 0, 0, 0)); text_block(sub, f"A snail climbs {u} m up a {D} m well each day, then slides {dn} m back each night.", 200, 46, maxw=560)
        im.alpha_composite(sub.crop((CW/2 - 290, 0, CW/2 + 290, 520)), (330, 40))
        d.text((630, 520), "How many days", font=font(46), fill=PURPLE, anchor="mm"); d.text((630, 580), "to get OUT?", font=font(46), fill=PURPLE, anchor="mm")
        if rev: explain(im, f"day {ans}: it reaches the top before it can slide back!", y=CH - 50, col=RED, size=34)
        return im
    o, k = opts4(r, ans, [naive, D, ans - 1])
    return dict(q=card2(False), a=card2(True), options=o, correct=k, question="HOW MANY DAYS?", banner=f"{ans} DAYS!", catch=True)

# 26. LILY PADS (doubling)
def lily(seed, level):
    r = random.Random(seed); N = r.choice([20, 24, 30, 40, 48]); ans = N - 1
    def card(rev):
        im = blank(); d = ImageDraw.Draw(im); d.ellipse((90, 60, CW - 90, 430), fill=(110, 170, 230), outline=(70, 120, 190), width=6)
        rr = random.Random(seed)
        for _ in range(9):
            x, y = rr.uniform(200, CW - 200), rr.uniform(140, 350); d.ellipse((x - 45, y - 30, x + 45, y + 30), fill=(70, 170, 80), outline=(40, 120, 50), width=4)
        text_block(im, f"Lily pads DOUBLE every day. The pond is fully covered on day {N}. On which day was it HALF covered?", 570, 44)
        if rev: explain(im, f"it doubles overnight: half on day {ans}, full on day {N}", y=CH - 50, col=RED, size=34)
        return im
    o, k = opts4(r, ans, [N//2, N - 2, N//2 + 1])
    return dict(q=card(False), a=card(True), options=o, correct=k, question="WHICH DAY?", banner=f"DAY {ans}!", catch=True)

# 27. SOCKS (pigeonhole)
def socks(seed, level):
    r = random.Random(seed); kcol = [2, 3, 3][level]; each = r.choice([8, 10, 12])
    cols = ["red", "blue", "green"][:kcol]; ans = kcol + 1
    def card(rev):
        im = blank(); d = ImageDraw.Draw(im); scene(im, ["🧦"]*kcol, y=140, size=120)
        text_block(im, f"A drawer has {each} socks of each colour ({', '.join(cols)}). In the DARK, how many must you grab to be SURE of a matching pair?", 440, 46)
        if rev: explain(im, f"{kcol} socks could all differ, the next one MUST match", y=CH - 50, col=RED, size=34)
        return im
    o, k = opts4(r, ans, [each + 1, 2, kcol*each//2])
    return dict(q=card(False), a=card(True), options=o, correct=k, question="HOW MANY SOCKS?", banner=f"{ans} SOCKS!", catch=True)

# 28. TRUTH SIGNS (exactly one sign tells the truth)
def liar(seed, level):
    r = random.Random(seed); doors = ["Red", "Blue", "Green"]
    for _ in range(10000):
        st = [(r.choice(doors), r.random() < 0.5) for _ in range(3)]  # (door, is_negated)
        def truth(s, exit_): return (exit_ != s[0]) if s[1] else (exit_ == s[0])
        sol = [e for e in doors if sum(truth(s, e) for s in st) == 1]
        if len(sol) == 1 and len({(s[0], s[1]) for s in st}) == 3: ans = sol[0]; break
    COL = {"Red": (231, 76, 60), "Blue": (52, 120, 219), "Green": (46, 160, 90)}
    def card(rev):
        im = blank(); d = ImageDraw.Draw(im)
        for i, dn in enumerate(doors):
            x = 170 + i*310
            d.rounded_rectangle((x - 95, 230, x + 95, 560), 20, fill=COL[dn], outline=(GREEN if rev and dn == ans else DARK), width=12 if rev and dn == ans else 5)
            d.ellipse((x + 50, 390, x + 70, 410), fill=(255, 220, 90))
            sd, neg = st[i]; txt_ = f"The exit is {'NOT ' if neg else ''}{sd}"
            d.rounded_rectangle((x - 140, 60, x + 140, 200), 18, fill=(255, 250, 230), outline=DARK, width=4)
            lines = ["The exit", f"is {'NOT ' if neg else ''}", sd]
            d.text((x, 95), "The exit is", font=font(30), fill=DARK, anchor="mm")
            d.text((x, 140), ("NOT " if neg else "") + sd.upper(), font=font(38), fill=RED if neg else DARK, anchor="mm")
            if rev:
                ok = (ans != sd) if neg else (ans == sd)
                d.text((x, 180), "TRUE" if ok else "false", font=font(26), fill=GREEN if ok else GREY, anchor="mm")
        d.text((CW/2, CH - 90), "Only ONE sign is telling the truth.", font=font(40), fill=PURPLE, anchor="mm")
        d.text((CW/2, CH - 40), "Which door is the exit?", font=font(36), fill=GREY, anchor="mm")
        return im
    opts = doors + ["No exit"]
    return dict(q=card(False), a=card(True), options=opts, correct=doors.index(ans), question="WHICH DOOR IS THE EXIT?", banner=f"{ans.upper()} DOOR!", catch=False)

# 29. SPINNER PROBABILITY (size trap)
SPC = {"Red": (231, 76, 60), "Blue": (52, 120, 219), "Green": (46, 180, 100), "Yellow": (250, 205, 50)}
def spinner(seed, level):
    r = random.Random(seed)
    for _ in range(5000):
        names = list(SPC); r.shuffle(names)
        # many small slices for one colour, few big slices for another
        sl = []
        for nm in names:
            cnt = r.randint(1, 4); sl += [nm]*cnt
        r.shuffle(sl); w = [r.uniform(0.5, 2.5) for _ in sl]; tot = sum(w); ang = [x/tot*360 for x in w]
        area = {nm: sum(a for s_, a in zip(sl, ang) if s_ == nm) for nm in names}; cnt = {nm: sl.count(nm) for nm in names}
        best = max(area, key=area.get); mostslices = max(cnt, key=cnt.get)
        srt = sorted(area.values())
        if srt[-1] - srt[-2] > 25 and (level < 2 or (mostslices != best and list(cnt.values()).count(cnt[mostslices]) == 1)): break
    def card(rev):
        im = blank(); d = ImageDraw.Draw(im); cx, cy, R = CW/2, 340, 280; a0 = -90
        for s_, a in zip(sl, ang):
            d.pieslice((cx - R, cy - R, cx + R, cy + R), a0, a0 + a, fill=SPC[s_], outline=(255, 255, 255), width=5); a0 += a
        d.ellipse((cx - 22, cy - 22, cx + 22, cy + 22), fill=DARK); d.polygon([(cx - 14, cy), (cx + 14, cy), (cx, cy - 200)], fill=DARK)
        if rev: explain(im, "it's about the total AREA, not how many slices", y=CH - 60, col=RED, size=34)
        else: d.text((CW/2, CH - 60), "spin once...", font=font(36), fill=GREY, anchor="mm")
        return im
    o, k = shuffle_opts(r, best, [n for n in SPC if n != best])
    return dict(q=card(False), a=card(True), options=o, correct=k, question="WHICH COLOUR IS MOST LIKELY?", banner=f"{best.upper()}!", catch=level >= 2)

# 30. VOLUME (which glass holds more)
def volume(seed, level):
    r = random.Random(seed)
    while True:
        r1, h1 = r.randint(2, 3), r.randint(9, 14); r2, h2 = 2*r1, r.randint(3, 5)
        v1, v2 = r1*r1*h1, r2*r2*h2
        if abs(v1 - v2) > 0.15*max(v1, v2) and v2 > v1: break
    tall_is_A = r.random() < 0.5
    def card(rev):
        im = blank(); d = ImageDraw.Draw(im); sc = 32; base = 540
        glasses = [(r1, h1, v1), (r2, h2, v2)] if tall_is_A else [(r2, h2, v2), (r1, h1, v1)]
        for i, (rr, hh, vv) in enumerate(glasses):
            x = 260 + i*440; w = rr*2*sc; h = hh*sc
            d.rectangle((x - w/2, base - h, x + w/2, base), fill=(200, 230, 255), outline=DARK, width=6)
            d.rectangle((x - w/2 + 6, base - h*0.85, x + w/2 - 6, base - 6), fill=(110, 180, 240))
            d.text((x, base + 40), "AB"[i], font=font(54), fill=BADGE[i], anchor="mm")
            d.text((x + w/2 + 14, base - h/2), f"{hh} cm", font=font(30), fill=DARK, anchor="lm")
            d.text((x, base - h - 30), f"{2*rr} cm wide", font=font(30), fill=DARK, anchor="mm")
            if rev: d.text((x, base + 95), f"r²×h = {rr*rr*hh}", font=font(30), fill=PURPLE, anchor="mm")
        if rev: explain(im, "doubling the width = 4× the space!", y=CH - 30, col=RED, size=32)
        return im
    ans = "Glass B" if tall_is_A else "Glass A"
    opts = ["Glass A", "Glass B", "Same", "Can't tell"]
    return dict(q=card(False), a=card(True), options=opts, correct=opts.index(ans), question="WHICH GLASS HOLDS MORE?", banner=f"{ans.upper()}!", catch=True)

GENS = dict(angle=angle, percent=percent, hex_color=hex_color, unit_convert=unit_convert, age=age, ranking=ranking, family=family,
            queue=queue, bus=bus, snail=snail, lily=lily, socks=socks, liar=liar, spinner=spinner, volume=volume)
