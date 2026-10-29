"""Render one Noggin Battle video (ball battle royale, see battle.py).

Usage:  python3 make_battle.py battles/battle_YYYY_MM_DD.py YYYY-MM-DD [--stills]
The battle file defines THEME (short unique id), HEADLINE = ("LINE 1.", "LINE 2."), CONTESTANTS = [(name, emoji), ...] (16-30),
TITLE (hook, 1 emoji, under 60 chars) and CAPTION (Instagram/TikTok text).
Refuses a THEME already in data/used_battles.json, writes videos/<date>/battle-1.mp4 + battle_manifest.json,
appends the theme to used_battles.json and saves a check sheet to /tmp/battle_check_<date>.png.
"""
import json, os, sys, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import battle

def load(path):
    spec = importlib.util.spec_from_file_location("b", path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

if __name__ == "__main__":
    path, date = sys.argv[1], sys.argv[2]; stills = "--stills" in sys.argv
    b = load(path); n = len(b.CONTESTANTS); assert 12 <= n <= 30, "12-30 contestants"
    names = [c[0] for c in b.CONTESTANTS]; assert len(set(names)) == n, "duplicate contestant"
    for nm, e in b.CONTESTANTS: assert e and len(nm) <= 16, f"name too long or emoji missing: {nm}"
    lp = os.path.join(HERE, "data", "used_battles.json"); used = json.load(open(lp)) if os.path.exists(lp) else []
    if not stills and any(u["theme"] == b.THEME for u in used): raise SystemExit(f"DUPLICATE theme already used: {b.THEME}")
    r = 44 if n > 24 else 50 if n > 18 else 56
    run = battle.find_run(n, r, seed0=getattr(b, "SEED", 1))
    out = os.path.join(HERE, "..", "videos", date); os.makedirs(out, exist_ok=True); mp4 = os.path.join(out, "battle-1.mp4")
    if stills:
        battle.render(b.CONTESTANTS, b.HEADLINE, run, r, mp4, stills=[0.3, 3.5, run["end"]*0.5, run["end"] + 3.0]); print("stills in", out); sys.exit()
    dur = battle.render(b.CONTESTANTS, b.HEADLINE, run, r, mp4, sheet=f"/tmp/battle_check_{date}.png")
    winner = b.CONTESTANTS[run["winner"]][0]
    man = [dict(n=1, file="battle-1.mp4", url=f"https://raw.githubusercontent.com/NOGGlN/noggin-shorts/main/videos/{date}/battle-1.mp4",
                title=b.TITLE, caption=b.CAPTION, theme=b.THEME, winner=winner, seed=run["seed"], seconds=round(dur, 1))]
    json.dump(man, open(os.path.join(out, "battle_manifest.json"), "w"), ensure_ascii=False, indent=1)
    used.append(dict(date=date, theme=b.THEME, winner=winner)); json.dump(used, open(lp, "w"), ensure_ascii=False, indent=1)
    print("done", mp4, round(dur, 1), "s, winner:", winner, "| check sheet:", f"/tmp/battle_check_{date}.png")
