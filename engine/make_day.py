"""Render one day of Noggin Shorts.

Usage:  python3 make_day.py days/day_2026_10_29.py 2026-10-29

The day module must define:
  PLAN = [ ((easy_gen, medium_gen, hard_gen), "File Title", "YouTube title with emoji"), ... ]   # usually 7 entries
  GENS = {name: generator(seed, level) -> puzzle dict}   (use helpers from puzzles8: trivia(), scene_q())
Each name must be NEW: it is checked against data/used_questions.json (question text + answer).
Writes videos/<date>/NN-slug.mp4 and videos/<date>/manifest.json, renders a check sheet to /tmp/check_<date>.png,
and appends the used questions to data/used_questions.json.
"""
import importlib.util, json, os, re, sys
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import v5
v5.LIMITS = [8.5, 8.5, 7.0]; v5.HOOK_FIRST = True
from puzzles8 import tag

# hook line shown over the level-1 question from frame 0 (no intro card). A day file may set HOOK_LINES = [one per video].
HOOKS = ["99% FAIL LEVEL 3", "ONLY 1 IN 10 GETS THIS", "ONLY 2% REACH LEVEL 3", "NOBODY PASSES LEVEL 3", "BET YOU MISS LEVEL 3"]
DESC = ("3 levels: Easy 8.5s, Medium 8.5s, Hard 7s. Keep score and comment it 👇 Did Noggin distract you? 🍅\n\n"
        "#shorts #puzzle #trivia #brainteaser #quiz #genz #noggin #brainteasers")

def slug(s): return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

def load(path):
    spec = importlib.util.spec_from_file_location("day", path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def throws_for(v, seed):
    import random
    r = random.Random(seed + v); l1 = "screen" if r.random() < 0.6 else None; l2 = "strip" if r.random() < 0.5 else None
    if r.random() < 0.2: l1 = l2 = None
    elif not (l1 or l2): l1 = "screen"
    return [l1, l2, None]

def build(day, v, seed):
    names = day.PLAN[v - 1][0]; ps = []
    for lv, nm in enumerate(names):
        P = day.GENS[nm](seed + v*97 + lv*19, lv)
        if P.get("trivia") and nm in ("haircut", "emoji_game"): tag(P["q"]); tag(P["a"])
        ps.append(P)
    for P, th in zip(ps, throws_for(v, seed)): P["throw"] = th
    return ps

def job(args):
    path, date, v, seed, out = args
    day = load(path); v5.LIMITS = [8.5, 8.5, 7.0]; v5.HOOK_FIRST = True
    v5.HOOK_LINE = day.HOOK_LINES[v - 1] if hasattr(day, "HOOK_LINES") else HOOKS[(v + seed) % len(HOOKS)]
    ps = build(day, v, seed); fn = f"{v:02d}-{slug(day.PLAN[v - 1][1])}.mp4"; wav = f"/tmp/noggin_{date}_{v}.wav"
    v5.make_sfx(ps, wav); v5.make_video(ps, os.path.join(out, fn), wav); os.remove(wav)
    return v, fn, [P["options"][P["correct"]] for P in ps]

if __name__ == "__main__":
    path, date = sys.argv[1], sys.argv[2]; seed = int(date.replace("-", "")) % 100000
    day = load(path); out = os.path.join(HERE, "..", "videos", date); os.makedirs(out, exist_ok=True)
    ledger_p = os.path.join(HERE, "data", "used_questions.json")
    used = json.load(open(ledger_p)) if os.path.exists(ledger_p) else []
    seen = {u["question"].strip().lower() for u in used}
    # validate + duplicate check + contact sheet
    from PIL import Image
    sheet = Image.new("RGB", (6*320, len(day.PLAN)*267), "grey"); new_entries = []
    for v in range(1, len(day.PLAN) + 1):
        for lv, (nm, P) in enumerate(zip(day.PLAN[v - 1][0], build(day, v, seed))):
            assert len(P["options"]) == 4 and len(set(P["options"])) == 4, (nm, P["options"])
            q = (P.get("qtext") or f"{nm}: {P['question']} -> {P['options'][P['correct']]}").strip()
            if q.lower() in seen: raise SystemExit(f"DUPLICATE question already used before: {q}")
            seen.add(q.lower()); new_entries.append(dict(date=date, gen=nm, question=q, answer=P["options"][P["correct"]]))
            for j, key in enumerate(("q", "a")):
                im = P[key].resize((320, 267)); sheet.paste(im, ((lv*2 + j)*320, (v - 1)*267), im)
    sheet.save(f"/tmp/check_{date}.png"); print("check sheet:", f"/tmp/check_{date}.png")
    with Pool(2) as pool:
        res = sorted(pool.imap_unordered(job, [(path, date, v, seed, out) for v in range(1, len(day.PLAN) + 1)]))
    manifest = []
    for v, fn, ans in res:
        names, short, yt = day.PLAN[v - 1]
        manifest.append(dict(n=v, file=fn, url=f"https://raw.githubusercontent.com/NOGGlN/noggin-shorts/main/videos/{date}/{fn}",
                             title=(yt + " #shorts")[:100], description=DESC, answers=ans))
        print("done", v, fn, ans, flush=True)
    json.dump(manifest, open(os.path.join(out, "manifest.json"), "w"), ensure_ascii=False, indent=1)
    json.dump(used + new_entries, open(ledger_p, "w"), ensure_ascii=False, indent=1)
    print("manifest:", os.path.join(out, "manifest.json"))
