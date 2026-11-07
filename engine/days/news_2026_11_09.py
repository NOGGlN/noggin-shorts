# The Noggin Times, Monday Nov 9, 2026 (cinematic news6 look). Every fact checked against the linked page on 2026-11-07.
P = "assets/photos/2026-11-09/"

ITEMS = [
    dict(text="NASA just revealed its newest experimental plane: the X-70 Fractal.",
         detail="It can carry 2,000 pounds of experiments and should first fly for NASA within two years.",
         vo=["NASA just revealed its newest experimental plane, the X-70 Fractal.",
             "It can carry 2,000 pounds of experiments, and should fly within two years."],
         photo=P + "x70.jpg", credit="X-70 Fractal, generated image | NASA",
         explain_photo=P + "ksc_vab.jpg", explain_credit="Kennedy Space Center, Florida | NASA/Cory Huston / Public domain",
         source=dict(outlet="NASA", date="November 4, 2026",
                     headline="NASA Announces X-70 Experimental Aircraft to Advance Flight Research",
                     url="nasa.gov", link="https://www.nasa.gov/news-release/nasa-announces-x-70-experimental-aircraft-to-advance-flight-research/")),
    dict(text="Two NASA spacecraft are using Earth as a slingshot to get to Mars.",
         detail="Each one fires its engine for about 9 minutes as it swings past. They reach Mars in September 2027.",
         vo=["Two NASA spacecraft are using Earth as a slingshot to Mars.",
             "Each fires its engine for about 9 minutes as it swings past. They reach Mars in September 2027."],
         photo=P + "escapade.jpg", credit="ESCAPADE's Earth flyby path, animation | NASA, Advanced Space/Matt Bolliger",
         explain_photo=P + "escapade_craft.jpg", explain_credit="ESCAPADE at Mars, illustration | NASA SVS / Public domain",
         source=dict(outlet="NASA", date="November 2, 2026",
                     headline="NASA's Twin ESCAPADE Spacecraft to Slingshot Past Earth on Way to Mars",
                     url="science.nasa.gov", link="https://science.nasa.gov/blogs/escapade/2026/11/02/nasas-twin-escapade-spacecraft-to-slingshot-past-earth-on-way-to-mars/")),
    dict(text="A runner solved four Rubik's cubes while running a mile, in just over 5 minutes.",
         detail="He solved a cube, ran a lap, and repeated. It's now a Guinness World Record.",
         vo=["A British runner solved four Rubik's cubes while running one mile.",
             "His time: 5 minutes 9 seconds. A world record."],
         photo=P + "cube.jpg", credit="A Rubik's cube | Alessandro Di Pretoro / CC BY-SA 4.0",
         explain_photo=P + "track.jpg", explain_credit="Athletics track | Santeri Viinamaki / CC BY-SA 4.0",
         source=dict(outlet="UPI", date="November 6, 2026",
                     headline="Watch: Rubik's cube enthusiast sprints to Guinness World Records title",
                     url="upi.com", link="https://www.upi.com/Odd_News/2026/11/06/guinness-world-records-puzzle-cube-mile/9871793989473/")),
]

BRIEFS = [[
    dict(cat="Space", title="NASA's Swift telescope says goodbye",
         text="After almost 22 years in space, Swift re-entered Earth's atmosphere on Nov 4. It was built for a 2-year mission.",
         vo="NASA's Swift telescope fell back to Earth after almost 22 years.",
         photo=P + "swift.jpg", credit="Swift in space, illustration | NASA",
         source=dict(outlet="NASA", date="Nov 4", link="https://science.nasa.gov/blogs/swift/2026/11/02/nasas-swift-observatory-to-re-enter-atmosphere/")),
    dict(cat="Drops", title="The Air Jordan 6 'White Infrared' is back",
         text="The 1991 colourway returns on SNKRS.", price="Nov 7 on SNKRS: $215",
         vo="And the Air Jordan 6 White Infrared is back, for $215.",
         photo=P + "aj6_nike.jpg", credit="Image: Nike",
         source=dict(outlet="Nike SNKRS", date="Nov 7", link="https://www.nike.com/launch/t/air-jordan-6-white-infrared-white-and-light-crimson")),
    dict(cat="Space", title="The ISS gets its 8th and final new solar array",
         text="Spacewalkers installed the last roll-out array on Nov 5, raising the station's power to about 215 kilowatts.",
         photo=P + "iss_irosa.jpg", credit="A roll-out solar array on the ISS arm, 2021 | NASA / Public domain",
         source=dict(outlet="NASA", date="Nov 5", link="https://www.nasa.gov/blogs/spacestation/2026/11/05/spacewalkers-install-final-roll-out-solar-array/")),
]]

_src = [(i["source"]["outlet"], i["source"]["link"]) for i in ITEMS] + [(b["source"]["outlet"], b["source"]["link"]) for pg in BRIEFS for b in pg]
_sources = "\n".join(f"- {o}: {l}" for o, l in _src)
_photos = "\n".join(f"- {i['credit']}\n- {i['explain_credit']}" for i in ITEMS) + "\n" + "\n".join(f"- {b['credit']}" for pg in BRIEFS for b in pg)

NEWS = [dict(
    title="NASA's new X-plane and a slingshot to Mars ✈️ #shorts",
    vo_open="Here's the news you missed this week.",
    cats=["Planes", "Space", "Records", "Sneakers"],
    vo_outro="That's the news. Follow so you don't miss next week.",
    items=ITEMS, briefs=BRIEFS,
    description=("NASA showed off a brand-new experimental plane, and two spacecraft are using Earth as a slingshot to Mars. Here's the news you missed this week.\n\n"
                 "Sources:\n" + _sources + "\n\nPhotos:\n" + _photos + "\n\n#shorts #news #thisweek #noggin"),
)]
