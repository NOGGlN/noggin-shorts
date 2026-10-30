"""2026-11-03. 2 puzzle slots (12:00 + 16:00 YT). Formats rotate: previous video (11-02 16:00) was SPEED MATH WITH A TRAP.
Video 1 (12:00): 3-LEVEL GEN Z TRIVIA. Video 2 (16:00): SPOT THE MISTAKE.
Hook-first: level-1 question on screen from frame 0 with the hook line."""
from puzzles8 import trivia, scene_q

def _t(q, a, wrong, emojis, why, header, banner, catch=False):
    return lambda s, lv: trivia(q, a, wrong, emojis, why, header, banner, catch=catch, seed=s)

def _p(q, a, wrong, emojis, why, header, banner, catch=False, fmt=str):
    return lambda s, lv: scene_q(q, emojis, why, a, wrong, header, banner, catch=catch, seed=s, size=50, fmt=fmt)

GENS = dict(
  # 1 - Gen Z trivia
  d1103_fomo=_t("In texting, what does 'FOMO' stand for?", "Fear of missing out", ["Follow or move on", "Fun online moments", "Friends of my own"],
                ["📱", "😱"], "FOMO = fear of missing out", "SLANG CHECK!", "FEAR OF MISSING OUT!"),
  d1103_pacman=_t("Pac-Man was first released in Japan under what name?", "Puck Man", ["Pizza Man", "Chomp Man", "Pellet Man"],
                  ["👾", "🍒"], "it launched in Japan in 1980 as Puck Man", "GAMING TRIVIA!", "PUCK MAN!"),
  d1103_months=_t("How many months of the year have 28 days?", "All 12", ["1", "2", "None"],
                  ["📅", "🤔"], "every month has at least 28 days!", "TRAP QUESTION!", "ALL 12!", catch=True),
  # 2 - spot the mistake
  d1103_weekday=_p("Spot the mistake: which day is spelled WRONG?", "Wensday", ["Thursday", "Saturday", "Tuesday"], ["🔍", "📅"],
                   "it is spelled Wednesday", "SPOT THE MISTAKE!", "WENSDAY!"),
  d1103_spelling=_p("Spot the mistake: which word is spelled WRONG?", "Seperate", ["Necessary", "Definitely", "Calendar"], ["🔍", "✏️"],
                    "the right spelling is separate", "SPOT THE MISTAKE!", "SEPERATE!"),
  d1103_yolk=_p("Which is right: 'The yolk of the egg IS white' or 'The yolk of the egg ARE white'?", "Neither",
                ["IS white", "ARE white", "Both work"], ["🥚", "🔍"],
                "egg yolks are yellow, not white!", "TRAP QUESTION!", "NEITHER!", catch=True),
)
PLAN = [
  (("d1103_fomo", "d1103_pacman", "d1103_months"), "Gen Z Trivia", "Pac-Man's REAL first name? 👾 Level 3 is a trap"),
  (("d1103_weekday", "d1103_spelling", "d1103_yolk"), "Spot The Mistake", "Spot the mistake... 99% miss level 3 🔍"),
]
HOOK_LINES = ["ONLY 1 IN 10 GETS THIS", "99% FAIL LEVEL 3"]
