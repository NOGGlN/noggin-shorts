"""Batch-6 genres, part C (words, knowledge, real-life data, codes)."""
import math, random, re, os
from PIL import Image, ImageDraw, ImageFont
from render import font, DARK
from v3 import CARD, blank, emoji, GREEN
from puzzles4 import shuffle_opts, num_wrong, explain, em, paste_c, BADGE, RED, BLUE, ORANGE, PURPLE, GREY, SOFT, CW, CH
from puzzles5 import text_block, option_tiles

MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
def mono(sz): return ImageFont.truetype(MONO, sz)
_W = None
def words(n):
    global _W
    if _W is None:
        _W = set()
        for line in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "cmudict.dict"), encoding="utf-8"):
            w = line.split()[0]
            if w.isalpha() and "(" not in w: _W.add(w.upper())
    return {w for w in _W if len(w) == n}
COMMON4 = set("""COLD CORD CARD WARD WORD WORM WARM HEAD HEAL TEAL TELL TALL TAIL LOVE LOSE LOST LIST LIFT CAKE LAKE LIKE BIKE BAKE MAKE
MAKE MILK SILK SILL HILL HALL BALL BELL BELT MELT MALT SALT SALE PALE PILE TILE TIME TAME GAME CAME CAPE TAPE TYPE HOPE ROPE
ROSE NOSE NOTE VOTE MOTE MOLE HOLE HOME COME CORE MORE MOVE LIVE LINE MINE MINT HINT HUNT HURT CART DART DARK PARK PART PORT
SORT SOFT LOFT LEFT FISH DISH WISH WASH CASH CAST LAST FAST FIST MIST MOST POST PAST PEST BEST NEST REST TEST TENT RENT BENT""".split())

# 31. WORD LADDER
LADDERS = [["COLD", "CORD", "WORD", "WARD", "WARM"], ["HEAD", "HEAL", "TEAL", "TELL", "TALL"], ["LOVE", "LOSE", "LOST", "LIST", "LIFT"],
           ["CAKE", "LAKE", "LIKE", "BIKE"], ["FISH", "DISH", "WISH", "WASH", "CASH"], ["MILK", "SILK", "SILL", "HILL", "HALL"]]
def diff1(a, b): return sum(x != y for x, y in zip(a, b)) == 1
def word_ladder(seed, level):
    r = random.Random(seed); lad = r.choice(LADDERS); i = r.randrange(1, len(lad) - 1); ans = lad[i]
    pool = [w for w in COMMON4 if w != ans and not (diff1(w, lad[i - 1]) and diff1(w, lad[i + 1])) and (diff1(w, lad[i - 1]) or diff1(w, lad[i + 1]))]
    if len(pool) < 3: pool += [w for w in sorted(COMMON4) if w not in pool and w != ans and not (diff1(w, lad[i - 1]) and diff1(w, lad[i + 1])) and w not in lad]
    wrong = r.sample(sorted(pool)[:12] if len(pool) > 12 else sorted(pool), 3)
    def card(rev):
        im = blank(); d = ImageDraw.Draw(im); n = len(lad); y0 = 70; step = min(115, 560//n)
        for j, w in enumerate(lad):
            y = y0 + j*step
            hl = j == i
            d.rounded_rectangle((CW/2 - 170, y, CW/2 + 170, y + step - 18), 18, fill=(GREEN if rev else (255, 245, 205)) if hl else (232, 240, 255), outline=DARK, width=4)
            d.text((CW/2, y + (step - 18)/2 + 2), (w if (rev or not hl) else "? ? ? ?"), font=font(54), fill=("white" if rev else RED) if hl else DARK, anchor="mm")
        d.text((CW/2, CH - 70), "change ONE letter at each step", font=font(36), fill=GREY, anchor="mm")
        return im
    o, k = shuffle_opts(r, ans.title(), [w.title() for w in wrong])
    return dict(q=card(False), a=card(True), options=o, correct=k, question="WHAT'S THE MISSING WORD?", banner=f"{ans}!", catch=False)

# 32. HIDDEN ANIMAL
HIDDEN = [("My robot terribly broke down.", "Otter", "robOT TERribly"), ("A crab bit my toe!", "Rabbit", "cRAB BIT"),
          ("Get milk; it tends to run out.", "Kitten", "milK IT TENds"), ("Hide errors in the code.", "Deer", "hiDE ERrors")]
DECOY = ["Tiger", "Horse", "Mouse", "Camel", "Goat", "Snake", "Sheep", "Panda", "Zebra", "Wolf"]
def hidden_word(seed, level):
    r = random.Random(seed); sent, ans, how = r.choice(HIDDEN); flat = re.sub("[^a-z]", "", sent.lower())
    wrong = [w for w in r.sample(DECOY, len(DECOY)) if w.lower() not in flat][:3]
    def card(rev):
        im = blank(); d = ImageDraw.Draw(im); paste_c(im, em("🔍", 120), CW/2, 120)
        text_block(im, f"“{sent}”", 340, 62)
        if rev: explain(im, how, y=CH - 120, col=GREEN, size=56)
        else: d.text((CW/2, CH - 120), "an animal is hiding across the words", font=font(36), fill=GREY, anchor="mm")
        return im
    o, k = shuffle_opts(r, ans, wrong)
    return dict(q=card(False), a=card(True), options=o, correct=k, question="FIND THE HIDDEN ANIMAL!", banner=f"{ans.upper()}!", catch=False)

# 33. EMOJI REBUS
REBUS = [("⭐", "🐟", "Starfish", ["Goldfish", "Sunfish", "Shellfish"]), ("☀️", "🌸", "Sunflower", ["Starlight", "Sunshine", "Wildflower"]),
         ("🐄", "👦", "Cowboy", ["Bullseye", "Farmboy", "Cowbell"]), ("🦶", "⚽", "Football", ["Footstep", "Handball", "Kickoff"]),
         ("🧈", "🪰", "Butterfly", ["Dragonfly", "Buttercup", "Firefly"]), ("🥚", "🌱", "Eggplant", ["Eggshell", "Houseplant", "Sprout"])]
def rebus(seed, level):
    r = random.Random(seed); a, b, ans, wrong = r.choice(REBUS)
    def card(rev):
        im = blank(); d = ImageDraw.Draw(im); y = 300
        paste_c(im, em(a, 230), CW/2 - 230, y); d.text((CW/2, y), "+", font=font(140), fill=DARK, anchor="mm"); paste_c(im, em(b, 230), CW/2 + 230, y)
        if rev: d.text((CW/2, 600), ans.upper(), font=font(90), fill=GREEN, anchor="mm")
        else: d.text((CW/2, 600), "= ?", font=font(90), fill=RED, anchor="mm")
        return im
    o, k = shuffle_opts(r, ans, wrong)
    return dict(q=card(False), a=card(True), options=o, correct=k, question="WHAT WORD IS THIS?", banner=f"{ans.upper()}!", catch=False)

# 34. WORD SEARCH
WS = ["PLANET", "ROCKET", "GARDEN", "DRAGON", "PIRATE", "CASTLE", "MONKEY", "PENCIL", "GUITAR", "SPIDER", "WIZARD", "TURTLE"]
def word_search(seed, level):
    r = random.Random(seed); n = 7
    dirs = [(1, 0), (0, 1)] if level == 0 else [(1, 0), (0, 1), (1, 1), (-1, 0), (0, -1)]
    def present(G, w):
        for y in range(n):
            for x in range(n):
                for dx, dy in [(1, 0), (0, 1), (1, 1), (-1, 0), (0, -1), (-1, -1), (1, -1), (-1, 1)]:
                    if all(0 <= x + dx*i < n and 0 <= y + dy*i < n and G[y + dy*i][x + dx*i] == ch for i, ch in enumerate(w)): return (x, y, dx, dy)
        return None
    while True:
        ans = r.choice(WS); dx, dy = r.choice(dirs); L = len(ans)
        x0 = r.randrange(n) ; y0 = r.randrange(n)
        if not all(0 <= x0 + dx*i < n and 0 <= y0 + dy*i < n for i in range(L)): continue
        G = [[r.choice("ABCDEFGHIKLMNOPRSTUW") for _ in range(n)] for _ in range(n)]
        for i, ch in enumerate(ans): G[y0 + dy*i][x0 + dx*i] = ch
        wrong = r.sample([w for w in WS if w != ans], 3)
        if all(present(G, w) is None for w in wrong) and present(G, ans): break
    pos = present(G, ans)
    def card(rev):
        im = blank(); d = ImageDraw.Draw(im); cs = 92; gx = (CW - n*cs)/2; gy = 40
        if rev:
            x, y, ddx, ddy = pos; p0 = (gx + (x + 0.5)*cs, gy + (y + 0.5)*cs); p1 = (gx + (x + ddx*(len(ans) - 1) + 0.5)*cs, gy + (y + ddy*(len(ans) - 1) + 0.5)*cs)
            d.line((p0, p1), fill=(255, 225, 90), width=74); d.ellipse((p0[0] - 37, p0[1] - 37, p0[0] + 37, p0[1] + 37), fill=(255, 225, 90)); d.ellipse((p1[0] - 37, p1[1] - 37, p1[0] + 37, p1[1] + 37), fill=(255, 225, 90))
        for yy in range(n):
            for xx in range(n): d.text((gx + (xx + 0.5)*cs, gy + (yy + 0.5)*cs + 2), G[yy][xx], font=font(54), fill=DARK, anchor="mm")
        d.text((CW/2, CH - 50), "only ONE of the answers is hidden in the grid", font=font(32), fill=GREY, anchor="mm")
        return im
    o, k = shuffle_opts(r, ans.title(), [w.title() for w in wrong])
    return dict(q=card(False), a=card(True), options=o, correct=k, question="WHICH WORD IS HIDDEN?", banner=f"{ans}!", catch=False)

# 35. NO VOWELS
VW = ["BANANA", "MONKEY", "PIZZA", "TOMATO", "PUZZLE", "RAINBOW", "COOKIE", "PENGUIN", "UNICORN", "ELEPHANT", "AVOCADO", "OCTOPUS"]
def skel(w): return re.sub("[AEIOU]", "", w)
def vowelless(seed, level):
    r = random.Random(seed)
    while True:
        ans = r.choice(VW); wrong = r.sample([w for w in VW if w != ans and skel(w) != skel(ans)], 3)
        if len(skel(ans)) >= 3: break
    def card(rev):
        im = blank(); d = ImageDraw.Draw(im); s_ = " ".join(skel(ans))
        d.rounded_rectangle((80, 180, CW - 80, 400), 30, fill=(232, 240, 255), outline=DARK, width=5)
        d.text((CW/2, 290), s_, font=font(110 if len(s_) < 12 else 84), fill=DARK, anchor="mm")
        if rev: d.text((CW/2, 520), ans, font=font(90), fill=GREEN, anchor="mm")
        else: d.text((CW/2, 520), "all the vowels are gone!", font=font(42), fill=GREY, anchor="mm")
        return im
    o, k = shuffle_opts(r, ans.title(), [w.title() for w in wrong])
    return dict(q=card(False), a=card(True), options=o, correct=k, question="WHAT'S THE WORD?", banner=f"{ans}!", catch=False)

# 36. KEYBOARD MEMORY
ROWS = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]
def keyboard(seed, level):
    r = random.Random(seed); ri = r.choice([0, 1] if level == 0 else [1, 2]); row = ROWS[ri]; qi = r.randrange(1, len(row) - 1); ans = row[qi]
    def card(rev):
        im = blank(); d = ImageDraw.Draw(im); ks = 82; y0 = 180
        for j, rw in enumerate(ROWS):
            x0 = (CW - len(ROWS[0])*ks)/2 + j*ks*0.45
            for i, ch in enumerate(rw):
                x = x0 + i*ks; y = y0 + j*(ks + 14); target = (j == ri and i == qi)
                show = (j == ri) or rev
                d.rounded_rectangle((x + 4, y, x + ks - 4, y + ks), 12, fill=((GREEN if rev else (255, 245, 205)) if target else ((245, 246, 252) if show else (225, 228, 238))), outline=DARK, width=3)
                if target: d.text((x + ks/2, y + ks/2 + 2), ans if rev else "?", font=font(42), fill=("white" if rev else RED), anchor="mm")
                elif show: d.text((x + ks/2, y + ks/2 + 2), ch, font=font(38), fill=DARK, anchor="mm")
        d.text((CW/2, 600), "you type on it every day...", font=font(38), fill=GREY, anchor="mm")
        return im
    o, k = shuffle_opts(r, ans, r.sample([c for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if c != ans and c not in row], 3))
    return dict(q=card(False), a=card(True), options=o, correct=k, question="WHICH KEY IS MISSING?", banner=f"{ans}!", catch=False)

# 37. COUNT THE LETTER (classic F trap)
LC = [("FINISHED FILES ARE THE RESULT OF YEARS OF SCIENTIFIC STUDY COMBINED WITH THE EXPERIENCE OF YEARS.", "F"),
      ("THE FASTEST FOX OF ALL FOUND FIVE OF HIS FRIENDS AT THE FAIR.", "F")]
def letter_count(seed, level):
    r = random.Random(seed); s_, L = LC[0] if level >= 1 else LC[1]; ans = s_.count(L)
    def card(rev):
        im = blank(); d = ImageDraw.Draw(im)
        f = font(50); words_ = s_.split(); lines = [""]
        for w in words_:
            t = (lines[-1] + " " + w).strip()
            if d.textlength(t, font=f) < CW - 120: lines[-1] = t
            else: lines.append(w)
        y = 160
        for ln in lines:
            x = CW/2 - d.textlength(ln, font=f)/2
            for ch in ln:
                col = (231, 76, 60) if (rev and ch == L) else DARK
                if rev and ch == L: d.rounded_rectangle((x - 3, y - 34, x + d.textlength(ch, font=f) + 3, y + 30), 8, fill=(255, 230, 120))
                d.text((x, y), ch, font=f, fill=col, anchor="lm"); x += d.textlength(ch, font=f)
            y += 78
        if rev: explain(im, "most people miss the F in every 'OF'!", y=CH - 80, col=RED, size=40)
        else: d.text((CW/2, CH - 80), f"count every {L}, read it once", font=font(38), fill=GREY, anchor="mm")
        return im
    o, k = shuffle_opts(r, str(ans), [str(ans - 3), str(ans - 2), str(ans + 1)])
    return dict(q=card(False), a=card(True), options=o, correct=k, question=f"HOW MANY {L}'S ARE THERE?", banner=f"{ans} {L}'S!", catch=True)

# 38. FLAGS
FLAGS = {"Ireland": ("v", [(22, 155, 96), (255, 255, 255), (255, 136, 62)]), "Ivory Coast": ("v", [(247, 127, 0), (255, 255, 255), (0, 158, 96)]),
         "Italy": ("v", [(0, 146, 70), (255, 255, 255), (206, 43, 55)]), "France": ("v", [(0, 35, 149), (255, 255, 255), (237, 41, 57)]),
         "Germany": ("h", [(0, 0, 0), (221, 0, 0), (255, 206, 0)]), "Netherlands": ("h", [(174, 28, 40), (255, 255, 255), (33, 70, 139)]),
         "Russia": ("h", [(255, 255, 255), (0, 57, 166), (213, 43, 30)]), "Belgium": ("v", [(0, 0, 0), (253, 218, 36), (239, 51, 64)])}
def flags(seed, level):
    r = random.Random(seed)
    ans, wrong = (r.choice(["Italy", "France", "Germany"]), None) if level == 0 else ("Ireland", ["Ivory Coast", "Italy", "India"])
    if wrong is None: wrong = r.sample([k for k in FLAGS if k != ans and k not in ("Ivory Coast",)], 3)
    kind, cols = FLAGS[ans]
    def card(rev):
        im = blank(); d = ImageDraw.Draw(im); x0, y0, w, h = CW/2 - 300, 110, 600, 400
        for i, c in enumerate(cols):
            if kind == "v": d.rectangle((x0 + i*w/3, y0, x0 + (i + 1)*w/3, y0 + h), fill=c)
            else: d.rectangle((x0, y0 + i*h/3, x0 + w, y0 + (i + 1)*h/3), fill=c)
        d.rectangle((x0, y0, x0 + w, y0 + h), outline=DARK, width=6); d.rectangle((x0 - 30, y0 - 20, x0 - 14, y0 + h + 120), fill=(120, 120, 135))
        if rev and level >= 1: explain(im, "green on the POLE side = Ireland, orange = Ivory Coast", y=CH - 90, col=PURPLE, size=32)
        return im
    o, k = shuffle_opts(r, ans, wrong)
    return dict(q=card(False), a=card(True), options=o, correct=k, question="WHICH COUNTRY'S FLAG IS THIS?", banner=f"{ans.upper()}!", catch=level >= 1)

# 39. ANIMAL RECORDS
ANIM = [("Which animal is the BIGGEST that ever lived?", "Blue whale", ["T-Rex", "Elephant", "Megalodon"], ["🐋", "🦖", "🐘", "🦈"], "blue whales beat every dinosaur"),
        ("Which land animal is the FASTEST?", "Cheetah", ["Lion", "Horse", "Greyhound"], ["🐆", "🦁", "🐎", "🐕"], "cheetahs hit about 110 km/h")]
def animal(seed, level):
    r = random.Random(seed); q, ans, wrong, es, why = ANIM[0] if level >= 1 else ANIM[1]
    def card(rev):
        im = blank(); n = len(es)
        for i, e in enumerate(es): paste_c(im, em(e, 150), 130 + i*(CW - 260)/(n - 1), 180)
        text_block(im, q, 430, 58)
        if rev: explain(im, why, y=CH - 80, col=PURPLE, size=40)
        return im
    o, k = shuffle_opts(r, ans, wrong)
    return dict(q=card(False), a=card(True), options=o, correct=k, question="ANIMAL RECORDS!", banner=f"{ans.upper()}!", catch=level >= 1)

# 40. PLANETS
PL = [("Mercury", (170, 160, 150), 18), ("Venus", (230, 190, 110), 30), ("Earth", (70, 140, 220), 32), ("Mars", (210, 90, 60), 24),
      ("Jupiter", (220, 170, 120), 70), ("Saturn", (230, 200, 140), 60), ("Uranus", (150, 220, 230), 44), ("Neptune", (70, 100, 220), 42)]
def planets(seed, level):
    r = random.Random(seed)
    if level >= 1: q, ans, wrong, why, catch = "Which planet is the HOTTEST?", "Venus", ["Mercury", "Mars", "Jupiter"], "Venus: its thick clouds trap the heat", True
    else: q, ans, wrong, why, catch = "Which planet is the BIGGEST?", "Jupiter", ["Saturn", "Neptune", "Earth"], "Jupiter is over 11× wider than Earth", False
    def card(rev):
        im = blank(); d = ImageDraw.Draw(im)
        d.ellipse((-260, 60, 60, 380), fill=(255, 200, 60)); x = 90
        for nm, c, s in PL:
            x += s + 12; d.ellipse((x - s, 220 - s, x + s, 220 + s), fill=c, outline=(GREEN if rev and nm == ans else DARK), width=6 if rev and nm == ans else 2)
            if nm == "Saturn": d.ellipse((x - s*1.5, 220 - s*0.35, x + s*1.5, 220 + s*0.35), outline=(180, 150, 100), width=4)
            x += s + 12
        text_block(im, q, 470, 60)
        if rev: explain(im, why, y=CH - 80, col=PURPLE, size=38)
        return im
    o, k = shuffle_opts(r, ans, wrong)
    return dict(q=card(False), a=card(True), options=o, correct=k, question="SPACE QUIZ!", banner=f"{ans.upper()}!", catch=catch)

# 41. BEST DEAL
def best_deal(seed, level):
    r = random.Random(seed)
    while True:
        packs = []
        for _ in range(4):
            n = r.choice([1, 2, 3, 4, 5, 6]); unit = r.choice([1.40, 1.45, 1.50, 1.55, 1.60, 1.35]); packs.append((n, round(n*unit, 2)))
        per = [p/n for n, p in packs]
        if len(set(n for n, _ in packs)) >= 3 and sorted(per)[1] - sorted(per)[0] >= 0.04: break
    k = per.index(min(per))
    def card(rev):
        im = blank(); d = ImageDraw.Draw(im)
        for i, (n, p) in enumerate(packs):
            x = 125 + i*237; y = 330
            d.rounded_rectangle((x - 105, 90, x + 105, 560), 26, fill=(220, 250, 225) if (rev and i == k) else SOFT, outline=GREEN if (rev and i == k) else (200, 205, 222), width=8 if (rev and i == k) else 4)
            for j in range(n): paste_c(im, em("🥤", 56), x - 50 + (j % 3)*50, 160 + (j//3)*70)
            d.text((x, 360), f"{n} for", font=font(40), fill=DARK, anchor="mm"); d.text((x, 420), f"${p:.2f}", font=font(52), fill=RED, anchor="mm")
            if rev: d.text((x, 500), f"${p/n:.2f} each", font=font(30), fill=PURPLE, anchor="mm")
            d.ellipse((x - 30, 590, x + 30, 650), fill=GREEN if (rev and i == k) else BADGE[i]); d.text((x, 620), "ABCD"[i], font=font(34), fill="white", anchor="mm")
        d.text((CW/2, CH - 60), "cheapest PER DRINK wins", font=font(36), fill=GREY, anchor="mm")
        return im
    return dict(q=card(False), a=card(True), options=[f"Pack {c}" for c in "ABCD"], correct=k, question="WHICH IS THE BEST DEAL?", banner=f"PACK {'ABCD'[k]}!", catch=False)

# 42. VENN DIAGRAM
def venn(seed, level):
    r = random.Random(seed)
    while True:
        both = r.randint(3, 8); a = both + r.randint(4, 12); b = both + r.randint(4, 12); none_ = r.randint(2, 9); tot = a + b - both + none_
        if tot <= 40: break
    def card(rev):
        im = blank(); d = ImageDraw.Draw(im)
        d.rounded_rectangle((60, 40, CW - 60, 470), 30, outline=DARK, width=5)
        d.ellipse((160, 90, 540, 440), outline=(231, 76, 60), width=10); d.ellipse((420, 90, 800, 440), outline=(52, 120, 219), width=10)
        paste_c(im, em("🍕", 80), 260, 150); paste_c(im, em("🍔", 80), 700, 150)
        if rev:
            d.text((300, 280), str(a - both), font=font(56), fill=DARK, anchor="mm"); d.text((480, 280), str(both), font=font(56), fill=PURPLE, anchor="mm")
            d.text((660, 280), str(b - both), font=font(56), fill=DARK, anchor="mm"); d.text((130, 420), str(none_), font=font(56), fill=GREEN, anchor="mm")
        else:
            d.text((480, 280), str(both), font=font(56), fill=PURPLE, anchor="mm"); d.text((130, 420), "?", font=font(60), fill=RED, anchor="mm")
        text_block(im, f"{tot} kids:  {a} like pizza,  {b} like burgers,  {both} like BOTH.  How many like NEITHER?", 590, 40)
        if rev: explain(im, f"{tot} − ({a} + {b} − {both}) = {none_}", y=CH - 50, col=GREEN, size=40)
        return im
    o, k = shuffle_opts(r, str(none_), [str(tot - a - b), str(none_ + both), str(none_ - 1 if none_ > 1 else none_ + 2), str(none_ + 1)])
    return dict(q=card(False), a=card(True), options=o, correct=k, question="READ THE DIAGRAM!", banner=f"{none_} KIDS!", catch=False)

# 43. BAR CHART (truncated axis trap)
def bar_chart(seed, level):
    r = random.Random(seed); days = ["Mon", "Tue", "Wed", "Thu", "Fri"]
    base = r.choice([40, 50, 60]); lo = base; hi = base + r.choice([10, 20])
    vals = [r.randint(lo + 1, hi - 1) for _ in days]; i_lo = r.randrange(5); i_hi = r.choice([i for i in range(5) if i != i_lo])
    vals[i_lo] = lo + 2; vals[i_hi] = hi
    axis0 = lo
    ratio = vals[i_hi]/vals[i_lo]; ans = f"{ratio:.1f}×"; looks = (vals[i_hi] - axis0)/(vals[i_lo] - axis0)
    def card(rev):
        im = blank(); d = ImageDraw.Draw(im); x0, y0, W_, H_ = 140, 50, 720, 420
        for t in range(axis0, hi + 1, 5 if hi - axis0 <= 20 else 10):
            y = y0 + H_ - (t - axis0)/(hi - axis0)*H_; d.line((x0, y, x0 + W_, y), fill=(220, 222, 232), width=2); d.text((x0 - 14, y), str(t), font=font(30), fill=DARK, anchor="rm")
        for i, v in enumerate(vals):
            x = x0 + 30 + i*(W_ - 60)/5; h = (v - axis0)/(hi - axis0)*H_
            c = (231, 76, 60) if i == i_hi else ((52, 120, 219) if i == i_lo else (170, 175, 195))
            d.rectangle((x, y0 + H_ - h, x + (W_ - 60)/5 - 30, y0 + H_), fill=c)
            d.text((x + ((W_ - 60)/5 - 30)/2, y0 + H_ + 30), days[i], font=font(30), fill=DARK, anchor="mm")
            if rev: d.text((x + ((W_ - 60)/5 - 30)/2, y0 + H_ - h - 24), str(v), font=font(30), fill=DARK, anchor="mm")
        d.line((x0, y0, x0, y0 + H_), fill=DARK, width=5); d.line((x0, y0 + H_, x0 + W_, y0 + H_), fill=DARK, width=5)
        text_block(im, f"{days[i_hi]} sold how many TIMES more than {days[i_lo]}?", CH - 175, 40)
        if rev: explain(im, f"{vals[i_hi]} ÷ {vals[i_lo]} = {ratio:.2f}: the axis starts at {axis0}, not 0!", y=CH - 100, col=RED, size=32)
        return im
    w1 = f"{min(4, max(2, round(looks)))}.0×"
    wrong = [w1, f"{ratio + 0.5:.1f}×", "3.0×", "2.0×", f"{max(1.1, ratio - 0.1):.1f}×"]
    o, k = shuffle_opts(r, ans, [w for w in dict.fromkeys(wrong) if w != ans])
    return dict(q=card(False), a=card(True), options=o, correct=k, question="READ THE CHART CAREFULLY!", banner=f"ONLY {ans}!", catch=True)

# 44. CODE OUTPUT
def code_output(seed, level):
    r = random.Random(seed)
    if level >= 2:
        a, b = r.sample(range(2, 10), 2)
        lines = [f'x = "{a}"', f'y = "{b}"', "print(x + y)"]; ans = f"{a}{b}"; wrong = [str(a + b), f"{b}{a}", "error"]
        why = "they're TEXT, so + glues them together"; catch = True
    else:
        x = r.randint(2, 5); n = r.randint(2, 3); m = r.choice([2, 3])
        lines = [f"x = {x}", f"repeat {n} times:", f"    x = x * {m}", "print(x)"]; ans = str(x*m**n); wrong = list(dict.fromkeys(w for w in [str(x*m*n), str(x + m*n), str(x*m**(n - 1)), str(x*m**(n + 1)), str(x**n)] if w != ans))
        why = f"{x} × {m}" + f" × {m}"*(n - 1) + f" = {ans}"; catch = False
    def card(rev):
        im = blank(); d = ImageDraw.Draw(im)
        d.rounded_rectangle((90, 70, CW - 90, 520), 28, fill=(30, 32, 48))
        for j, c in enumerate(((255, 95, 86), (255, 189, 46), (39, 201, 63))): d.ellipse((120 + j*34, 96, 142 + j*34, 118), fill=c)
        for i, ln in enumerate(lines):
            d.text((140, 170 + i*80), ln, font=mono(52), fill=(220, 230, 255), anchor="lm")
        if rev: d.text((140, 470), f"> {ans}", font=mono(52), fill=(120, 230, 140), anchor="lm"); explain(im, why, y=CH - 120, col=PURPLE, size=36)
        else: d.text((CW/2, CH - 120), "what gets printed?", font=font(40), fill=GREY, anchor="mm")
        return im
    o, k = shuffle_opts(r, ans, wrong)
    return dict(q=card(False), a=card(True), options=o, correct=k, question="WHAT DOES THE CODE PRINT?", banner=f"{ans}!", catch=catch)

# 45. MORSE CODE
MORSE = {"A": ".-", "C": "-.-.", "D": "-..", "E": ".", "G": "--.", "N": "-.", "O": "---", "S": "...", "T": "-", "U": "..-", "W": ".--", "I": "..", "M": "--", "R": ".-."}
MW = ["SUN", "DOG", "CAT", "SOS", "WIN", "RED", "NET", "MOM", "TEN"]
def morse(seed, level):
    r = random.Random(seed); ans = r.choice([w for w in MW if all(c in MORSE for c in w)])
    letters = sorted(set(ans) | set(r.sample([c for c in MORSE if c not in ans], 5 - len(set(ans)) + 3)))[:8]
    wrong = [w for w in MW if w != ans and all(c in letters for c in w)]
    while len(wrong) < 3:
        cand = "".join(r.sample(letters, 3))
        if cand != ans and cand not in wrong: wrong.append(cand)
    wrong = r.sample(wrong, 3)
    def sym(d, code, x, y, s=1.0):
        for ch in code:
            if ch == ".": d.ellipse((x, y - 9*s, x + 18*s, y + 9*s), fill=DARK); x += 32*s
            else: d.rounded_rectangle((x, y - 8*s, x + 52*s, y + 8*s), 8, fill=DARK); x += 66*s
        return x
    def card(rev):
        im = blank(); d = ImageDraw.Draw(im)
        for i, c in enumerate(letters):
            x = 70 + (i % 2)*430; y = 70 + (i//2)*62
            d.text((x, y), c, font=font(40), fill=PURPLE, anchor="lm"); sym(d, MORSE[c], x + 60, y, 0.8)
        d.rounded_rectangle((60, 340, CW - 60, 520), 26, fill=(255, 245, 205), outline=DARK, width=4)
        x = 100
        for ci, c in enumerate(ans):
            x0 = x; x = sym(d, MORSE[c], x, 410, 1.0)
            if rev: d.text(((x0 + x - 20)/2, 480), c, font=font(44), fill=GREEN, anchor="mm")
            x += 50
        d.text((CW/2, CH - 70), "decode the message using the key", font=font(34), fill=GREY, anchor="mm")
        return im
    o, k = shuffle_opts(r, ans, wrong)
    return dict(q=card(False), a=card(True), options=o, correct=k, question="DECODE THE MORSE!", banner=f"{ans}!", catch=False)

GENS = dict(word_ladder=word_ladder, hidden_word=hidden_word, rebus=rebus, word_search=word_search, vowelless=vowelless, keyboard=keyboard,
            letter_count=letter_count, flags=flags, animal=animal, planets=planets, best_deal=best_deal, venn=venn, bar_chart=bar_chart,
            code_output=code_output, morse=morse)
