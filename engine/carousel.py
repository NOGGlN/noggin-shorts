"""The Noggin Times as a swipeable photo carousel for Instagram (4:5, 1080x1350) and TikTok photo mode (9:16, 1080x1920).

Same data as the video (news_sampleN.py / a NEWS entry): items, briefs (one list or one list per page), hook.
Slides: 1 cover -> per story: headline + photo slide, then "the full story" slide -> In Brief slides (4 per slide)
-> Letters to the Editor (comment + follow).

Usage:  python3 carousel.py days/news_sample4.py out_dir/         (writes ig_01.jpg.. and tt_01.jpg..)
"""
import math, os, sys
from PIL import Image, ImageDraw, ImageOps
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import news4 as N
from news4 import F, INK, RED, GREY, PAPER, MEAS, wrap, fit_lines, halftone, tape, stamp, ink_mascot, load_photo
from news2 import load

M = 60; CW = 1080 - 2*M

def paper(h, seed=1):
    N.H = h; return N.make_paper(seed)

def big_masthead(pg, issue, date_txt):
    N.masthead(pg, issue, date_txt)
    return 330

def mini_masthead(pg, issue, date_txt, label):
    d = ImageDraw.Draw(pg)
    d.text((M, 70), "The Noggin Times", font=F("frak", 64), fill=INK, anchor="lm")
    d.text((1080 - M, 58), date_txt.upper(), font=F("typer", 22), fill=INK, anchor="rm")
    d.text((1080 - M, 88), f"NO. {issue}", font=F("type", 22), fill=INK, anchor="rm")
    d.line((M, 118, 1080 - M, 118), fill=INK, width=4); d.line((M, 126, 1080 - M, 126), fill=INK, width=1)
    d.text((M, 160), label, font=F("type", 28), fill=RED, anchor="lm")
    return 190

def foot(pg, h, txt):
    d = ImageDraw.Draw(pg); d.line((M, h - 96, 1080 - M, h - 96), fill=INK, width=2)
    d.text((540, h - 60), txt, font=F("type", 26), fill=INK, anchor="mm")

def grain(pg, h, k=0):
    gl = N.grain_layers(1, seed=7 + k)[0]
    pg.alpha_composite(gl.crop((0, 0, 1080, h)))
    return pg.convert("RGB")

def photo_box(pg, photo, x, y, w, h, credit, seed=0, tape_it=True, cell=6, crop=None):
    src = photo
    if crop: src = src.crop(crop)
    pic = halftone(src, (w, h), cell=cell)
    sh = Image.new("RGBA", (w + 30, h + 30), (0, 0, 0, 0)); ImageDraw.Draw(sh).rectangle((15, 20, w + 15, h + 20), fill=(0, 0, 0, 60))
    from PIL import ImageFilter
    pg.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)), (x - 15, y - 15))
    pg.alpha_composite(pic, (x, y)); d = ImageDraw.Draw(pg); d.rectangle((x, y, x + w - 1, y + h - 1), outline=INK, width=3)
    if tape_it:
        t1, t2 = tape(seed=seed), tape(ang=35, seed=seed + 1)
        pg.alpha_composite(t1, (x - 50, y - 38)); pg.alpha_composite(t2, (x + w - t2.width + 50, y - 38))
    if credit: d.text((x, y + h + 10), "PHOTO: " + credit, font=F("ital", 22), fill=GREY)

def headline(pg, text, y, maxh, start=84, minsz=46):
    d = ImageDraw.Draw(pg); f, ls, lh = fit_lines(text, "head", CW, maxh, start, minsz=minsz)
    for l in ls: d.text((M, y), l, font=f, fill=INK); y += lh
    return y

def cover_slide(h, items, hook, issue, date_txt):
    pg = paper(h); y = big_masthead(pg, issue, date_txt); d = ImageDraw.Draw(pg)
    d.text((M, y + 22), "TODAY'S EDITION  |  EVERYTHING HERE REALLY HAPPENED", font=F("type", 26), fill=RED, anchor="lm")
    y = headline(pg, hook, y + 60, 260 if h > 1500 else 150, 84, 56) + 10
    d.line((M, y, 1080 - M, y), fill=INK, width=2); y += 30
    ph = int((h - 120 - y - 60) - 60 - 46 - sum(min(2, len(wrap(it["text"], F("body", 38), CW - 70)))*44 + 18 for it in items))
    first = load_photo(items[0]["photo"]); photo_box(pg, first, M, y, CW, ph, items[0]["credit"], seed=3)
    st = stamp("EXTRA!", 110 if h < 1500 else 140, ang=-9); pg.alpha_composite(st, (540 - st.width//2, y + ph//2 - st.height//2))
    y += ph + 60
    d.text((M, y), "INSIDE THIS ISSUE", font=F("type", 28), fill=INK); y += 46
    for k, it in enumerate(items):
        f, ls, lh = fit_lines(it["text"], "body", CW - 70, 90, 38, lh=1.15, minsz=28)
        d.text((M, y), f"{k + 1}", font=F("head", 52), fill=RED)
        for l in ls[:2]: d.text((M + 60, y + 6), l, font=f, fill=INK); y += lh
        y += 18
        if y > h - 200: break
    foot(pg, h, "SWIPE TO READ  >>")
    return grain(pg, h, 0)

def story_slides(h, it, i, n, issue, date_txt):
    out = []
    # A: headline + big photo + lead
    pg = paper(h, seed=2 + i); y = mini_masthead(pg, issue, date_txt, f"STORY {i + 1} OF {n}  |  THIS REALLY HAPPENED")
    y = headline(pg, it["text"], y + 20, 340 if h > 1500 else 270, 88, 52) + 10
    d = ImageDraw.Draw(pg); d.line((M, y, 1080 - M, y), fill=INK, width=2); y += 36
    lead_f = F("body", 44); lead = wrap(it["detail"], lead_f, CW); lead_h = len(lead)*54
    ph = h - 120 - y - 70 - lead_h - 30
    photo_box(pg, load_photo(it["photo"]), M, y, CW, ph, it["credit"], seed=10 + i)
    y += ph + 60
    for l in lead: d.text((M, y), l, font=lead_f, fill=INK); y += 54
    foot(pg, h, "THE FULL STORY  >>")
    out.append(grain(pg, h, 1 + 2*i))
    # B: the full story - NEW material only (no repeated headline or lead): by-the-numbers box, fine print, source, 2nd photo
    pg = paper(h, seed=3 + i); y = mini_masthead(pg, issue, date_txt, f"STORY {i + 1}  |  THE FULL STORY")
    d = ImageDraw.Draw(pg); y += 24
    nums = it.get("numbers") or []
    if nums:
        d.rectangle((M, y, 1080 - M, y + 52), fill=INK); d.text((540, y + 26), "BY THE NUMBERS", font=F("head", 34), fill=PAPER, anchor="mm"); y += 52
        cols = 2; rows = math.ceil(len(nums)/cols); cw2 = CW//cols; rh = 150 if h < 1500 else 190
        d.rectangle((M, y, 1080 - M, y + rows*rh), outline=INK, width=3)
        for k, (big, label) in enumerate(nums):
            cx, cy = M + (k % cols)*cw2, y + (k//cols)*rh
            if k % cols: d.line((cx, cy + 14, cx, cy + rh - 14), fill=INK, width=1)
            if k >= cols: d.line((cx + 14, cy, cx + cw2 - 14, cy), fill=INK, width=1)
            bf = F("head", 72 if h < 1500 else 86)
            while MEAS.textlength(big, font=bf) > cw2 - 40: bf = F("head", bf.size - 4)
            d.text((cx + cw2/2, cy + rh*0.40), big, font=bf, fill=RED, anchor="mm")
            lf = F("type", 22 if h < 1500 else 26); ll = wrap(label.upper(), lf, cw2 - 40)
            for j, l in enumerate(ll[:2]): d.text((cx + cw2/2, cy + rh*0.72 + j*28), l, font=lf, fill=INK, anchor="mm")
        y += rows*rh + 36
    body = it.get("body", "")
    bf = F("body", 32 if h < 1500 else 36); blh = int(bf.size*1.28)
    for para in body.split("\n"):
        for l in wrap(para.strip(), bf, CW): d.text((M, y), l, font=bf, fill=INK); y += blh
        y += 10
    src = it["source"]; y += 6
    d.line((M, y, 1080 - M, y), fill=INK, width=1); y += 16
    d.text((M, y), f"SOURCE: {src['outlet'].upper()}  -  {src['date'].upper()}", font=F("type", 26), fill=RED); y += 40
    fi, hl, hlh = fit_lines(f'"{src["headline"]}"', "ital", CW, 90, 30, lh=1.15, minsz=24)
    for l in hl: d.text((M, y), l, font=fi, fill=GREY); y += hlh
    d.text((M, y + 2), src["url"], font=F("typer", 26), fill=INK); y += 60
    room = h - 120 - y - 40
    if room > 170:
        p2 = it.get("explain_photo")
        if p2: photo_box(pg, load_photo(p2), M, y, CW, room, it.get("explain_credit", ""), seed=20 + i)
        else:
            im = load_photo(it["photo"]); w, hh = im.size
            photo_box(pg, im, M, y, CW, room, it["credit"], seed=20 + i, crop=(int(w*0.2), int(hh*0.2), int(w*0.9), int(hh*0.9)))
    foot(pg, h, "IN BRIEF  >>" if i == n - 1 else "NEXT STORY  >>")
    out.append(grain(pg, h, 2 + 2*i))
    return out

def brief_cell(pg, b, x, y, w, h):
    d = ImageDraw.Draw(pg); y0 = y
    d.text((x, y), b["cat"].upper(), font=F("type", 24), fill=RED); y += 34
    f, ls, lh = fit_lines(b["title"], "head", w, 100, 36, lh=1.1, minsz=26)
    for l in ls: d.text((x, y), l, font=f, fill=INK); y += lh
    y += 16
    tf = F("body", 26); tl = wrap(b["text"], tf, w)
    rest = len(tl)*31 + (34 if b.get("price") else 0) + 28
    ph = max(150, (y0 + h) - y - rest - 20)
    ph = min(ph, int(w*0.9))
    if b.get("photo"):
        src = load_photo(b["photo"]); g = ImageOps.grayscale(src); bgv = g.getpixel((2, 2))
        if bgv > 225:
            bb = g.point(lambda v: 255 if v < bgv - 18 else 0).getbbox()
            if bb:
                pw_, ph_ = bb[2] - bb[0], bb[3] - bb[1]; src = src.crop((max(0, bb[0] - pw_//10), max(0, bb[1] - ph_//10), min(src.width, bb[2] + pw_//10), min(src.height, bb[3] + ph_//10)))
                c = Image.new("RGB", (max(src.width, int(src.height*w/ph)), max(src.height, int(src.width*ph/w))), (bgv,)*3)
                c.paste(src, ((c.width - src.width)//2, (c.height - src.height)//2)); src = c
        pic = halftone(src, (w, ph), cell=4); pg.alpha_composite(pic, (x, y)); d.rectangle((x, y, x + w - 1, y + ph - 1), outline=INK, width=2)
        if b.get("credit"):
            cf = F("ital", 16); tw = MEAS.textlength(b["credit"], font=cf)
            d.rectangle((x + w - tw - 12, y + ph - 24, x + w - 2, y + ph - 2), fill=PAPER); d.text((x + w - 6, y + ph - 6), b["credit"], font=cf, fill=GREY, anchor="rs")
        y += ph + 12
    for l in tl: d.text((x, y), l, font=tf, fill=INK); y += 31
    if b.get("price"): d.text((x, y + 2), b["price"], font=F("type", 26), fill=INK); y += 34
    d.text((x, y + 2), f"Source: {b['source']['outlet']}, {b['source']['date']}", font=F("ital", 21), fill=GREY)

def _trim_white(src, w, ph):
    g = ImageOps.grayscale(src); bgv = g.getpixel((2, 2))
    if bgv > 225:
        bb = g.point(lambda v: 255 if v < bgv - 18 else 0).getbbox()
        if bb:
            pw_, ph_ = bb[2] - bb[0], bb[3] - bb[1]
            src = src.crop((max(0, bb[0] - pw_//10), max(0, bb[1] - ph_//10), min(src.width, bb[2] + pw_//10), min(src.height, bb[3] + ph_//10)))
            c = Image.new("RGB", (max(src.width, int(src.height*w/ph)), max(src.height, int(src.width*ph/w))), (bgv,)*3)
            c.paste(src, ((c.width - src.width)//2, (c.height - src.height)//2)); src = c
    return src

def price_tag(txt, sz=30):
    f = F("type", sz); tw = MEAS.textlength(txt, font=f)
    im = Image.new("RGBA", (int(tw + 50), sz + 26), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.polygon([(0, im.height/2), (16, 0), (im.width, 0), (im.width, im.height), (16, im.height)], fill=RED)
    d.ellipse((10, im.height/2 - 4, 18, im.height/2 + 4), fill=PAPER)
    d.text((30, im.height/2), txt, font=f, fill=PAPER, anchor="lm")
    return im.rotate(-3, expand=True, resample=Image.BICUBIC)

def brief_rows_slide(h, chunk, issue, date_txt, label):
    """Second In Brief style: one row per item - photo left, text right, red price tag."""
    pg = paper(h, seed=61); y = mini_masthead(pg, issue, date_txt, label); d = ImageDraw.Draw(pg)
    top = y + 20; bottom = h - 120; rh = (bottom - top)//len(chunk); pw = 380
    for k, b in enumerate(chunk):
        ry = top + k*rh
        if k: d.line((M, ry - 6, 1080 - M, ry - 6), fill=INK, width=1)
        ph = rh - 34
        if b.get("photo"):
            src = _trim_white(load_photo(b["photo"]), pw, ph)
            pic = halftone(src, (pw, ph), cell=4); pg.alpha_composite(pic, (M, ry + 8)); d.rectangle((M, ry + 8, M + pw - 1, ry + 8 + ph - 1), outline=INK, width=2)
            if b.get("credit"):
                cf = F("ital", 15); tw = MEAS.textlength(b["credit"], font=cf)
                d.rectangle((M + pw - tw - 12, ry + 8 + ph - 22, M + pw - 2, ry + 8 + ph - 2), fill=PAPER); d.text((M + pw - 6, ry + 8 + ph - 5), b["credit"], font=cf, fill=GREY, anchor="rs")
        tx = M + pw + 30; tw_ = 1080 - M - tx; ty = ry + 8
        d.text((tx, ty), b["cat"].upper(), font=F("type", 24), fill=RED); ty += 34
        f, ls, lh = fit_lines(b["title"], "head", tw_, 110 if h < 1500 else 130, 36 if h < 1500 else 42, lh=1.1, minsz=26)
        for l in ls: d.text((tx, ty), l, font=f, fill=INK); ty += lh
        ty += 8; tf = F("body", 25 if h < 1500 else 29)
        for l in wrap(b["text"], tf, tw_)[:4 if h < 1500 else 6]: d.text((tx, ty), l, font=tf, fill=INK); ty += int(tf.size*1.2)
        d.text((tx, ty + 4), f"Source: {b['source']['outlet']}, {b['source']['date']}", font=F("ital", 20), fill=GREY); ty += 34
        if b.get("price"):
            tag = price_tag(b["price"], 24 if h < 1500 else 30)
            if ty + tag.height < ry + rh - 4: pg.alpha_composite(tag, (tx - 4, ty))
            else:   # no room under the text: pin it on the photo, never wider than the photo
                sz = 24
                while tag.width > pw - 10 and sz > 14: sz -= 2; tag = price_tag(b["price"], sz)
                pg.alpha_composite(tag, (M - 6, ry + 8 + ph - tag.height - 26))
    foot(pg, h, "SWIPE  >>")
    return grain(pg, h, 50)

def brief_slides(h, briefs, issue, date_txt, start_k):
    out = []; chunks = [briefs[p:p + 4] for p in range(0, len(briefs), 4)]
    for ci, chunk in enumerate(chunks):
        label = f"IN BRIEF  |  {ci + 1} OF {len(chunks)}"
        if ci % 2 == 1:
            out.append(brief_rows_slide(h, chunk, issue, date_txt, label)); continue
        pg = paper(h, seed=40 + ci); y = mini_masthead(pg, issue, date_txt, label)
        d = ImageDraw.Draw(pg); top = y + 20; bottom = h - 120
        cw = (CW - 40)//2; chh = (bottom - top - 40)//2
        d.line((M + cw + 20, top, M + cw + 20, bottom - 10), fill=INK, width=1); d.line((M, top + chh + 20, 1080 - M, top + chh + 20), fill=INK, width=1)
        for k, b in enumerate(chunk):
            brief_cell(pg, b, M + (k % 2)*(cw + 40), top + (k//2)*(chh + 40), cw, chh)
        foot(pg, h, "SWIPE  >>")
        out.append(grain(pg, h, 30 + ci))
    return out

def outro_slide(h, n, issue, date_txt):
    pg = paper(h, seed=99); y = mini_masthead(pg, issue, date_txt, "LETTERS TO THE EDITOR")
    y = headline(pg, "Which story was the craziest?", y + 30, 300, 104, 70) + 10
    d = ImageDraw.Draw(pg); d.line((M, y, 1080 - M, y), fill=INK, width=2); y += 40
    nums = ", ".join(str(k + 1) for k in range(n - 1)) + f" or {n}"
    for l in wrap(f"Write your answer in the comments: {nums}.", F("body", 46), CW): d.text((M, y), l, font=F("body", 46), fill=INK); y += 56
    d.text((M, y + 10), "Save this edition and send it to a friend.", font=F("ital", 42), fill=GREY); y += 90
    e = ink_mascot(size=(380, 415) if h > 1500 else (300, 328)); pg.alpha_composite(e, (540 - e.width//2, y + 20)); y += e.height + 40
    d.text((540, y), "- The Editor", font=F("ital", 44), fill=INK, anchor="mm")
    foot(pg, h, "FOLLOW FOR TOMORROW'S EDITION")
    return grain(pg, h, 77)

def make_carousel(items, briefs, hook, out_dir, prefix, h, issue=1, date_txt="Wednesday, October 28, 2026"):
    os.makedirs(out_dir, exist_ok=True)
    flat = [b for pg in briefs for b in pg] if briefs and isinstance(briefs[0], (list, tuple)) else list(briefs or [])
    slides = [cover_slide(h, items, hook or f"{len(items)} things that actually happened", issue, date_txt)]
    for i, it in enumerate(items): slides += story_slides(h, it, i, len(items), issue, date_txt)
    if flat: slides += brief_slides(h, flat, issue, date_txt, len(slides))
    slides.append(outro_slide(h, len(items), issue, date_txt))
    paths = []
    for k, s in enumerate(slides, 1):
        p = os.path.join(out_dir, f"{prefix}_{k:02d}.jpg"); s.save(p, quality=90); paths.append(p)
    N.H = 1920
    return paths

if __name__ == "__main__":
    mod = load(sys.argv[1]); out = sys.argv[2]
    date_txt = getattr(mod, "DATE", "Wednesday, October 28, 2026")
    for prefix, h in (("ig", 1350), ("tt", 1920)):
        ps = make_carousel(mod.ITEMS, getattr(mod, "BRIEFS", None), getattr(mod, "HOOK", None), out, prefix, h, getattr(mod, "ISSUE", 1), date_txt)
        print(prefix, len(ps), "slides")
