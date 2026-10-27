"""2026-10-31 (Halloween), 16:00 slot. Format: SPEED MATH WITH A TRAP (the 12:00 video is 3-level mixed trivia).
Hook-first: level-1 question on screen from frame 0 with the hook line."""
from puzzles8 import trivia, scene_q

def _p(q, a, wrong, emojis, why, header, banner, catch=False, fmt=str):
    return lambda s, lv: scene_q(q, emojis, why, a, wrong, header, banner, catch=catch, seed=s, size=50, fmt=fmt)

GENS = dict(
  d1031_candy_share=_p("A bag has 48 candies. You share it equally with 3 friends. How many does each person get?", "12", ["16", "14", "10"], ["🍬", "🎃"],
                       "you + 3 friends = 4 people: 48 / 4 = 12", "CANDY MATH!", "12 EACH!"),
  d1031_haunted_tours=_p("Haunted house tours start every 12 minutes from 6:00 PM. When does the 6th tour start?", "7:00 PM", ["7:12 PM", "6:48 PM", "7:06 PM"], ["👻", "⏰"],
                         "the 1st is at 6:00, so add 5 x 12 = 60 min", "SPOOKY TIMING!", "7:00 PM!"),
  d1031_witch_hat=_p("A witch hat and a broom cost $11 in total. The broom costs $10 MORE than the hat. How much is the hat?", "$0.50", ["$1", "$1.50", "$0.10"], ["🧙", "🧹"],
                     "hat $0.50 + broom $10.50 = $11 (not $1!)", "TRICK OR TREAT!", "50 CENTS!", catch=True),
)
PLAN = [
  (("d1031_candy_share", "d1031_haunted_tours", "d1031_witch_hat"), "Halloween Speed Math", "The witch hat costs WHAT? 🧙 Most people say $1"),
]
HOOK_LINES = ["99% FAIL LEVEL 3"]
