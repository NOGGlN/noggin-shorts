"""Render one Noggin Brick Race video (two balls, every bounce adds a brick, first one walled in loses; see bricks.py).

Usage:  python3 make_bricks.py bricks_races/race_YYYY_MM_DD.py YYYY-MM-DD [--stills]
The race file defines THEME (short unique id), HEADLINE = ("LINE 1.", "LINE 2."), PLAYERS = [(name, emoji), (name, emoji)],
TITLE (hook, 1 emoji, under 60 chars), CAPTION (Instagram/TikTok text) and optionally SEED.
Refuses a THEME already in data/used_bricks.json, writes videos/<date>/bricks-1.mp4 + bricks_manifest.json,
appends the theme to used_bricks.json and saves a check sheet to /tmp/bricks_check_<date>.png.
"""
import json, os, sys, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import bricks

def load(path):
    spec = importlib.util.spec_from_file_location("b", path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

if __name__ == "__main__":
    path, date = sys.argv[1], sys.argv[2]; stills = "--stills" in sys.argv
    b = load(path); assert len(b.PLAYERS) == 2, "exactly 2 players"
    (n1, e1), (n2, e2) = b.PLAYERS; assert n1 != n2 and e1 != e2 and len(n1) <= 14 and len(n2) <= 14, "2 different players, names <= 14 chars"
    lp = os.path.join(HERE, "data", "used_bricks.json"); used = json.load(open(lp)) if os.path.exists(lp) else []
    if not stills and any(u["theme"] == b.THEME for u in used): raise SystemExit(f"DUPLICATE theme already used: {b.THEME}")
    seed0 = getattr(b, "SEED", 1); race = bricks.find_race(seed0)
    race["loser_slot"] = race["seeds"][0] % 2                     # which ring loses comes from the seed, not from us
    out = os.path.join(HERE, "..", "videos", date); os.makedirs(out, exist_ok=True); mp4 = os.path.join(out, "bricks-1.mp4")
    end = race["end"]
    if stills:
        bricks.render(b.PLAYERS, b.HEADLINE, race, mp4, stills=[0.3, end*0.5, end - 0.5, end + 0.6, end + 3.5]); print("stills in", out, "end", round(end, 1)); sys.exit()
    dur = bricks.render(b.PLAYERS, b.HEADLINE, race, mp4, sheet=f"/tmp/bricks_check_{date}.png")
    winner = b.PLAYERS[1 - race["loser_slot"]][0]
    man = [dict(n=1, file="bricks-1.mp4", url=f"https://raw.githubusercontent.com/NOGGlN/noggin-shorts/main/videos/{date}/bricks-1.mp4",
                title=b.TITLE, caption=b.CAPTION, theme=b.THEME, winner=winner, seeds=list(race["seeds"]), seconds=round(dur, 1))]
    json.dump(man, open(os.path.join(out, "bricks_manifest.json"), "w"), ensure_ascii=False, indent=1)
    used.append(dict(date=date, theme=b.THEME, winner=winner)); json.dump(used, open(lp, "w"), ensure_ascii=False, indent=1)
    print("done", mp4, round(dur, 1), "s, winner:", winner, "| check sheet:", f"/tmp/bricks_check_{date}.png")
