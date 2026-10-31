"""Render one cinematic "news you missed" Short (news6.py) for a day. YouTube only.

Usage:  python3 make_news6.py days/news_YYYY_MM_DD.py YYYY-MM-DD [--stills]
The day file has NEWS = [one edition dict] (same fields as news6.py expects: items with text/detail/vo/photo/credit/
explain_photo/explain_credit/source, briefs as a list of pages, title, description, optional vo_open/vo_outro/cats).
- Refuses stories or briefs already in data/used_news.json, checks every photo exists and is big enough.
- Writes videos/<date>/news.mp4 + news_manifest.json ([{file, url, title, description, seconds}]),
  appends the stories and the briefs actually shown to data/used_news.json, saves a check sheet next to the video.
"""
import importlib.util, json, os, re, sys
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import news6

RAW = "https://raw.githubusercontent.com/NOGGlN/noggin-shorts/main/videos/{date}/{file}"
def norm(s): return re.sub(r"\W+", " ", s.lower()).strip()

if __name__ == "__main__":
    path, date = sys.argv[1], sys.argv[2]; stills = "--stills" in sys.argv
    sp = importlib.util.spec_from_file_location("day", path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
    assert len(m.NEWS) == 1, "one edition per day"
    ed = m.NEWS[0]; assert ed.get("title") and ed.get("description"), "title + description needed"
    lp = os.path.join(HERE, "data", "used_news.json"); used = json.load(open(lp)) if os.path.exists(lp) else []
    seen = {norm(u["text"]) for u in used} | {u.get("link") for u in used if u.get("link")}
    items = ed["items"]; assert 2 <= len(items) <= 3, "2 or 3 real stories"
    briefs = [b for pg in ed["briefs"] for b in pg] if ed["briefs"] and isinstance(ed["briefs"][0], list) else ed["briefs"]
    small = []
    for it in items + briefs:
        for k in ("photo", "explain_photo"):
            if it.get(k):
                p = os.path.join(HERE, it[k]); assert os.path.exists(p), f"missing photo {it[k]}"
                w, h = Image.open(p).size
                if max(w, h) < 1200: small.append(f"{it[k]} ({w}x{h})")
    for it in items:
        link = it["source"]["link"]; assert link.startswith("http"), f"story needs a full source link: {it['text']}"
        if not stills and (norm(it["text"]) in seen or link in seen): raise SystemExit(f"DUPLICATE story already used: {it['text']}")
    out = os.path.join(HERE, "..", "videos", date); os.makedirs(out, exist_ok=True); mp4 = os.path.join(out, "news.mp4")
    if small: print("WARNING: small photos will look soft full-screen:", ", ".join(small))
    dur = news6.render(ed, mp4, stills)
    if stills: sys.exit()
    man = [dict(file="news.mp4", url=RAW.format(date=date, file="news.mp4"), title=ed["title"], description=ed["description"], seconds=round(dur, 1))]
    json.dump(man, open(os.path.join(out, "news_manifest.json"), "w"), ensure_ascii=False, indent=1)
    for it in items: used.append(dict(date=date, text=it["text"], real=True, link=it["source"]["link"], kind="story"))
    for b in briefs: used.append(dict(date=date, text=b["title"], real=True, link=b["source"]["link"], kind="brief"))
    json.dump(used, open(lp, "w"), ensure_ascii=False, indent=1)
    print("done", mp4, round(dur, 1), "s | manifest + used_news updated")
