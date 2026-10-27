"""Render one day's Real-or-Fake news Shorts (max 2 per day).

Usage:  python3 make_news.py days/news_YYYY_MM_DD.py YYYY-MM-DD
The day module defines NEWS = [ dict(title=<YouTube title>, items=[...3 items as in news2.py...], description=<text>), ... ]
(1 or 2 entries). Photos live in assets/photos/<date>/ . Every real item needs a source with a full "link".
Checks every story against data/used_news.json (no repeats), renders videos/<date>/news-N.mp4,
writes videos/<date>/news_manifest.json, appends the stories to data/used_news.json,
and saves a check sheet of key frames to /tmp/news_check_<date>.png.
"""
import json, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import news2

def norm(t): return re.sub(r"[^a-z0-9 ]", "", t.lower()).strip()

if __name__ == "__main__":
    path, date = sys.argv[1], sys.argv[2]
    day = news2.load(path); assert 1 <= len(day.NEWS) <= 2, "1 or 2 news videos per day"
    lp = os.path.join(HERE, "data", "used_news.json"); used = json.load(open(lp)) if os.path.exists(lp) else []
    seen = {norm(u["text"]) for u in used} | {u.get("link", "") for u in used if u.get("link")}
    out = os.path.join(HERE, "..", "videos", date); os.makedirs(out, exist_ok=True)
    new, manifest, frames = [], [], []
    for n, v in enumerate(day.NEWS, 1):
        items = v["items"]; assert len(items) == 3 and any(not i["real"] for i in items) and any(i["real"] for i in items)
        for it in items:
            assert ("source" in it) == it["real"] and ("fix" in it) == (not it["real"]), it
            for k in ("photo", "explain_photo", "fix_photo"):
                if it.get(k): assert os.path.exists(os.path.join(HERE, it[k])), f"missing photo {it[k]}"
            link = it.get("source", {}).get("link", "")
            if it["real"]: assert link.startswith("http"), f"real story needs a full source link: {it['text']}"
            if norm(it["text"]) in seen or (link and link in seen): raise SystemExit(f"DUPLICATE story already used: {it['text']}")
            seen.add(norm(it["text"])); seen.add(link)
            new.append(dict(date=date, text=it["text"], real=it["real"], link=link))
        fn = f"news-{n}.mp4"; mp4 = os.path.join(out, fn); wav = mp4 + ".wav"
        news2.make_audio(items, getattr(day, "MUSIC", None), wav); segs, total = news2.make_video(items, mp4, wav); os.remove(wav)
        for s in segs:
            for tt in (s["vote"] + 0.8, s["reveal"] + 0.3, s["explain"] + 1.5):
                frames.append((mp4, tt))
        manifest.append(dict(n=n, file=fn, url=f"https://raw.githubusercontent.com/NOGGlN/noggin-shorts/main/videos/{date}/{fn}",
                             title=(v["title"] if "#shorts" in v["title"] else v["title"] + " #shorts")[:100],
                             description=v["description"], answers=["REAL" if i["real"] else "FAKE" for i in items]))
        print("done", fn, round(total, 1), "s", flush=True)
    from PIL import Image
    sheet = Image.new("RGB", (9*240, len(day.NEWS)*427), "grey")
    for k, (mp4, tt) in enumerate(frames):
        png = f"/tmp/_nf_{k}.png"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", str(tt), "-i", mp4, "-frames:v", "1", "-vf", "scale=240:-1", png], check=True)
        sheet.paste(Image.open(png), ((k % 9)*240, (k//9)*427)); os.remove(png)
    sheet.save(f"/tmp/news_check_{date}.png"); print("check sheet:", f"/tmp/news_check_{date}.png")
    json.dump(manifest, open(os.path.join(out, "news_manifest.json"), "w"), ensure_ascii=False, indent=1)
    json.dump(used + new, open(lp, "w"), ensure_ascii=False, indent=1)
    print("manifest:", os.path.join(out, "news_manifest.json"))
