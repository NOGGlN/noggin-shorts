"""2026-11-02. 2 puzzle slots (12:00 + 16:00 YT). Formats rotate: previous video (11-01 16:00) was 3-LEVEL GEN Z TRIVIA.
Video 1 (12:00): IMPOSSIBLE-LOOKING FACTS with a reveal. Video 2 (16:00): SPEED MATH WITH A TRAP.
Hook-first: level-1 question on screen from frame 0 with the hook line."""
from puzzles8 import trivia, scene_q

def _t(q, a, wrong, emojis, why, header, banner, catch=False):
    return lambda s, lv: trivia(q, a, wrong, emojis, why, header, banner, catch=catch, seed=s)

def _p(q, a, wrong, emojis, why, header, banner, catch=False, fmt=str):
    return lambda s, lv: scene_q(q, emojis, why, a, wrong, header, banner, catch=catch, seed=s, size=50, fmt=fmt)

GENS = dict(
  # 1 - impossible-looking facts
  d1102_wombat=_t("Wombats are famous for pooping out what SHAPE?", "Cubes", ["Spheres", "Stars", "Spirals"], ["💩", "🤯"],
                  "wombat poop comes out as little cubes", "IMPOSSIBLE FACT!", "CUBES!"),
  d1102_cleopatra=_t("Cleopatra lived closer to the Moon landing than to the building of...?", "The Great Pyramid",
                     ["The Colosseum", "The Eiffel Tower", "The Taj Mahal"], ["🏺", "🚀"],
                     "Pyramid: about 2560 BC. Moon landing: 1969", "TIME TRAVEL FACT!", "THE GREAT PYRAMID!"),
  d1102_trex=_t("Which dinosaur lived closer in time to T. rex than YOU do?", "None of them", ["Stegosaurus", "Brachiosaurus", "Diplodocus"], ["🦖", "⏳"],
                "they all lived 75+ million years before T. rex", "DINO TRAP!", "NONE OF THEM!", catch=True),
  # 2 - speed math with a trap
  d1102_coins=_p("You win 15 coins every round. How many coins after 8 rounds?", "120", ["105", "135", "115"], ["🪙", "🎮"],
                 "15 x 8 = 120", "SPEED MATH!", "120 COINS!"),
  d1102_highfive=_p("5 friends each high-five every other friend once. How many high-fives?", "10", ["20", "25", "15"], ["🙌", "👥"],
                    "4 + 3 + 2 + 1 = 10", "THINK FAST!", "10 HIGH-FIVES!"),
  d1102_half=_p("Divide 30 by half, then add 10. What do you get?", "70", ["25", "40", "35"], ["➗", "🧠"],
                "30 / 0.5 = 60, then 60 + 10 = 70", "TRAP QUESTION!", "70!", catch=True),
)
PLAN = [
  (("d1102_wombat", "d1102_cleopatra", "d1102_trex"), "Impossible Facts", "T. rex lived closer to YOU than to these 🦖"),
  (("d1102_coins", "d1102_highfive", "d1102_half"), "Speed Math Trap", "Divide 30 by half... most people say 15 🧮"),
]
HOOK_LINES = ["ONLY 1 IN 10 GETS THIS", "99% FAIL LEVEL 3"]
