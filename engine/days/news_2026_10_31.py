# The Noggin Times, Saturday Oct 31, 2026. Every fact checked against the linked article on 2026-10-30.
P = "assets/photos/2026-10-31/"

ITEMS = [
    dict(text="Scientists built a robot hand that walks around on its own fingers. Just in time for Halloween.",
         detail="Researchers at ETH Zurich compare it to Thing, the crawling hand from The Addams Family.",
         body=("The hand comes from the Soft Robotics Lab at ETH Zurich in Switzerland, which shared videos and a pre-print paper. "
               "Its fingers are not all the same, so it had to learn to stay balanced while moving them together.\n"
               "Instead of coding every move by hand, the team let it practise walking in a computer simulation. The videos show "
               "it crossing different surfaces, getting up after a fall, pushing objects and even typing on a keyboard."),
         numbers=[("1", "robot hand, no body attached"), ("4", "skills on video: walk, get up, push, type"),
                  ("2", "ETH Zurich scientists quoted")],
         photo=P + "robot_hand.jpg", credit="A robotic hand, Hannover Messe | NearEMPTiness / CC BY-SA 4.0",
         explain_photo=P + "eth_zurich.jpg", explain_credit="ETH Zurich, Switzerland | Ank Kumar / CC BY-SA 4.0",
         source=dict(outlet="UPI", date="October 30, 2026",
                     headline="Watch: Swiss researchers unveil robot hand that walks on its fingers",
                     url="upi.com", link="https://www.upi.com/Odd_News/2026/10/30/switzerland-eth-zurich-robot-hand-walk/8121793382351/")),
    dict(text="A man strapped himself to the wing of a flying plane to open trading cards. It's a world record.",
         detail="He ripped open seven packs in one minute, 600 feet up, in 120 mph winds.",
         body=("Londoner Colby Bull, who runs the collectibles business Edition One, did the stunt on Oct. 13 at Headcorn Aerodrome "
               "in Kent, England, standing on top of a 1940s Boeing Stearman biplane.\n"
               "He opened seven packs of Topps Chrome basketball cards without losing a single card to the wind. Guinness World "
               "Records certified it the day after the flight. Bull said his hands went numb and seven packs felt like seventy."),
         numbers=[("7", "card packs opened in one minute"), ("600 ft", "up in the air"),
                  ("120 mph", "winds on the wing"), ("1940s", "Boeing Stearman biplane")],
         photo=P + "wing_walker.jpg", credit="A biplane at an air show | Tech. Sgt. Joseph Harwood / Public domain",
         explain_photo=P + "headcorn.jpg", explain_credit="Biplane at Headcorn Aerodrome, Kent | Dave Bushell / CC BY-SA 2.0",
         source=dict(outlet="UPI", date="October 30, 2026",
                     headline="Watch: Collector opens trading cards while wing walking for world record",
                     url="upi.com", link="https://www.upi.com/Odd_News/2026/10/30/guinness-world-records-trading-cards-wing-walker/6101793377118/")),
    dict(text="A man carried a $1 million lottery ticket in his wallet for two months without knowing it.",
         detail="He only found out when he tried to pay for a soda with some old Powerball tickets.",
         body=("The 54-year-old from Wyoming, Michigan, bought the ticket for the Aug. 8 Powerball drawing at Big Top Market and "
               "tucked it into his wallet with his other tickets.\n"
               "Short on cash at the store, he handed over a few he knew were small winners. One came back with a message to file a "
               "claim at the lottery office. It had matched all five white balls. He plans to pay off his mortgage and invest."),
         numbers=[("$1M", "prize hiding in his wallet"), ("Nearly 2", "months before it was checked"),
                  ("5", "white balls matched"), ("Aug 8", "the Powerball drawing")],
         photo=P + "lottery_billboard.jpg", credit="Powerball jackpot sign, Missouri | Tony Webster / CC BY 2.0",
         explain_photo=P + "wyoming_mi.jpg", explain_credit="City Hall, Wyoming, Michigan | WMrapids / CC0",
         source=dict(outlet="UPI", date="October 30, 2026",
                     headline="$1M Powerball ticket spent two months in oblivious winner's wallet",
                     url="upi.com", link="https://www.upi.com/Odd_News/2026/10/30/lotto-Michigan-Lottery-powerball-two-months-lottery/5521793381252/")),
]

BRIEFS_P1 = [
    dict(cat="Space", title="Webb spots a spooky cat's head in space",
         text="NASA released this Webb view of the Cat's Head Nebula on Oct 29. Winds from huge nearby stars carved its shape.",
         photo=P + "webb_cats_head.jpg", credit="Cat's Head Nebula | NASA, ESA, CSA, STScI, J. DePasquale",
         source=dict(outlet="NASA", date="Oct 30", link="https://www.nasa.gov/image-article/nasas-james-webb-space-telescope-captures-eerie-cats-head/")),
    dict(cat="Drops", title="The Air Force 1 'What the LA' is back",
         text="A collage of colours and materials inspired by the sports teams of Los Angeles.",
         price="Nov 5 on SNKRS: $125",
         photo=P + "af1_what_the_la.jpg", credit="Image: Nike",
         source=dict(outlet="Nike SNKRS", date="Oct 30", link="https://www.nike.com/launch/t/air-force-1-low-premium-what-the-la")),
    dict(cat="F1", title="F1 could crown its champion in Mexico on Sunday",
         text="Kimi Antonelli leads by 123 points and needs ninth or better. The race starts Nov 1 at 8 p.m. GMT.",
         photo=P + "mercedes_w17.jpg", credit="Mercedes W17, 2026 Chinese GP | Liauzh / CC BY 4.0",
         source=dict(outlet="ESPN", date="Oct 30", link="https://www.espn.com/f1/story/_/id/50250142/mexico-city-grand-prix-2026-race-f1-start-s-how-watch-schedule-tv-channel-live-stream-predictions")),
]
BRIEFS_P2 = [
    dict(cat="Tech", title="Xreal's Android XR glasses get a launch discount",
         text="Xreal Aura now starts at $1,099 instead of $1,279 until the end of the year. Gemini is built in.",
         price="From $1,099",
         photo=P + "xreal_aura.jpg", credit="Image: XREAL",
         source=dict(outlet="XREAL", date="Oct 30", link="https://www.xreal.com/aura")),
    dict(cat="Space", title="A satellite spotted a skull-shaped island in Antarctica",
         text="On Vega Island, ice, rock and a glacier form a smirking skull. It looks toward Devil Island.",
         photo=P + "vega_island.jpg", credit="Vega Island, Oct 10, 2026 | NASA Earth Observatory / Public domain",
         source=dict(outlet="NASA", date="Oct 30", link="https://science.nasa.gov/earth/earth-observatory/vega-island-frozen-in-fright/")),
    dict(cat="Drops", title="The Kobe 3 Low 'Mamba Eterno' just dropped",
         text="A Day of the Dead tribute with flower graphics on the see-through cage, plus Air Zoom cushioning.",
         price="Out Oct 30 on SNKRS: $190",
         photo=P + "kobe3_mamba_eterno.jpg", credit="Image: Nike",
         source=dict(outlet="Nike SNKRS", date="Oct 30", link="https://www.nike.com/launch/t/kobe-3-low-protro-mamba-eterno")),
]
BRIEFS_P3 = [
    dict(cat="Drops", title="A Space Jam Jordan 11 for baseball",
         text="The Jordan 11 MCS cleat marks 30 years of the Space Jam film.",
         price="Nov 5 on SNKRS: $225",
         photo=P + "j11_space_jam.jpg", credit="Image: Nike",
         source=dict(outlet="Nike SNKRS", date="Oct 30", link="https://www.nike.com/launch/t/jordan-11-mcs-space-jam-black")),
    dict(cat="Space", title="A 4.1-billion-year-old piece of Mars found in the Sahara",
         text="The 800-gram Teghaza 001, found in 2022, is one of the three oldest Mars meteorites ever found on Earth.",
         photo=P + "mars_meteorite.jpg", credit="Slice of Teghaza 001 | NASA/JPL-Caltech / Public domain",
         source=dict(outlet="NASA", date="Oct 29", link="https://www.nasa.gov/solar-system/planets/mars/nasa-funded-study-details-one-of-oldest-mars-meteorites-ever-found/")),
    dict(cat="Space", title="NASA asks companies for ideas to save Hubble",
         text="Hubble is slowly sinking and may re-enter around 2033-2034. Companies can pitch a boost until Nov 30.",
         photo=P + "hubble.jpg", credit="Hubble Space Telescope, 1997 | NASA / Public domain",
         source=dict(outlet="NASA", date="Oct 30", link="https://science.nasa.gov/missions/hubble/nasa-explores-potential-commercial-servicing-for-hubble-telescope/")),
]
BRIEFS = [BRIEFS_P1, BRIEFS_P2, BRIEFS_P3]

HOOK = "3 things that actually happened this week"

_src = [(i["source"]["outlet"], i["source"]["link"]) for i in ITEMS] + [(b["source"]["outlet"], b["source"]["link"]) for pg in BRIEFS for b in pg]
_sources = "\n".join(f"- {o}: {l}" for o, l in _src)
_photos = "\n".join(f"- {i['credit']}\n- {i['explain_credit']}" for i in ITEMS) + "\n" + "\n".join(
    f"- {b['title']}: {b['credit']}" for pg in BRIEFS for b in pg)
_lines = ("Scientists built a robot hand that walks on its fingers.\n"
          "A man opened trading cards on the wing of a flying plane.\n"
          "A $1 million lottery ticket sat in a wallet for two months.")

NEWS = [dict(
    title="This robot hand walks on its own fingers 🖐️ Real news #shorts",
    hook=HOOK, items=ITEMS, briefs=BRIEFS,
    description=("The Noggin Times: 3 real stories from this week. Which one is the wildest?\n\n" + _lines + "\n\nSources:\n" + _sources +
                 "\n\nPhotos (Wikimedia Commons, NASA and brand press images):\n" + _photos +
                 "\n\n#shorts #news #crazynews #didyouknow #noggin"),
    caption=("3 things that actually happened this week. Swipe through The Noggin Times.\n\n" + _lines + "\n\nSources:\n" + _sources +
             "\n\nPhotos: Wikimedia Commons (NearEMPTiness, Ank Kumar, Tech. Sgt. Joseph Harwood, Dave Bushell, Tony Webster, WMrapids, "
             "Liauzh; licences credited on each slide), NASA / ESA / CSA / STScI / JPL-Caltech, and press images from Nike and XREAL."
             "\n\n#news #crazynews #didyouknow #noggin #thenoggintimes"),
)]
