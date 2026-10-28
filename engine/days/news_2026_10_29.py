# The Noggin Times, Thursday Oct 29, 2026. Every fact checked against the linked article on 2026-10-28.
P = "assets/photos/2026-10-29/"

ITEMS = [
    dict(text="A bear broke into a family's car in Alaska, got locked inside and wrecked it.",
         detail="Police in Juneau had to use a rope to pull open the Subaru's door and let the trapped black bear out.",
         body=("The bear seems to have opened the unlocked door by itself, then got stuck when it slammed shut behind it. "
               "By the time it was freed after midnight, the inside of the car was destroyed, and it had left some bear poo behind.\n"
               "The owner joked that Subaru makes a good car, because the bear could not get out. "
               "The family later learned the bear had broken into three cars that night."),
         numbers=[("3", "cars it broke into that night"), ("1", "car it got locked inside"),
                  ("1 month", "since a bear raided a neighbour's car")],
         photo=P + "bear_road.jpg", credit="Black bear, Southeast Alaska | Gillfoto / CC BY-SA 4.0",
         explain_photo=P + "trash_bear.jpg", explain_credit="Black bear vs a bear-proof bin | Just Step Sideways / CC BY-SA 4.0",
         source=dict(outlet="UPI", date="October 27, 2026",
                     headline="Watch: Bear gets trapped inside Alaska family's car, destroys interior",
                     url="upi.com", link="https://www.upi.com/Odd_News/2026/10/27/bear-subaru-juneau-alaska/2201793113056/")),
    dict(text="A San Francisco startup offered people $20 an hour to take its robot dogs for walks.",
         detail="Walkers had to steer the robots around the city for at least four hours and carry home any that broke down.",
         body=("The company, Dimensional, posted the job in a Bay Area group on Facebook and later deleted it. "
               "Walkers had to be able to lift about 33 pounds of robot, and its office sits, fittingly, in the Dogpatch neighbourhood.\n"
               "The founder said AI was still worse than humans at controlling the robots, so the walks gather data. "
               "Each robot dog was bought from Chinese maker Unitree for $2,000."),
         numbers=[("$20", "an hour to walk a robot dog"), ("4-6 hrs", "per walking shift"),
                  ("33 lb", "robot you may have to carry"), ("$2,000", "price of each robot dog")],
         photo=P + "unitree_go2.jpg", credit="A Unitree Go2 robot dog | Adi Iacob, Ovidiu Popica / CC BY 3.0",
         explain_photo=P + "dogpatch.jpg", explain_credit="Dogpatch, San Francisco | Clyde Charles Brown / CC BY-SA 4.0",
         source=dict(outlet="UPI", date="October 28, 2026",
                     headline="San Francisco company offering $20 an hour to walk robot dogs",
                     url="upi.com", link="https://www.upi.com/Odd_News/2026/10/28/dimension-san-francisco-robot-dog-walkers/9021793207168/")),
    dict(text="A capybara escaped an English zoo in March. Seven months later, she is still on the run.",
         detail="Wildlife cameras just snapped Samba near Marwell Zoo, but keepers are taking it slow to win her back.",
         body=("Samba and a second capybara, Tango, got out less than a day after arriving at the zoo near Winchester. "
               "Tango was found nearby quickly, but Samba turned up days later in the village of Owslebury.\n"
               "The zoo knows the area she is in. To avoid scaring her away, the team added more cameras and set up a feeding spot "
               "to keep her close. Capybaras are the largest rodents in the world."),
         numbers=[("7", "months on the loose"), ("<24 hrs", "after arriving, she escaped"),
                  ("2", "capybaras escaped, 1 still free"), ("No. 1", "biggest rodent on Earth")],
         photo=P + "capybara.jpg", credit="Capybaras, Sao Paulo, Brazil | Clodomiro Esteves Junior / CC BY-SA 4.0",
         explain_photo=P + "owslebury.jpg", explain_credit="Owslebury, Hampshire | Stephen McKay / CC BY-SA 2.0",
         source=dict(outlet="UPI", date="October 28, 2026",
                     headline="Capybara caught on camera 7 months after zoo escape",
                     url="upi.com", link="https://www.upi.com/Odd_News/2026/10/28/marwell-zoo-samba-capybara-sighting/1521793199576/")),
]

BRIEFS_P1 = [
    dict(cat="Votes", title="Portugal's 2027 budget passes its first vote",
         text="Approved Oct 28: PSD and CDS-PP voted for, PS abstained. The final vote is set for Nov 24.",
         photo="assets/photos/briefs/parliament.jpg", credit="Sao Bento Palace, Lisbon | Jose Manuel / CC BY-SA 3.0",
         source=dict(outlet="Euronews", date="Oct 28", link="https://pt.euronews.com/2026/10/28/oe2027-aprovado-na-generalidade-com-abstencao-do-ps-em-clima-de-contestacao-ao-governo")),
    dict(cat="Strikes", title="CP train strike hits Portugal on Friday",
         text="Ticket inspectors and ticket office staff walk out on Oct 30. CP warns of delays Oct 29 to 31 and offers refunds.",
         photo=P + "alfa_pendular.jpg", credit="CP Alfa Pendular, Porto | Rob Dammers / CC BY 2.0",
         source=dict(outlet="DN / Lusa", date="Oct 27", link="https://www.dn.pt/sociedade/cp-alerta-para-perturbaes-na-circulao-a-partir-de-quinta-feira-devido-greve")),
    dict(cat="Tech", title="Apple's MacBook Pro gets OLED and touch",
         text="The first Mac with touch, a tandem OLED screen and up to 24 hours of battery. In stores Nov 6.",
         price="From: $2,899",
         photo=P + "mbp_proled.jpg", credit="Image: Apple",
         source=dict(outlet="Apple Newsroom", date="Oct 28", link="https://www.apple.com/newsroom/2026/10/apple-unveils-groundbreaking-macbook-pro-with-proled-xdr-display/")),
]
BRIEFS_P2 = [
    dict(cat="Space", title="Rocket chunk may have landed in a Minnesota field",
         text="Deputies found an 11-foot metal object in a cornfield on Oct 14. Experts think it is from a Chinese rocket launched Sept 14.",
         photo=P + "zhuque2e.jpg", credit="Zhuque-2E, May 2026 | Brainandforce / CC BY 4.0",
         source=dict(outlet="UPI", date="Oct 26", link="https://www.upi.com/Odd_News/2026/10/26/minnesota-space-object-chinese-landspace-rocket/6381793035327/")),
    dict(cat="Drops", title="Nike's Alphafly 4 gets a wide release",
         text="Nike's newest marathon super shoe dropped in limited pairs in September. Now it lands for everyone.",
         price="Oct 29: $280",
         photo=P + "alphafly4.jpg", credit="Image: Nike",
         source=dict(outlet="Complex", date="Oct 27", link="https://www.complex.com/sneakers/a/victor-deng/sneaker-release-guide-10-27-26-air-jordan-14-forest-green")),
    dict(cat="Tech", title="The iPad mini switches to OLED",
         text="Thinner, lighter, water and dust resistant, with the A20 Pro chip. Pre-orders Oct 28, in stores Nov 6.",
         price="From: $699",
         photo=P + "ipad_mini.jpg", credit="Image: Apple",
         source=dict(outlet="Apple Newsroom", date="Oct 26", link="https://www.apple.com/newsroom/2026/10/apple-gives-ipad-mini-its-biggest-update-ever/")),
]
BRIEFS_P3 = [
    dict(cat="F1", title="Antonelli could be F1's youngest ever champion",
         text="The 20-year-old won his 9th race of 2026 in Austin. He can clinch the title at the Mexico City GP.",
         photo="assets/photos/briefs/f1_antonelli_2026.jpg", credit="Antonelli, Bahrain 2026 | Liauzh / CC BY-SA 4.0",
         source=dict(outlet="AP", date="Oct 25", link="https://www.ajc.com/news/2026/10/kimi-antonelli-wins-dominant-us-grand-prix-and-tightens-his-grip-on-historic-f1-title-chase/")),
    dict(cat="Drops", title="Adidas restocks its $500 marathon shoe",
         text="The Adios Pro Evo 3, worn for the first pair of sub-2-hour marathons, is back before the NYC Marathon.",
         price="Oct 29: $500",
         photo=P + "adios_evo3.jpg", credit="Image: adidas",
         source=dict(outlet="Complex", date="Oct 27", link="https://www.complex.com/sneakers/a/victor-deng/sneaker-release-guide-10-27-26-air-jordan-14-forest-green#adios")),
    dict(cat="Tech", title="Apple's new iMac gets the M6 chip",
         text="Seven colours, Wi-Fi 7 and a 24-inch 4.5K screen. Pre-orders Oct 28, in stores Nov 6.",
         price="From: $1,499",
         photo=P + "imac_m6.jpg", credit="Image: Apple",
         source=dict(outlet="Apple Newsroom", date="Oct 27", link="https://www.apple.com/newsroom/2026/10/apple-unveils-new-imac-with-m6/")),
]
BRIEFS = [BRIEFS_P1, BRIEFS_P2, BRIEFS_P3]

HOOK = "3 things that actually happened this week"

_src = [(i["source"]["outlet"], i["source"]["link"]) for i in ITEMS] + [(b["source"]["outlet"], b["source"]["link"]) for pg in BRIEFS for b in pg]
_sources = "\n".join(f"- {o}: {l}" for o, l in _src)
_photos = "\n".join(f"- {i['credit']}\n- {i['explain_credit']}" for i in ITEMS) + "\n" + "\n".join(
    f"- {b['title']}: {b['credit']}" for pg in BRIEFS for b in pg)
_lines = ("A bear locked itself in a family's car and trashed it.\n"
          "A startup paid $20 an hour to walk robot dogs.\n"
          "A zoo capybara has been on the run for 7 months.")

NEWS = [dict(
    title="A bear got LOCKED inside a car 🐻 This really happened #shorts",
    hook=HOOK, items=ITEMS, briefs=BRIEFS,
    description=("The Noggin Times: 3 real stories from this week. Which one is the wildest?\n\n" + _lines + "\n\nSources:\n" + _sources +
                 "\n\nPhotos (Wikimedia Commons and brand press images):\n" + _photos +
                 "\n\n#shorts #news #crazynews #didyouknow #noggin"),
    caption=("3 things that actually happened this week. Swipe through The Noggin Times.\n\n" + _lines + "\n\nSources:\n" + _sources +
             "\n\nPhotos: Wikimedia Commons (Gillfoto, Just Step Sideways, Adi Iacob & Ovidiu Popica, Clyde Charles Brown, "
             "Clodomiro Esteves Junior, Stephen McKay, Jose Manuel, Rob Dammers, Brainandforce, Liauzh; CC licences, credited on each slide) "
             "and press images from Apple, Nike and adidas.\n\n#news #crazynews #didyouknow #noggin #thenoggintimes"),
)]
