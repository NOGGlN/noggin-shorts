# The Noggin Times, Sunday Nov 1, 2026. Every fact checked against the linked article on 2026-10-30.
P = "assets/photos/2026-11-01/"

ITEMS = [
    dict(text="Dozens of people protested outside an insurance company's headquarters. Their demand: get rid of its fluffy mascot.",
         detail="The 'Liberty Biberty' protest at Liberty Mutual in Boston was organised by a 19-year-old YouTuber.",
         body=("It all started with his YouTube video 'Death of Mascots', where he complained about the fluffy yellow character. "
               "The video passed 600,000 views.\n"
               "On Sunday afternoon, protesters gathered outside Liberty Mutual's Boston headquarters holding signs that read "
               "'Liberty from Biberty' and crossed-out pictures of the mascot. The organiser livestreamed it and promised to keep it "
               "peaceful. One lone counter-protester turned up dressed as Biberty."),
         numbers=[("Dozens", "of protesters outside the HQ"), ("19", "age of the organiser"),
                  ("600K+", "views on his YouTube video"), ("1", "counter-protester, in costume")],
         photo=P + "lm_hq.jpg", credit="Liberty Mutual headquarters, Boston | ajay_suresh / CC BY 4.0",
         explain_photo=P + "lm_tower.jpg", explain_credit="Liberty Mutual Tower, Boston | Daderot / CC0",
         source=dict(outlet="UPI", date="October 28, 2026",
                     headline="Dozens protest against 'Liberty Biberty' in Boston",
                     url="upi.com", link="https://www.upi.com/Odd_News/2026/10/28/liberty-biberty-protest/5661793206185/")),
    dict(text="A power bank exploded into flames right next to a woman on her sofa. A camera caught all of it.",
         detail="She wasn't hurt, and the people at home put the fire out before it spread.",
         body=("The video was filmed inside a home in Vacaville, California, and shared by the city's fire department on Facebook.\n"
               "Firefighters are using it as a warning about lithium-ion batteries. Their advice: be careful with cheap, off-brand "
               "power banks sold online, look for UL or ETL safety marks, keep chargers off things that can burn, always use the "
               "right cable, and watch out for swelling or too much heat."),
         numbers=[("0", "people hurt"), ("2", "safety marks to look for: UL and ETL")],
         photo=P + "powerbank.jpg", credit="A phone on a power bank | Santeri Viinamaki / CC BY-SA 4.0",
         explain_photo=P + "vacaville.jpg", explain_credit="Vacaville, California | Basil D Soufi / CC BY-SA 3.0",
         source=dict(outlet="UPI", date="October 29, 2026",
                     headline="Watch: Portable phone charger explosion caught on camera",
                     url="upi.com", link="https://www.upi.com/Odd_News/2026/10/29/vacaville-phone-charger-fire/5681793299314/")),
    dict(text="A man now owns more than 1,000 different spreadsheet programs. Yes, spreadsheets.",
         detail="He already holds the Guinness World Record for the biggest collection of physical spreadsheet software.",
         body=("Ariel Fischman, a financial advisor, first set the record in 2018 with 506 different copies. Now he says he has "
               "more than 1,000.\n"
               "He started collecting after writing about the history of electronic accounting. The first spreadsheet, VisiCalc, was "
               "made in 1978 by Harvard student Dan Bricklin and his friend Bob Frankston, and it set the format Microsoft Excel later "
               "made famous. Fischman says everyone loves spreadsheets, some just haven't noticed yet."),
         numbers=[("1,000+", "spreadsheet programs he owns"), ("506", "copies when he set the record in 2018"),
                  ("1978", "the year VisiCalc was invented"), ("2", "inventors of the first spreadsheet")],
         photo=P + "apple2.jpg", credit="Apple II, Computer History Museum | The wub / CC BY-SA 4.0",
         explain_photo=P + "visicalc.jpg", explain_credit="VisiCalc on screen | Gortu / Public domain",
         source=dict(outlet="UPI", date="October 28, 2026",
                     headline="Spreadsheet fan's software collection surpasses 1,000 programs",
                     url="upi.com", link="https://www.upi.com/Odd_News/2026/10/28/guinness-world-records-spreadsheet-software/4681793200201/")),
]

BRIEFS_P1 = [
    dict(cat="Space", title="NASA's Lucy reaches Jupiter's Trojan asteroids",
         text="It is the first spacecraft ever to get there, after 2.2 billion miles. Its first Trojan flyby is on Aug 11, 2027.",
         photo=P + "lucy.jpg", credit="Lucy spacecraft, illustration | NASA",
         source=dict(outlet="NASA", date="Oct 28", link="https://science.nasa.gov/blogs/lucy/2026/10/28/nasas-lucy-reaches-trojan-asteroid-region-5-years-after-launch/")),
    dict(cat="Drops", title="The SHAI 001 now comes with laces",
         text="Shai Gilgeous-Alexander's shoe swaps its zipper for laces, in the 'Flare' colourway.",
         price="Out Oct 29 on SNKRS: $120",
         photo=P + "shai001_nike.jpg", credit="Image: Nike",
         source=dict(outlet="Nike SNKRS", date="Oct 30", link="https://www.nike.com/launch/t/shai-001-lace-up-flare")),
    dict(cat="Music", title="U2 will play Lisbon in May 2027",
         text="The show is at Estadio da Luz on May 27, 2027. Fan club presale is Nov 2, general sale Nov 6.",
         photo=P + "estadio_luz.jpg", credit="Estadio da Luz, Lisbon | Florent Dusonchet / CC BY 2.0",
         source=dict(outlet="CNN Portugal", date="Oct 29", link="https://cnnportugal.iol.pt/u2/u2-em-portugal/u2-regressam-a-portugal-em-maio-de-2027-concerto-acontece-no-estadio-da-luz/20261029/6ae33a12d34e53c759c7883f")),
]
BRIEFS_P2 = [
    dict(cat="Space", title="Astronauts add a 7th new solar array to the ISS",
         text="The Oct 29 spacewalk lasted 7 hours, 11 minutes. The 8th and last goes up Nov 5, adding up to 30% more power.",
         photo=P + "iss_eva.jpg", credit="Spacewalk, Oct 29, 2026 | NASA",
         source=dict(outlet="NASA", date="Oct 29", link="https://www.nasa.gov/blogs/spacestation/2026/10/29/spacewalkers-install-roll-out-solar-arrays-for-power-generation/")),
    dict(cat="Drops", title="The women's Air Jordan 11 'Magic Ball' is coming",
         text="A new women's Air Jordan 11 colourway called Magic Ball.",
         price="Nov 11 on SNKRS: $235",
         photo=P + "aj11_magic_ball_nike.jpg", credit="Image: Nike",
         source=dict(outlet="Nike SNKRS", date="Oct 30", link="https://www.nike.com/launch/t/womens-air-jordan-11-magic-ball")),
    dict(cat="Travel", title="America's newest national park is full of rock towers",
         text="Chiricahua in Arizona became a national park in October. A volcano made its spires 27 million years ago.",
         photo=P + "chiricahua.jpg", credit="Hoodoos, Chiricahua, Arizona | SonoranDesertNPS / CC BY 2.0",
         source=dict(outlet="NASA Earth Observatory", date="Oct 27", link="https://science.nasa.gov/earth/earth-observatory/the-land-of-the-standing-up-rocks/")),
]
BRIEFS_P3 = [
    dict(cat="Earth", title="A giant iceberg is bumping into a remote island",
         text="Iceberg A-81, about 600 square miles, broke off Antarctica in 2023. It has drifted 1,400 miles to South Georgia.",
         photo=P + "a81.jpg", credit="Iceberg A-81, Oct 20, 2026 | NASA Earth Observatory / Public domain",
         source=dict(outlet="NASA Earth Observatory", date="Oct 27", link="https://science.nasa.gov/earth/earth-observatory/a-81-reaches-south-georgia/")),
    dict(cat="Drops", title="Nike's Air Max 97 gets college colours",
         text="Five pairs are named after US universities, like this 'Clark Atlanta University' in Gym Red and Black.",
         price="Price: $190",
         photo=P + "am97_cau_nike.jpg", credit="Image: Nike",
         source=dict(outlet="Nike SNKRS", date="Oct 30", link="https://www.nike.com/launch/t/air-max-97-clark-atlanta-university-gym-red-and-black")),
    dict(cat="Drops", title="The Nike Blazy gets a 'Tie-Dye' look",
         text="A new Blazy colourway in Dark Sulfur and Sail.",
         price="Nov 4 on SNKRS: $105",
         photo=P + "blazy_nike.jpg", credit="Image: Nike",
         source=dict(outlet="Nike SNKRS", date="Oct 30", link="https://www.nike.com/launch/t/blazy-tie-dye-dark-sulfur-and-sail")),
]
BRIEFS = [BRIEFS_P1, BRIEFS_P2, BRIEFS_P3]

HOOK = "3 things that actually happened this week"

_src = [(i["source"]["outlet"], i["source"]["link"]) for i in ITEMS] + [(b["source"]["outlet"], b["source"]["link"]) for pg in BRIEFS for b in pg]
_sources = "\n".join(f"- {o}: {l}" for o, l in _src)
_photos = "\n".join(f"- {i['credit']}\n- {i['explain_credit']}" for i in ITEMS) + "\n" + "\n".join(
    f"- {b['title']}: {b['credit']}" for pg in BRIEFS for b in pg)
_lines = ("Dozens of people protested an insurance company's fluffy mascot.\n"
          "A power bank burst into flames next to a woman on her sofa.\n"
          "A man owns more than 1,000 spreadsheet programs.")

NEWS = [dict(
    title="People really protested a fluffy mascot 🪧 Real news #shorts",
    hook=HOOK, items=ITEMS, briefs=BRIEFS,
    description=("The Noggin Times: 3 real stories from this week. Which one is the wildest?\n\n" + _lines + "\n\nSources:\n" + _sources +
                 "\n\nPhotos (Wikimedia Commons, NASA and brand press images):\n" + _photos +
                 "\n\n#shorts #news #crazynews #didyouknow #noggin"),
    caption=("3 things that actually happened this week. Swipe through The Noggin Times.\n\n" + _lines + "\n\nSources:\n" + _sources +
             "\n\nPhotos: Wikimedia Commons (ajay_suresh, Daderot, Santeri Viinamaki, Basil D Soufi, The wub, Gortu, Florent Dusonchet, "
             "SonoranDesertNPS; licences credited on each slide), NASA, and press images from Nike."
             "\n\n#news #crazynews #didyouknow #noggin #thenoggintimes"),
)]
