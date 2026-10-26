"""Batch-7: Gen-Z-tuned puzzles + trivia (sample set)."""
import math, random
from PIL import Image, ImageDraw, ImageFilter
from render import font, DARK
from v3 import blank, GREEN
from puzzles4 import shuffle_opts, num_wrong, explain, em, paste_c, BADGE, RED, PURPLE, GREY, SOFT, CW, CH
from puzzles5 import text_block
from mascot import mascot, OUTL

HAIR = (70, 45, 30)
def noggin_hair(style, s=2.0):
    """Noggin wearing a haircut. Canvas 320x350 at s=1 -> scaled."""
    S = 2; W_, H_ = 420, 420; ox, oy = 50, 60   # mascot pasted at (ox, oy) in a larger canvas
    back = Image.new("RGBA", (W_*S, H_*S), (0, 0, 0, 0)); d = ImageDraw.Draw(back)
    def P(x, y): return ((ox + x)*S, (oy + y)*S)
    def E(x0, y0, x1, y1, **k): d.ellipse((*P(x0, y0), *P(x1, y1)), **k)
    if style == "Afro":
        for x, y, r in [(160, 70, 120), (70, 110, 70), (250, 110, 70), (100, 40, 70), (220, 40, 70), (160, 10, 70)]:
            E(x - r, y - r, x + r, y + r, fill=HAIR, outline=OUTL, width=5*S)
    if style == "Mullet":
        d.polygon([P(50, 110), P(270, 110), P(292, 205), P(270, 245), P(50, 245), P(28, 205)], fill=HAIR)
        for x in range(40, 290, 26): d.polygon([P(x, 240), P(x + 26, 240), P(x + 13, 262)], fill=HAIR)
    m = mascot("idle", (0, 0), False).resize((320*S, 350*S), Image.LANCZOS)
    back.alpha_composite(m, (ox*S, oy*S))
    d = ImageDraw.Draw(back)
    if style == "Mohawk":
        for i, x in enumerate(range(115, 215, 20)):
            h = 95 + 25*math.sin(i)
            d.polygon([P(x - 14, 70), P(x + 14, 70), P(x + 4, 70 - h)], fill=(240, 60, 120), outline=OUTL)
        d.rounded_rectangle((*P(110, 52), *P(210, 82)), 12*S, fill=(240, 60, 120))
    if style == "Mullet":
        d.chord((*P(42, 40), *P(278, 200)), 180, 360, fill=HAIR, outline=OUTL, width=5*S)
        for x in range(60, 262, 25): d.polygon([P(x, 118), P(x + 25, 118), P(x + 12, 140)], fill=HAIR)
    if style == "Man bun":
        d.chord((*P(42, 40), *P(278, 200)), 180, 360, fill=HAIR, outline=OUTL, width=5*S)
        E(125, -20, 195, 50, fill=HAIR, outline=OUTL, width=5*S); d.rounded_rectangle((*P(140, 42), *P(180, 54)), 6*S, fill=(240, 60, 120))
    if style == "Buzz cut":
        d.chord((*P(44, 44), *P(276, 196)), 180, 360, fill=(120, 95, 80), outline=OUTL, width=4*S)
        r = random.Random(3)
        for _ in range(160):
            a = r.uniform(math.pi, 2*math.pi); rr = r.uniform(0, 1); x = 160 + math.cos(a)*110*rr**0.5; y = 120 + math.sin(a)*70*rr**0.5
            d.ellipse((*P(x - 1.5, y - 1.5), *P(x + 1.5, y + 1.5)), fill=(70, 50, 40))
    if style == "Afro":
        pass
    if style == "Bowl cut":
        d.chord((*P(38, 30), *P(282, 230)), 180, 360, fill=HAIR, outline=OUTL, width=5*S); d.rectangle((*P(40, 128), *P(280, 140)), fill=HAIR)
    out = back.resize((int(W_*s/2*2/2*2/2*1.0*s/s*1), int(H_*s/2*2/2*2/2*1.0*s/s*1)), Image.LANCZOS) if False else back.resize((int(W_*s*0.5), int(H_*s*0.5)), Image.LANCZOS)
    return out

STYLES = ["Mullet", "Mohawk", "Man bun", "Buzz cut", "Afro", "Bowl cut"]
def haircut(seed, level):
    r = random.Random(seed); ans = r.choice(["Mullet", "Mohawk", "Man bun"]); wrong = r.sample([s for s in STYLES if s != ans], 3)
    def card(rev):
        im = blank(); d = ImageDraw.Draw(im); n = noggin_hair(ans, 2.9); paste_c(im, n, CW/2, 420)
        d.text((CW/2, 60), "Noggin got a fresh cut ✂", font=font(42), fill=PURPLE, anchor="mm") if False else d.text((CW/2, 100), "Noggin got a fresh cut", font=font(42), fill=PURPLE, anchor="mm")
        if rev: explain(im, {"Mullet": "business in the front, party in the back", "Mohawk": "a spiky strip right down the middle", "Man bun": "all the hair tied up in a bun"}[ans], y=CH - 60, col=GREEN, size=38)
        return im
    o, k = shuffle_opts(r, ans, wrong)
    return dict(q=card(False), a=card(True), options=o, correct=k, question="NAME THIS HAIRCUT!", banner=f"THE {ans.upper()}!", catch=False, trivia=True)

GAMES = [("⛏️", "🧱", "🧟", "Minecraft", ["Roblox", "Fortnite", "Terraria"]), ("🍄", "👨", "🏰", "Super Mario", ["Zelda", "Sonic", "Pac-Man"]),
         ("🟦", "🟨", "🟥", "Tetris", ["Candy Crush", "Minecraft", "Pac-Man"]), ("🐦", "😠", "🐷", "Angry Birds", ["Flappy Bird", "Among Us", "Pokémon"])]
def emoji_game(seed, level):
    r = random.Random(seed); a, b, c, ans, wrong = r.choice(GAMES)
    def card(rev):
        im = blank(); d = ImageDraw.Draw(im)
        for i, e in enumerate((a, b, c)): paste_c(im, em(e, 190), CW/2 + (i - 1)*270, 300)
        d.text((CW/2, 560), ans.upper() if rev else "= ?", font=font(84), fill=GREEN if rev else RED, anchor="mm")
        d.text((CW/2, 110), "guess the game from 3 emojis", font=font(38), fill=GREY, anchor="mm")
        return im
    o, k = shuffle_opts(r, ans, wrong)
    return dict(q=card(False), a=card(True), options=o, correct=k, question="NAME THE GAME!", banner=f"{ans.upper()}!", catch=False, trivia=True)

def group_dm(seed, level):
    r = random.Random(seed); n = r.choice([5, 6, 7]); ans = n*(n - 1); half = ans//2
    def card(rev):
        im = blank(); d = ImageDraw.Draw(im); cx, cy, R = CW/2, 265, 190
        pts = [(cx + R*math.cos(2*math.pi*i/n - math.pi/2), cy + R*math.sin(2*math.pi*i/n - math.pi/2)) for i in range(n)]
        if rev:
            for i in range(n):
                for j in range(i + 1, n): d.line((pts[i], pts[j]), fill=(170, 200, 255), width=4)
        faces = ["😎", "🤓", "😏", "🥳", "😴", "🤠", "🙃"]
        for p, f_ in zip(pts, faces): paste_c(im, em(f_, 100), *p)
        paste_c(im, em("💬", 90), cx, cy)
        text_block(im, f"{n} friends. Everyone sends ONE private DM to every other friend. How many DMs in total?", 565, 40)
        if rev: explain(im, f"{n} × {n - 1} = {ans}  (you to them AND them to you!)", y=CH - 40, col=RED, size=34)
        return im
    o, k = shuffle_opts(r, ans, [half, n*n, ans - n] + num_wrong(r, ans, (2, 4)))
    return dict(q=card(False), a=card(True), options=[str(x) for x in o], correct=k, question="COUNT THE DMs!", banner=f"{ans} DMs!", catch=True)

GENS = dict(haircut=haircut, emoji_game=emoji_game, group_dm=group_dm)
