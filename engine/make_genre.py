"""Render one Noggin video in one of the three YouTube formats: Would You Rather, Battle Royale, Satisfying Bounce.

Usage:  python3 make_genre.py genre_days/YYYY_MM_DD_<kind>.json YYYY-MM-DD [--stills]
The JSON spec: {"kind": "wyr"|"royale"|"bounce", "format": "video"|"short", "id": "<unique id>", "title": ..., "description": ...,
                plus the kind's own fields (see engine/genres/wyr.py, royale.py, bounce.py)}.
- format "video" = 1920x1080 regular YouTube video; "short" = 1080x1920 YouTube Short (must stay under 60 s).
- Refuses ids/questions/themes already used (data/used_wyr.json, data/used_battles.json, data/used_bounce.json).
- Writes videos/<date>/<kind>-<format>.mp4, adds/updates its entry in videos/<date>/genre_manifest.json,
  logs it as used, and saves a check sheet to /tmp/genre_check_<date>_<kind>.jpg.
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "genres"))
import gcommon as g
from PIL import Image

RAW = "https://raw.githubusercontent.com/NOGGlN/noggin-shorts/main/videos/{date}/{file}"

def loadj(p, d): return json.load(open(p)) if os.path.exists(p) else d
def norm(s): return " ".join(s.upper().split())

if __name__ == "__main__":
    path, date = sys.argv[1], sys.argv[2]; stills = "--stills" in sys.argv
    spec = json.load(open(path)); kind, fmt = spec["kind"], spec["format"]
    assert kind in ("wyr", "royale", "bounce") and fmt in ("video", "short")
    for f in ("id", "title", "description"): assert spec.get(f), f"missing {f}"
    if fmt == "short": g.set_size(1080, 1920)
    data = os.path.join(HERE, "data")
    # ---- no repeats
    if kind == "wyr":
        up = os.path.join(data, "used_wyr.json"); used = loadj(up, [])
        keys = {norm(" ".join(q["a"])) for u in used for q in [u]} | {norm(" ".join(u["b"])) for u in used}
        Q = spec["questions"]; assert (3 if fmt == "short" else 8) <= len(Q) <= (4 if fmt == "short" else 14), "short: 3-4 questions, video: 8-14"
        for q in Q:
            assert q["pick"] in (0, 1) and q["ae"] and q["be"] and q["why"], f"incomplete question {q}"
            for side in ("a", "b"):
                if not stills and norm(" ".join(q[side])) in keys: raise SystemExit(f"DUPLICATE option already used: {q[side]}")
    elif kind == "royale":
        up = os.path.join(data, "used_battles.json"); used = loadj(up, [])
        if not stills and any(u["theme"] == spec["id"] for u in used): raise SystemExit(f"DUPLICATE battle theme: {spec['id']}")
        C = spec["contestants"]; assert 12 <= len(C) <= 24 and len({c[0] for c in C}) == len(C) and len({c[1] for c in C}) == len(C)
        for nm, e in C: assert e and len(nm) <= 14, f"name too long or emoji missing: {nm}"
    else:
        up = os.path.join(data, "used_bounce.json"); used = loadj(up, [])
        if not stills and any(u["id"] == spec["id"] for u in used): raise SystemExit(f"DUPLICATE bounce id: {spec['id']}")
    mod = __import__({"wyr": "wyr", "royale": "royale", "bounce": "bounce"}[kind])
    frame, audio, dur, still_times, info = mod.build(spec, fmt)
    if fmt == "short": assert dur < 59.5, f"short too long: {dur:.1f}s"
    out = os.path.join(HERE, "..", "videos", date); os.makedirs(out, exist_ok=True)
    fname = f"{kind}-{fmt}.mp4"; mp4 = os.path.join(out, fname)
    # ---- check sheet
    ims = [frame(t).convert("RGB") for t in still_times]; tw = 640 if fmt == "video" else 360; th = int(tw*g.H/g.W)
    sheet = Image.new("RGB", (tw*min(3, len(ims)), th*((len(ims) + 2)//3)))
    for i, im in enumerate(ims): sheet.paste(im.resize((tw, th)), ((i % 3)*tw, (i//3)*th))
    sp = f"/tmp/genre_check_{date}_{kind}.jpg"; sheet.save(sp, quality=85)
    if stills: print("check sheet:", sp, info); sys.exit()
    wav = f"/tmp/genre_{date}_{kind}.wav"; audio(wav); g.render(frame, dur, wav, mp4)
    mp = os.path.join(out, "genre_manifest.json"); man = [m for m in loadj(mp, []) if m["file"] != fname]
    man.append(dict(file=fname, url=RAW.format(date=date, file=fname), kind=kind, format=fmt, id=spec["id"], title=spec["title"],
                    description=spec["description"], seconds=round(dur, 1), **info))
    json.dump(man, open(mp, "w"), ensure_ascii=False, indent=1)
    if kind == "wyr": used += [dict(date=date, a=q["a"], b=q["b"]) for q in spec["questions"]]
    elif kind == "royale": used.append(dict(date=date, theme=spec["id"], winner=info.get("winner")))
    else: used.append(dict(date=date, id=spec["id"]))
    json.dump(used, open(up, "w"), ensure_ascii=False, indent=1)
    print("done", mp4, round(dur, 1), "s", info, "| check sheet:", sp)
