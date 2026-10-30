"""Would You Rather: split-screen dilemmas, a countdown, then Noggin's pick.
Video (16:9): left/right split.  Short (9:16): top/bottom split.
spec["questions"] = [{"a": ["LINE 1", "LINE 2"], "ae": "🍕", "b": [...], "be": "⚡", "pick": 0|1, "why": "SHORT REASON"}, ...]
"""
import math
from PIL import Image, ImageDraw
import gcommon as g

QT, PICK = 7.6, 4.0
LEFT, RIGHT = (226, 60, 70), (50, 100, 230)

def build(spec, fmt):
    Q = spec["questions"]; vert = fmt == "short"; W, H = g.W, g.H
    T0 = 2.2; DUR = T0 + QT*len(Q) + 2.6
    K = g.Kicks(); K.add(0.1, 0.8)
    for n in range(len(Q)): K.add(T0 + n*QT + 0.35, 0.7, True); K.add(T0 + n*QT + 0.9 + PICK, 1.3, True)
    hook1, hook2 = spec.get("hook", ["WOULD YOU RATHER", f"YOU HAVE {int(PICK)} SECONDS"])

    def panel(txt, e, col, w, h, t, focus):
        im = Image.new("RGBA", (max(2, int(w)), max(2, int(h))), col + (255,)); d = ImageDraw.Draw(im)
        for y in range(0, im.height, 6): d.line((0, y, im.width, y), fill=(255, 255, 255, 8))
        cx, cy = im.width/2, im.height/2; s = 1 + 0.12*focus
        es = 300 if not vert else 260; ey = cy - (160 if not vert else 120)
        g.paste(im, g.emoji(e, es), cx, ey + 10*math.sin(t*3), s)
        mw = min(820, im.width - 60)
        g.paste(im, g.T(txt[0], 72 if not vert else 76, g.WHITE, 10, maxw=mw), cx, cy + (100 if not vert else 110), s)
        if len(txt) > 1: g.paste(im, g.T(txt[1], 60 if not vert else 62, g.WHITE, 9, maxw=mw), cx, cy + (190 if not vert else 200), s)
        return im

    def frame(t):
        im = Image.new("RGBA", (W, H), (12, 10, 24, 255))
        n = min(len(Q) - 1, int((t - T0)//QT)) if t >= T0 else 0; lt = t - T0 - n*QT if t >= T0 else -1; q = Q[n]; pick = q["pick"]
        if T0 <= t < T0 + QT*len(Q):
            rev = 0.9 + PICK; k = g.ease((lt - rev)/0.4) if lt >= rev else 0; slide = g.ease(lt/0.35)
            span = H if vert else W
            sa = span/2 + (span*0.16*k if pick == 0 else -span*0.16*k)
            if not vert:
                A = panel(q["a"], q["ae"], LEFT, sa, H, t, k if pick == 0 else 0); B = panel(q["b"], q["be"], RIGHT, W - sa, H, t, k if pick == 1 else 0)
                im.alpha_composite(A, (int(-W/2*(1 - slide)), 0)); im.alpha_composite(B, (int(sa + W/2*(1 - slide)), 0))
                if k > 0:
                    dim = Image.new("RGBA", (int(W - sa) if pick == 0 else int(sa), H), (0, 0, 0, int(150*k))); im.alpha_composite(dim, (int(sa), 0) if pick == 0 else (0, 0))
                cx, cy = sa, H/2
            else:
                A = panel(q["a"], q["ae"], LEFT, W, sa, t, k if pick == 0 else 0); B = panel(q["b"], q["be"], RIGHT, W, H - sa, t, k if pick == 1 else 0)
                im.alpha_composite(A, (0, int(-H/2*(1 - slide)))); im.alpha_composite(B, (0, int(sa + H/2*(1 - slide))))
                if k > 0:
                    dim = Image.new("RGBA", (W, int(H - sa) if pick == 0 else int(sa)), (0, 0, 0, int(150*k))); im.alpha_composite(dim, (0, int(sa)) if pick == 0 else (0, 0))
                cx, cy = W/2, sa
            d = ImageDraw.Draw(im); rr = 105
            d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=(12, 10, 24), outline=g.WHITE, width=8)
            if 0.9 <= lt < rev:
                left = rev - lt; d.arc((cx - rr - 4, cy - rr - 4, cx + rr + 4, cy + rr + 4), -90, -90 + 360*left/PICK, fill=g.YEL, width=14)
                g.paste(im, g.T(str(math.ceil(left)), 90, g.WHITE, 0), cx, cy)
            else: g.paste(im, g.T("OR", 80, g.WHITE, 0), cx, cy, 1 + 0.06*math.sin(t*8))
            g.paste(im, g.T(f"WOULD YOU RATHER...  {n + 1}/{len(Q)}", 54, g.WHITE, 8, maxw=W - 80), W/2, 70 if not vert else 120)
            if lt >= rev:
                if not vert: x, y1, y2 = (sa/2 if pick == 0 else sa + (W - sa)/2), 170, 880
                else: x = W/2; y1, y2 = ((sa/2 - 300, sa/2 + 330) if pick == 0 else (sa + (H - sa)/2 - 330, sa + (H - sa)/2 + 330))
                g.paste(im, g.T("NOGGIN PICKS THIS", 70, g.YEL, 10, maxw=W - 80), x, y1, g.back((lt - rev)/0.25), rot=-4)
                g.paste(im, g.T(q["why"], 50, g.WHITE, 8, maxw=min(900, W - 80)), x, y2, g.back((lt - rev - 0.4)/0.3))
                g.paste(im, g.T("AGREE? COMMENT A OR B", 44, g.YEL, 7, maxw=W - 80), W/2, H - 50 if not vert else H - 110, g.back((lt - rev - 0.9)/0.3))
        if t < T0 + 0.35:
            a = 1 - g.ease((t - T0)/0.35)
            if a > 0:
                im.alpha_composite(Image.new("RGBA", (W, H), (12, 10, 24, int(255*a))))
                g.paste(im, g.T(hook1, 150, g.WHITE, 14, maxw=W - 80), W/2, H/2 - 120, g.back((t - 0.1)/0.25), alpha=a)
                g.paste(im, g.T(hook2, 100, g.YEL, 11, maxw=W - 80), W/2, H/2 + 50, g.back((t - 0.8)/0.25), rot=-3, alpha=a)
        if t >= T0 + QT*len(Q):
            k = t - T0 - QT*len(Q); im.alpha_composite(Image.new("RGBA", (W, H), (12, 10, 24, 255)))
            g.paste(im, g.T("WHICH ONE WAS HARDEST?", 110, g.WHITE, 12, maxw=W - 80), W/2, H/2 - 100, g.back(k/0.3))
            g.paste(im, g.T("TELL NOGGIN IN THE COMMENTS", 76, g.GRN, 9, maxw=W - 80), W/2, H/2 + 50, g.back((k - 0.3)/0.3))
        pose = "laugh" if t < T0 or t >= T0 + QT*len(Q) else "wave" if lt >= 0.9 + PICK else "idle"
        g.put_mascot(im, t, pose, (0, -1), W - 90, H - 90 if not vert else H - 260, 0.5)
        dx, dy = K.shake(t); return g.camera(im, K.zoom(t), dx, dy, K.flash(t), t=t, dur=DUR)

    def audio(path):
        M = g.Mix(DUR); M.add(M.boom(), 0.1, 0.8); M.add(M.ding(), 0.9)
        for n in range(len(Q)):
            b = T0 + n*QT; M.add(M.whoosh(0.4), b); M.add(M.thud(80), b + 0.35)
            for s in range(int(PICK*2)): M.add(M.tick(1300 if s < PICK*2 - 2 else 1900), b + 0.9 + s*0.5)
            M.add(M.boom(), b + 0.9 + PICK, 0.8); M.add(M.ding(1568), b + 1.0 + PICK)
        M.fanfare(T0 + QT*len(Q)); M.save(path)

    stills = [1.2] + [T0 + n*QT + 2.5 for n in range(min(3, len(Q)))] + [T0 + QT*len(Q) - 1.0]
    return frame, audio, DUR, stills, {}
