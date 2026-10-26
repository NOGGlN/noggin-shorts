"""Batch-8: Gen-Z puzzles + trivia (random mix). Same dict contract."""
import math, random
from PIL import Image, ImageDraw
from render import font, DARK
from v3 import blank, GREEN
from puzzles4 import shuffle_opts, num_wrong, explain, em, paste_c, BADGE, RED, PURPLE, GREY, SOFT, CW, CH
from puzzles5 import text_block
import puzzles7 as P7

PINK = (240, 60, 140)
def tag(im, label="TRIVIA", col=PINK):
    d = ImageDraw.Draw(im); f = font(30); w = d.textlength(label, font=f)
    d.rounded_rectangle((CW/2 - w/2 - 24, 18, CW/2 + w/2 + 24, 66), 24, fill=col); d.text((CW/2, 43), label, font=f, fill="white", anchor="mm")

def trivia(q, ans, wrong, emojis, why, question, banner, catch=False, seed=0, esize=150):
    r = random.Random(seed)
    def card(rev):
        im = blank(); tag(im); n = len(emojis)
        for i, e in enumerate(emojis): paste_c(im, em(e, esize), CW/2 + (i - (n - 1)/2)*min(240, (CW - 200)/max(1, n - 1) if n > 1 else 0), 225)
        text_block(im, q, 460, 58)
        if rev: explain(im, why, y=CH - 80, col=PURPLE, size=38)
        return im
    o, k = shuffle_opts(r, ans, wrong)
    return dict(q=card(False), a=card(True), options=o, correct=k, question=question, banner=banner, catch=catch, trivia=True)

# ------------------------------- TRIVIA -------------------------------
def music_fact(s, lv): return trivia("Which artist released the album ÷ (Divide)?", "Ed Sheeran", ["Harry Styles", "Shawn Mendes", "Lewis Capaldi"],
                                     ["🎤", "🎸", "➗"], "Ed Sheeran, 2017: it has 'Shape of You' on it", "MUSIC TRIVIA!", "ED SHEERAN!", seed=s)
def banana(s, lv): return trivia("Which of these is a BERRY, scientifically?", "Banana", ["Strawberry", "Raspberry", "Blackberry"],
                                 ["🍌", "🍓", "🫐"], "bananas are berries, strawberries are NOT!", "FOOD FACTS!", "BANANA!", catch=True, seed=s)
def slang(s, lv): return trivia("What does 'GOAT' stand for?", "Greatest of All Time", ["Good at Online Tasks", "Got Owned Again Today", "Game Over, Ask Twice"],
                                ["🐐", "🏆"], "the GOAT = the best ever", "SLANG CHECK!", "GREATEST OF ALL TIME!", seed=s)
def swoosh(s, lv): return trivia("Which brand's logo is called the 'Swoosh'?", "Nike", ["Adidas", "Puma", "Vans"], ["👟", "✔️"],
                                 "the Nike Swoosh, designed in 1971", "BRAND TRIVIA!", "NIKE!", seed=s)
def afk(s, lv): return trivia("In gaming, what does 'AFK' mean?", "Away from keyboard", ["Always fighting kills", "Aim for kills", "Add friend kindly"],
                              ["🎮", "💤"], "AFK = you walked away mid-game", "GAMER SLANG!", "AWAY FROM KEYBOARD!", seed=s)
def snapchat(s, lv): return trivia("Which app has a GHOST as its logo?", "Snapchat", ["Instagram", "TikTok", "Discord"], ["👻", "📱"],
                                   "Snapchat's ghost even has a name: Ghostface Chillah", "APP TRIVIA!", "SNAPCHAT!", seed=s)
def octopus(s, lv): return trivia("How many HEARTS does an octopus have?", "3", ["1", "2", "8"], ["🐙", "❤️"],
                                  "3 hearts AND blue blood!", "ANIMAL FACTS!", "3 HEARTS!", catch=True, seed=s)
def emoji_meaning(s, lv): return trivia("Online, what does 🧢 usually mean?".replace("🧢", "the 'cap' emoji"), "That's a lie", ["I'm so cool", "Let's play sports", "I'm wearing a hat"],
                                        ["🧢", "🤥"], "'cap' = a lie, 'no cap' = for real", "EMOJI CHECK!", "IT MEANS A LIE!", seed=s)
def saturn(s, lv): return trivia("Which planet could FLOAT in a giant bathtub of water?", "Saturn", ["Jupiter", "Earth", "No planet can"], ["🪐", "🛁"],
                                 "Saturn is less dense than water!", "SPACE FACT!", "SATURN!", catch=True, seed=s)
def app_first(s, lv): return trivia("Which of these came out FIRST?", "YouTube", ["Instagram", "Snapchat", "TikTok"], ["▶️", "📸", "👻", "🎵"],
                                    "YouTube 2005, Instagram 2010, Snapchat 2011, TikTok 2016", "WHICH CAME FIRST?", "YOUTUBE!", seed=s, esize=120)
def phone_fact(s, lv): return trivia("The very first iPhone (2007) did NOT have...?", "An App Store", ["A touchscreen", "A camera", "A web browser"], ["📱", "🤔"],
                                     "the App Store only arrived in 2008", "TECH HISTORY!", "NO APP STORE!", catch=True, seed=s)
def fortnite(s, lv): return trivia("How many players drop into a classic Fortnite Battle Royale match?", "100", ["50", "64", "150"], ["🎮", "🪂", "🏝️"],
                                   "100 players, 1 winner", "GAMING TRIVIA!", "100 PLAYERS!", seed=s)
def gif(s, lv): return trivia("What does 'GIF' stand for?", "Graphics Interchange Format", ["Good Internet Fun", "Graphic Image File", "Great Instant Feed"],
                              ["🖼️", "🔁"], "invented back in 1987!", "INTERNET TRIVIA!", "GRAPHICS INTERCHANGE FORMAT!", seed=s)
def sunlight(s, lv): return trivia("Sunlight hitting your face right now left the Sun about how long ago?", "8 minutes", ["8 seconds", "8 hours", "No time at all"],
                                   ["☀️", "😎"], "light takes about 8 min 20 s to reach Earth", "SCIENCE FACT!", "8 MINUTES!", catch=True, seed=s)

# ------------------------------- PUZZLES -------------------------------
def scene_q(q, emojis, why, ans, wrong, question, banner, catch=False, seed=0, size=56, fmt=str):
    r = random.Random(seed)
    def card(rev):
        im = blank(); n = len(emojis)
        for i, e in enumerate(emojis): paste_c(im, em(e, 140), CW/2 + (i - (n - 1)/2)*230, 170)
        text_block(im, q, 450, size)
        if rev: explain(im, why, y=CH - 70, col=RED if catch else PURPLE, size=38)
        return im
    o, k = shuffle_opts(r, ans, wrong)
    return dict(q=card(False), a=card(True), options=[fmt(x) for x in o], correct=k, question=question, banner=banner, catch=catch)

def likes(s, lv):
    r = random.Random(s); a = r.choice([4, 5, 6]); m = 3; tot = sum(a*m**i for i in range(4))
    return scene_q(f"Your post gets {a} likes in hour 1. Every hour it gets 3× MORE than the hour before. Total likes after 4 hours?",
                   ["📱", "❤️", "📈"], " + ".join(str(a*m**i) for i in range(4)) + f" = {tot}", tot, [a*m**3, a*12, tot - a*m**3 + a*m**2], "COUNT THE LIKES!", f"{tot} LIKES!", seed=s, size=48)
def streak(s, lv):
    r = random.Random(s); x = r.choice([5, 10, 20]); ans = x*2**4
    return scene_q(f"Day 1 of your streak gives {x} XP. The XP DOUBLES every day. How much XP on day 5?", ["🔥", "🎮"],
                   f"{x} then {x*2}, {x*4}, {x*8}, {x*16}", ans, [x*5, x*8, x*10], "STREAK MATH!", f"{ans} XP!", catch=True, seed=s, size=52)
def rank_up(s, lv):
    r = random.Random(s); need = 1000; w, l = r.choice([(6, 4), (5, 3), (7, 5)]); have = w*150 - l*50; ans = need - have
    return scene_q(f"You need 1000 XP to rank up. A win = +150 XP, a loss = −50 XP. You go {w} wins, {l} losses. How much MORE XP do you need?",
                   ["🏆", "⬆️"], f"{w}×150 − {l}×50 = {have}, so 1000 − {have} = {ans}", ans, [ans + 100, ans - 100, ans + 50], "RANK UP!", f"{ans} XP!", seed=s, size=46)
def typing(s, lv):
    return scene_q("You type 60 words per minute. How long to type a 450-word essay?", ["⌨️", "📝"], "450 ÷ 60 = 7.5 minutes", "7 min 30 s",
                   ["4 min 50 s", "7 min 50 s", "45 min"], "TYPING SPEED!", "7 MIN 30 S!", seed=s)
def battery(s, lv):
    r = random.Random(s); start, loss, saver = r.choice([(95, 15, 20), (100, 20, 20), (90, 14, 20)]); ans = (start - saver)//loss
    return scene_q(f"Your phone is at {start}%. Gaming drains {loss}% per hour. Low-battery mode kicks in at {saver}%. After how many hours?",
                   ["🔋", "🎮"], f"({start} − {saver}) ÷ {loss} = {ans}", ans, [ans + 1, ans - 1, ans + 2], "BATTERY CHECK!", f"{ans} HOURS!", seed=s, size=50, fmt=lambda v: f"{v} hours")
def screen_time(s, lv):
    return scene_q("Your screen time is 4 h 30 min EVERY day. How much is that in one week?", ["📱", "📅"], "4.5 h × 7 = 31.5 h",
                   "31 h 30 min", ["28 h 30 min", "30 h", "31 h 50 min"], "SCREEN TIME!", "31.5 HOURS!", seed=s)
def split_bill(s, lv):
    r = random.Random(s); n = 4; food = r.choice([38, 42, 46]); dlv = 6; ans = (food + dlv)//n
    return scene_q(f"{n} friends order pizza for ${food} plus ${dlv} delivery. Split evenly, how much does each pay?", ["🍕", "👫"],
                   f"(${food} + ${dlv}) ÷ {n} = ${ans}", ans, [food//n, ans + 2, ans - 1], "SPLIT THE BILL!", f"${ans} EACH!", seed=s, fmt=lambda v: f"${v}")
def playlist(s, lv):
    return scene_q("Your playlist has 12 songs, each 3 min 20 s long. How long is it?", ["🎧", "🎶"], "12 × 200 s = 2400 s = 40 min",
                   "40 min", ["36 min", "38 min", "42 min"], "PLAYLIST MATH!", "40 MINUTES!", seed=s)
def download(s, lv):
    return scene_q("A game is 60 GB. You download at 100 MB per second. How long will it take?", ["🎮", "⬇️"], "60 GB = 60,000 MB, ÷ 100 = 600 s = 10 min",
                   "10 min", ["6 min", "1 min", "1 hour"], "DOWNLOAD TIME!", "10 MINUTES!", catch=True, seed=s)
def coin_streak(s, lv):
    return scene_q("You flipped a coin and got HEADS 5 times in a row. What's the chance the next flip is heads?", ["🪙", "🪙", "🪙"],
                   "the coin has no memory: still 50/50!", "50%", ["3%", "97%", "10%"], "COIN FLIP!", "STILL 50%!", catch=True, seed=s)

def notifications(s, lv):
    r = random.Random(s)
    items = [("Mia", "2 h ago", 120), ("Leo", "45 min ago", 45), ("Sam", "1 day ago", 1440), ("Zoe", "3 h ago", 180)]
    r.shuffle(items); ans = max(items, key=lambda x: x[2])[0]; apps = ["💬", "📸", "🎵", "👻"]
    def card(rev):
        im = blank(); d = ImageDraw.Draw(im)
        for i, (nm, t, m) in enumerate(items):
            y = 70 + i*140; hl = rev and nm == ans
            d.rounded_rectangle((80, y, CW - 80, y + 112), 30, fill=(220, 250, 225) if hl else (242, 244, 250), outline=GREEN if hl else (210, 214, 228), width=8 if hl else 3)
            paste_c(im, em(apps[i], 64), 150, y + 56); d.text((210, y + 38), nm, font=font(40), fill=DARK, anchor="lm")
            d.text((210, y + 80), "sent you a message", font=font(28), fill=GREY, anchor="lm"); d.text((CW - 110, y + 56), t, font=font(32), fill=PURPLE, anchor="rm")
        if rev: d.text((CW/2, CH - 90), "1 day ago is the OLDEST one", font=font(40), fill=GREEN, anchor="mm")
        else: d.text((CW/2, CH - 90), "Which message was sent FIRST?", font=font(44), fill=DARK, anchor="mm")
        return im
    o, k = shuffle_opts(r, ans, [n for n, _, _ in items if n != ans])
    return dict(q=card(False), a=card(True), options=o, correct=k, question="WHO TEXTED FIRST?", banner=f"{ans.upper()}!", catch=False)

def lock_pattern(s, lv):
    r = random.Random(s); P = {i: (i % 3, i//3) for i in range(9)}
    while True:
        path = [r.randrange(9)]; used = set(path)
        for _ in range(r.choice([3, 4])):
            c = r.choice([j for j in range(9) if j not in used]); path.append(c); used.add(c)
        full = [path[0]]
        for a, b in zip(path, path[1:]):
            (ax, ay), (bx, by) = P[a], P[b]
            if (ax + bx) % 2 == 0 and (ay + by) % 2 == 0:
                mid = ((ax + bx)//2) + 3*((ay + by)//2)
                if mid not in full: full.append(mid)
            if b not in full: full.append(b)
        if len(full) > len(path) and len(set(full)) == len(full): break
    ans = len(full)
    def card(rev):
        im = blank(); d = ImageDraw.Draw(im); g = 190; ox, oy = CW/2 - g, 140
        def C(i): return (ox + P[i][0]*g, oy + P[i][1]*g)
        d.rounded_rectangle((ox - 120, oy - 100, ox + 2*g + 120, oy + 2*g + 100), 50, fill=(30, 32, 48))
        d.line([C(i) for i in path], fill=(120, 200, 255), width=16, joint="curve")
        for i in range(9):
            x, y = C(i); hit = rev and i in full; corner = i in path
            d.ellipse((x - 26, y - 26, x + 26, y + 26), fill=(GREEN if hit else ((120, 200, 255) if corner else (90, 95, 120))))
            if rev and i in full: d.text((x, y + 2), str(full.index(i) + 1), font=font(28), fill="white", anchor="mm")
        if rev: d.text((CW/2, CH - 110), "a line that crosses a dot USES that dot too!", font=font(36), fill=RED, anchor="mm")
        else: d.text((CW/2, CH - 110), "How many dots does this unlock pattern use?", font=font(40), fill=DARK, anchor="mm")
        return im
    o, k = shuffle_opts(r, ans, [len(path), ans + 1, len(path) - 1 if len(path) - 1 != ans else ans + 2])
    return dict(q=card(False), a=card(True), options=[str(x) for x in o], correct=k, question="COUNT THE DOTS!", banner=f"{ans} DOTS!", catch=True)

W5 = ["CRANE", "SLATE", "PIZZA", "GHOST", "BRAIN", "PLANT", "STORM", "FLAME", "GRAPE", "SMILE", "TRAIN", "CLOUD", "BEACH", "HOUSE", "MUSIC",
      "PARTY", "LEMON", "TIGER", "ROBOT", "SNAKE", "QUEEN", "HEART", "SPACE", "DREAM", "LIGHT", "SHINE", "CHAIR", "STONE", "MOUSE", "CANDY"]
def score(g, a):
    res = ["x"]*5; pool = list(a)
    for i in range(5):
        if g[i] == a[i]: res[i] = "g"; pool.remove(g[i])
    for i in range(5):
        if res[i] == "x" and g[i] in pool: res[i] = "y"; pool.remove(g[i])
    return "".join(res)
def word_guess(s, lv):
    r = random.Random(s)
    for _ in range(5000):
        ans = r.choice(W5); g1, g2 = r.sample([w for w in W5 if w != ans], 2); f1, f2 = score(g1, ans), score(g2, ans)
        if f1.count("x") == 5 or f2.count("x") == 5: continue
        cons = [w for w in W5 if score(g1, w) == f1 and score(g2, w) == f2]
        if cons == [ans]:
            near = sorted([w for w in W5 if w not in (ans, g1, g2)], key=lambda w: -(score(g1, w) == f1) - (score(g2, w) == f2) - sum(c in w for c in set(ans))/5)
            wrong = near[:3]; break
    COL = {"g": (106, 170, 100), "y": (201, 180, 88), "x": (120, 124, 126)}
    def card(rev):
        im = blank(); d = ImageDraw.Draw(im); ts = 110; gx = (CW - 5*ts - 4*12)/2
        rows = [(g1, f1), (g2, f2)] + ([(ans, "ggggg")] if rev else [("?????", None)])
        for j, (w, f) in enumerate(rows):
            for i, ch in enumerate(w):
                x = gx + i*(ts + 12); y = 60 + j*(ts + 14)
                fill = COL[f[i]] if f else (255, 255, 255)
                d.rounded_rectangle((x, y, x + ts, y + ts), 10, fill=fill, outline=(200, 200, 210) if not f else None, width=4)
                d.text((x + ts/2, y + ts/2 + 3), ch, font=font(64), fill="white" if f else RED, anchor="mm")
        d.text((CW/2, 520), "green = right letter, right spot", font=font(32), fill=(80, 140, 75), anchor="mm")
        d.text((CW/2, 565), "yellow = in the word, wrong spot", font=font(32), fill=(160, 140, 50), anchor="mm")
        d.text((CW/2, 610), "grey = not in the word", font=font(32), fill=GREY, anchor="mm")
        return im
    o, k = shuffle_opts(r, ans.title(), [w.title() for w in wrong])
    return dict(q=card(False), a=card(True), options=o, correct=k, question="GUESS THE 5-LETTER WORD!", banner=f"{ans}!", catch=False)

GENS = dict(haircut=P7.haircut, emoji_game=P7.emoji_game, group_dm=P7.group_dm, music_fact=music_fact, banana=banana, slang=slang, swoosh=swoosh,
            afk=afk, snapchat=snapchat, octopus=octopus, emoji_meaning=emoji_meaning, saturn=saturn, app_first=app_first, phone_fact=phone_fact,
            fortnite=fortnite, gif=gif, sunlight=sunlight, likes=likes, streak=streak, rank_up=rank_up, typing=typing, battery=battery,
            screen_time=screen_time, split_bill=split_bill, playlist=playlist, download=download, coin_streak=coin_streak,
            notifications=notifications, lock_pattern=lock_pattern, word_guess=word_guess)
