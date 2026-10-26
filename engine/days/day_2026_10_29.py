"""Day file (template). 7 videos x 3 levels = 21 NEW questions. Mix trivia (trivia()) and puzzles (scene_q()) at random,
every video has exactly one catch=True question on level 3 (hard). Gen Z themes: games, apps, music, internet, food, space, money."""
from puzzles8 import trivia, scene_q

def _t(q, a, wrong, emojis, why, header, banner, catch=False):
    return lambda s, lv: trivia(q, a, wrong, emojis, why, header, banner, catch=catch, seed=s)
def _p(q, a, wrong, emojis, why, header, banner, catch=False, fmt=str):
    return lambda s, lv: scene_q(q, emojis, why, a, wrong, header, banner, catch=catch, seed=s, size=50, fmt=fmt)

GENS = dict(
  # 1
  d29_spotify=_t("What colour is the Spotify logo?", "Green", ["Purple", "Black", "Blue"], ["🎧", "🎶"], "the famous green circle with 3 lines", "APP TRIVIA!", "GREEN!"),
  d29_pizza_slices=_p("A pizza has 8 slices. You eat 2, then your friend eats HALF of what's left. How many slices are left?", "3", ["2", "4", "5"], ["🍕", "😋"],
                      "8 − 2 = 6, your friend eats 3, so 3 left", "PIZZA MATH!", "3 SLICES!"),
  d29_honey=_t("Which food never goes bad if sealed?", "Honey", ["Rice", "Cheese", "Bread"], ["🍯", "🐝"], "3000-year-old honey was found still edible!", "FOOD FACT!", "HONEY!", catch=True),
  # 2
  d29_minecraft_blocks=_p("You need 64 blocks for a stack in Minecraft. You have 200 blocks. How many FULL stacks?", "3", ["4", "2", "5"], ["⛏️", "🧱"],
                          "64 × 3 = 192, so 3 full stacks + 8 left", "GAMER MATH!", "3 STACKS!"),
  d29_lol=_t("What does 'IRL' mean?", "In real life", ["I really laughed", "In red light", "It's really late"], ["🌍", "💬"], "IRL = offline, in the real world", "SLANG CHECK!", "IN REAL LIFE!"),
  d29_shark=_t("Which animal is OLDER than trees?", "Sharks", ["Crocodiles", "Turtles", "Jellyfish only"], ["🦈", "🌳"], "sharks: ~450 million years, trees: ~350 million", "ANIMAL FACT!", "SHARKS!", catch=True),
  # 3
  d29_ps=_t("Which shape is NOT on a PlayStation controller button?", "Star", ["Triangle", "Circle", "Square"], ["🎮"], "the 4 are triangle, circle, cross and square", "GAMING TRIVIA!", "STAR!"),
  d29_sub=_p("A streamer has 900 subs and gains 150 per week. How many weeks to reach 2,000?", "8", ["7", "6", "9"], ["📺", "📈"],
             "1100 ÷ 150 = 7.3, so it takes 8 full weeks", "SUB COUNT!", "8 WEEKS!"),
  d29_eiffel=_t("The Eiffel Tower gets TALLER in summer. Why?", "The metal expands", ["They add a floor", "It's an illusion", "The ground rises"], ["🗼", "☀️"],
                "heat makes iron expand: up to ~15 cm taller!", "SCIENCE FACT!", "IT EXPANDS!", catch=True),
  # 4
  d29_bitrate=_p("A video is 30 seconds long at 60 frames per second. How many frames?", "1800", ["180", "900", "3600"], ["🎬", "🎞️"], "30 × 60 = 1800", "FRAME COUNT!", "1800 FRAMES!"),
  d29_hello=_t("Which language says 'Hola'?", "Spanish", ["Italian", "French", "German"], ["👋", "🌍"], "Hola = hello in Spanish", "LANGUAGE TRIVIA!", "SPANISH!"),
  d29_week=_p("If 2 people can make 2 TikToks in 2 hours, how many TikToks can 6 people make in 6 hours?", "18", ["6", "12", "36"], ["🎵", "⏰"],
              "1 person makes 1 per 2 h: 6 people × 3 each = 18", "THINK FAST!", "18 TIKTOKS!", catch=True),
  # 5
  d29_moon=_t("How many Earths could fit inside the Sun?", "About 1.3 million", ["About 1,000", "About 100", "About 50,000"], ["☀️", "🌍"],
              "the Sun is HUGE: ~1.3 million Earths", "SPACE FACT!", "1.3 MILLION!"),
  d29_battery2=_p("Your earbuds last 6 h. The case gives 3 full extra charges. Total listening time?", "24 h", ["18 h", "9 h", "20 h"], ["🎧", "🔋"],
                  "6 h + 3 × 6 h = 24 h", "BATTERY MATH!", "24 HOURS!"),
  d29_strawberry=_t("Roughly how many seeds are on the OUTSIDE of a strawberry?", "About 200", ["About 20", "About 2,000", "None"], ["🍓", "🔍"],
                    "~200 seeds, and it's the only fruit with seeds outside", "FOOD FACT!", "ABOUT 200!", catch=True),
  # 6
  d29_emoji_most=_t("Which emoji is used the MOST in the world?", "Laughing-crying face", ["Red heart", "Thumbs up", "Fire"], ["😂", "❤️", "👍", "🔥"], "'face with tears of joy' tops the charts", "EMOJI TRIVIA!", "THE LAUGHING-CRYING FACE!"),
  d29_sneaker=_p("Sneakers cost $120. They're 25% off, then you use a $10 coupon. What do you pay?", "$80", ["$85", "$90", "$75"], ["👟", "🏷️"],
                 "$120 − $30 = $90, − $10 = $80", "SALE MATH!", "$80!"),
  d29_brain=_t("Your brain uses about how much of your body's energy?", "20%", ["2%", "50%", "5%"], ["🧠", "⚡"], "only 2% of your weight, but 20% of your energy!", "BODY FACT!", "20%!", catch=True),
  # 7
  d29_yt=_t("What was the first video ever uploaded to YouTube about?", "A zoo", ["A cat", "A song", "A game"], ["▶️", "🐘"], "'Me at the zoo', 2005", "INTERNET HISTORY!", "A ZOO!"),
  d29_wifi=_p("The Wi-Fi password is the number of letters in 'NOGGIN' times the number of vowels in it. What is it?", "12", ["6", "18", "8"], ["📶", "🔑"],
              "6 letters × 2 vowels (O, I) = 12", "WI-FI PUZZLE!", "12!"),
  d29_clock=_p("A clock shows 3:15. What's the angle between the hands?", "7.5°", ["0°", "15°", "90°"], ["🕒", "📐"],
               "the hour hand moves too: 1/4 of 30° = 7.5°", "TRICK QUESTION!", "7.5°!", catch=True),
)
PLAN = [
  (("d29_spotify", "d29_pizza_slices", "d29_honey"), "The Food That Never Expires", "This food NEVER goes bad 🍯 Can you guess it?"),
  (("d29_minecraft_blocks", "d29_lol", "d29_shark"), "Older Than Trees", "This animal is OLDER than trees 🦈 Most people don't know"),
  (("d29_ps", "d29_sub", "d29_eiffel"), "The Growing Tower", "The Eiffel Tower GROWS in summer?! 🗼 3-level quiz"),
  (("d29_bitrate", "d29_hello", "d29_week"), "The TikTok Trap", "2 people, 2 TikToks, 2 hours... 🎵 The trap question"),
  (("d29_moon", "d29_battery2", "d29_strawberry"), "Count the Strawberry Seeds", "How many seeds on a strawberry? 🍓 Nobody gets this"),
  (("d29_emoji_most", "d29_sneaker", "d29_brain"), "Your Brain Uses How Much", "Your brain uses HOW much energy? 🧠 Can you beat 3 levels?"),
  (("d29_yt", "d29_wifi", "d29_clock"), "The Clock Angle Trap", "What's the angle at 3:15? 🕒 It's NOT zero"),
]
