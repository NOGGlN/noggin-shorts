"""Sample for the cinematic news format (news6.py), built from the 31 Oct 2026 edition (days/news_2026_10_31.py).
Only adds the spoken lines (vo); every fact comes from that edition's checked sources."""
import copy, importlib.util, os
_s = importlib.util.spec_from_file_location("src", os.path.join(os.path.dirname(os.path.abspath(__file__)), "news_2026_10_31.py"))
_m = importlib.util.module_from_spec(_s); _s.loader.exec_module(_m)
ed = copy.deepcopy(_m.NEWS[0])
ed["vo_open"] = "Here's the news you missed this week."
ed["cats"] = ["Robots", "Records", "Space", "Sneakers"]
VO = [
    ["Scientists in Switzerland built a robot hand that walks on its own fingers.",
     "It learned to walk in a computer simulation, and it can even type on a keyboard."],
    ["A man strapped himself to the wing of a flying plane, to open trading cards.",
     "7 packs in one minute, 600 feet up. It's a world record."],
    ["A man carried a million-dollar lottery ticket in his wallet for two months.",
     "He only found out when he tried to pay for a soda with some old tickets."],
]
for it, vo in zip(ed["items"], VO): it["vo"] = vo
BVO = {"Webb spots a spooky cat's head in space": "NASA's Webb telescope spotted a cat's head in space, just in time for Halloween.",
       "The Air Force 1 'What the LA' is back": "And a sneaker inspired by the sports teams of Los Angeles drops on November fifth, for $125.",
       "F1 could crown its champion in Mexico on Sunday": "Formula One could crown its champion in Mexico on Sunday."}
for page in ed["briefs"]:
    for b in page:
        if b["title"] in BVO: b["vo"] = BVO[b["title"]]
ed["vo_outro"] = "That's the news. Follow so you don't miss next week."
NEWS = [ed]
