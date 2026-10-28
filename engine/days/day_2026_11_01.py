"""2026-11-01. 2 puzzle slots (12:00 + 16:00 YT). Formats rotate: previous video (10-31 16:00) was SPEED MATH.
Video 1 (12:00): WHICH IS BIGGER / HEAVIER comparisons. Video 2 (16:00): 3-level Gen Z trivia.
Hook-first: level-1 question on screen from frame 0 with the hook line."""
from puzzles8 import trivia, scene_q

def _t(q, a, wrong, emojis, why, header, banner, catch=False):
    return lambda s, lv: trivia(q, a, wrong, emojis, why, header, banner, catch=catch, seed=s)

GENS = dict(
  # 1 - which is bigger / heavier
  d1101_tallest=_t("Which one is the TALLEST?", "Burj Khalifa", ["Eiffel Tower", "Empire State Building", "Statue of Liberty"], ["🏙️", "📏"],
                   "Burj Khalifa: 828 m. Empire State: 443 m. Eiffel: 330 m", "WHICH IS BIGGER?", "BURJ KHALIFA!"),
  d1101_moon_pluto=_t("Which one is the BIGGEST?", "Our Moon", ["Pluto", "Ceres", "Phobos"], ["🌙", "🔭"],
                      "Moon: 3,474 km wide. Pluto: only 2,377 km", "SPACE SIZE-OFF!", "OUR MOON!"),
  d1101_ice_melt=_t("A glass of ice melts into water. Is it HEAVIER now?", "Same weight", ["Heavier", "Lighter", "Depends on the glass"], ["🧊", "💧"],
                    "melting changes the shape, not the mass", "HEAVY QUESTION!", "SAME WEIGHT!", catch=True),
  # 2 - 3-level Gen Z trivia
  d1101_npc=_t("In gaming, what does 'NPC' stand for?", "Non-player character", ["New player challenge", "No power code", "Next pro champion"], ["🎮", "🤖"],
               "a character the game controls, not a player", "GAMER TRIVIA!", "NON-PLAYER CHARACTER!"),
  d1101_bat=_t("Which is the only mammal that can truly FLY?", "Bat", ["Flying squirrel", "Sugar glider", "Flying lemur"], ["🦇", "🌙"],
               "bats fly with wings, the others only glide", "ANIMAL FACT!", "THE BAT!"),
  d1101_timezones=_t("Which country has the MOST time zones?", "France", ["Russia", "USA", "China"], ["🌍", "⏰"],
                     "France has 12, thanks to its overseas territories", "WORLD TRIVIA!", "FRANCE!", catch=True),
)
PLAN = [
  (("d1101_tallest", "d1101_moon_pluto", "d1101_ice_melt"), "Which Is Bigger", "Which is bigger, Pluto or the Moon? 🌙"),
  (("d1101_npc", "d1101_bat", "d1101_timezones"), "Most Time Zones", "The country with the MOST time zones 🌍"),
]
HOOK_LINES = ["ONLY 1 IN 10 GETS THIS", "99% FAIL LEVEL 3"]
