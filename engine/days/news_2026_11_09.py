# The Noggin Times, Monday Nov 9, 2026 (cinematic news6 look). Every fact checked against the linked page on 2026-11-07/08.
# v2 (Nov 8): fox story replaces the cube mile (event was Oct 12), Singapore Airlines brief replaces Swift + ISS (less space-heavy),
# ESCAPADE worded as planned flybys (NASA had not posted the outcome yet), KSC line restored, all Commons photos at 2560 px.
P = "assets/photos/2026-11-09/"

ITEMS = [
    dict(text="NASA just revealed its newest experimental plane: the X-70 Fractal.",
         detail="It was unveiled at Kennedy Space Center and can carry 2,000 pounds of experiments.",
         vo=["NASA just revealed its newest experimental plane, the X-70 Fractal.",
             "It was unveiled at Kennedy Space Center, and can carry 2,000 pounds of experiments."],
         photo=P + "x70.jpg", credit="X-70 Fractal, generated image | NASA",
         explain_photo=P + "ksc_vab.jpg", explain_credit="Kennedy Space Center, Florida | NASA/Cory Huston / Public domain",
         source=dict(outlet="NASA", date="November 4, 2026",
                     headline="NASA Announces X-70 Experimental Aircraft to Advance Flight Research",
                     url="nasa.gov", link="https://www.nasa.gov/news-release/nasa-announces-x-70-experimental-aircraft-to-advance-flight-research/")),
    dict(text="Two NASA spacecraft were set to swing past Earth on Nov 7 and 9, to slingshot themselves to Mars.",
         detail="If the engine burns worked, they reach Mars in September 2027.",
         vo=["Two NASA spacecraft were set to slingshot past Earth on Saturday and Monday, toward Mars.",
             "If the engine burns worked, they reach Mars in September 2027."],
         photo=P + "earth.jpg", credit="Earth from Apollo 17 | NASA / Public domain",
         explain_photo=P + "escapade_mars.jpg", explain_credit="ESCAPADE at Mars, illustration | NASA SVS / Public domain",
         source=dict(outlet="NASA", date="November 2, 2026",
                     headline="NASA's Twin ESCAPADE Spacecraft to Slingshot Past Earth on Way to Mars",
                     url="science.nasa.gov", link="https://science.nasa.gov/blogs/escapade/2026/11/02/nasas-twin-escapade-spacecraft-to-slingshot-past-earth-on-way-to-mars/")),
    dict(text="A fox ran onto the pitch during a pro football match in Turkey.",
         detail="It climbed into the stands. The home team won 6-0.",
         vo=["A fox ran onto the pitch in the middle of a pro football match in Turkey.",
             "It climbed into the stands. The home team won 6-0."],
         photo=P + "fox.jpg", credit="A red fox | Cephas / CC BY-SA 3.0",
         explain_photo=P + "football.jpg", explain_credit="A football on grass | J Dimas / CC BY 2.0",
         source=dict(outlet="UPI", date="November 3, 2026",
                     headline="Watch: Fox interrupts professional soccer game in Turkey",
                     url="upi.com", link="https://www.upi.com/Odd_News/2026/11/03/turkey-soccer-game-fox-kayseri/1171793729955/")),
]

BRIEFS = [[
    dict(cat="Travel", title="Singapore Airlines is adding the biggest double bed on any plane",
         text="Part of a S$2 billion cabin upgrade, arriving from the second half of 2027.",
         vo="Singapore Airlines is adding the biggest double bed on any plane, from 2027.",
         photo=P + "sia_a350.jpg", credit="Singapore Airlines A350-900 | Ian Gratton / CC BY 2.0",
         source=dict(outlet="Euronews", date="Nov 6", link="https://www.euronews.com/2026/11/06/singapore-airlines-to-invest-14-billion-upgrading-luxury-long-haul-cabins")),
    dict(cat="Drops", title="The Air Jordan 6 'White Infrared' is back",
         text="The 1991 colourway returns on SNKRS.", price="Nov 7 on SNKRS: $215",
         vo="And the Air Jordan 6 White Infrared is back, for $215.",
         photo=P + "aj6_nike.jpg", credit="Image: Nike",
         source=dict(outlet="Nike SNKRS", date="Nov 7", link="https://www.nike.com/launch/t/air-jordan-6-white-infrared-white-and-light-crimson")),
]]

_src = [(i["source"]["outlet"], i["source"]["link"]) for i in ITEMS] + [(b["source"]["outlet"], b["source"]["link"]) for pg in BRIEFS for b in pg]
_sources = "\n".join(f"- {o}: {l}" for o, l in _src)
_photos = "\n".join(f"- {i['credit']}\n- {i['explain_credit']}" for i in ITEMS) + "\n" + "\n".join(f"- {b['credit']}" for pg in BRIEFS for b in pg) + "\n- ESCAPADE passing Mars, illustration | NASA SVS / Public domain"

NEWS = [dict(
    title="NASA's new X-plane, a fox on the pitch and more ✈️ #shorts",
    vo_open="Here's the news you missed this week.",
    open_photo=P + "escapade_craft.jpg", open_credit="ESCAPADE passing Mars, illustration | NASA SVS / Public domain",
    cats=["Planes", "Space", "Football", "Travel"],
    vo_outro="That's the news. Follow so you don't miss next week.",
    items=ITEMS, briefs=BRIEFS,
    description=("NASA showed off a brand-new experimental plane, two spacecraft set off to slingshot past Earth toward Mars, and a fox crashed a football match. Here's the news you missed this week.\n\n"
                 "Sources:\n" + _sources + "\n\nPhotos:\n" + _photos + "\n\n#shorts #news #thisweek #noggin"),
)]
