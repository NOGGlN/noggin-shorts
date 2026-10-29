# The Noggin Times, Friday Oct 30, 2026. Every fact checked against the linked article on 2026-10-29.
P = "assets/photos/2026-10-30/"

ITEMS = [
    dict(text="A deer crashed into a laundromat, ran across the washing machines, then escaped through the window it broke.",
         detail="Security cameras at a North Carolina laundromat caught the whole thing on Tuesday.",
         body=("It happened at the Wishy Washy Laundry on South Main Street in Winston-Salem. The deer ran into a woman who was "
               "leaving, smashed through a window, then ran through the shop and climbed on top of the washers and dryers.\n"
               "Owner Corey Pendergrass called it a one in a million chance and said nobody was hurt. The only major damage was "
               "the window, which a local company fixed later that day."),
         numbers=[("1 in a million", "chance, says the owner"), ("0", "people injured"),
                  ("1", "window smashed, fixed the same day")],
         photo=P + "deer.jpg", credit="White-tailed deer | USFWS Mountain Prairie / Public domain",
         explain_photo=P + "laundromat.jpg", explain_credit="A laundromat in Walden, NY | Daniel Case / CC BY-SA 3.0",
         source=dict(outlet="UPI", date="October 29, 2026",
                     headline="Deer causes chaos inside North Carolina laundromat",
                     url="upi.com", link="https://www.upi.com/Odd_News/2026/10/29/deer-crashes-though-laundromat-winston-salem/5961793290016/")),
    dict(text="Police in Virginia chased a runaway sheep through a neighborhood. Now they are hunting for its owner.",
         detail="Manassas Park officers caught the mystery sheep after a brief 'food pursuit' into someone's backyard.",
         body=("Officers were called to Nancy Street in the Blooms Crossing community on Wednesday after a report of a sheep "
               "on the loose. The department told the story online with running and lettuce emojis.\n"
               "Police joked that no charges have been filed, but they suspect a few outstanding baaa-violations. They still "
               "do not know where the sheep came from, and asked the owner of the four-legged fugitive to call them."),
         numbers=[("0", "charges filed so far"), ("4", "legs on the fugitive"),
                  ("1", "backyard where the chase ended")],
         photo=P + "sheep.jpg", credit="A sheep | Tudor Washington Collins / CC BY 4.0",
         explain_photo=P + "manassas_park.jpg", explain_credit="Manassas Park, Virginia | Mojo Hand / CC BY-SA 4.0",
         source=dict(outlet="UPI", date="October 29, 2026",
                     headline="Mystery sheep leads police on 'food pursuit' in Virginia",
                     url="upi.com", link="https://www.upi.com/Odd_News/2026/10/29/manassas-park-sheep-escape-police/6071793292849/")),
    dict(text="A man rode a motorcycle more than 25 miles down a river. On top of the water.",
         detail="ZXMOTO founder Zhang Xue just set a Guinness World Record on the Chen River in China.",
         body=("He rode a modified MX450 motorcycle 25.3 miles across the surface of the river in Mayang, in Hunan Province, "
               "on Sunday. It earned the record for the longest distance travelled on open water by a modified motorcycle.\n"
               "The bike was fitted with an amphibious ski, so it can be driven on land or on water. On the river, its rear tyre "
               "pushes water backward to move it forward."),
         numbers=[("25.3 mi", "ridden on the river's surface"), ("MX450", "the modified motorcycle"),
                  ("1", "new Guinness World Record")],
         photo=P + "dirt_bike.jpg", credit="A motocross bike | jim simonson / CC BY 2.0",
         explain_photo=P + "mayang.jpg", explain_credit="Mayang, Hunan, China | PanShiBo / CC BY-SA 3.0",
         source=dict(outlet="UPI", date="October 26, 2026",
                     headline="Modified motorcycle takes a 25-mile drive on the water",
                     url="upi.com", link="https://www.upi.com/Odd_News/2026/10/26/guinness-world-records-motorcycle-water/9111793033790/")),
]

BRIEFS_P1 = [
    dict(cat="Drops", title="The Air Jordan 6 'White Infrared' is back",
         text="One of the 1991 launch colourways returns with the original shape and Nike Air on the heel.",
         price="Nov 7 on SNKRS: $215",
         photo=P + "aj6_white_infrared.jpg", credit="Image: Nike",
         source=dict(outlet="Nike SNKRS", date="Oct 29", link="https://www.nike.com/launch/t/air-jordan-6-white-infrared-white-and-light-crimson")),
    dict(cat="Votes", title="21 million Americans have already voted in the midterms",
         text="That was the early vote count on Oct 23, per the University of Florida's Election Lab. About 122 million voted in the 2022 midterms.",
         photo=P + "capitol.jpg", credit="US Capitol, Washington | Architect of the Capitol / Public domain",
         source=dict(outlet="NPR", date="Oct 23", link="https://www.wunc.org/2026-10-23/millions-of-americans-have-already-cast-their-votes-for-the-midterms-data-shows")),
    dict(cat="Money", title="The ECB keeps interest rates at 2.5%",
         text="The European Central Bank left all three key rates unchanged on Oct 29. It warned rising energy prices could push inflation up.",
         photo=P + "ecb.jpg", credit="ECB, Frankfurt | Dr. Thomas Liptak / CC BY-SA 4.0",
         source=dict(outlet="CNN Portugal", date="Oct 29", link="https://cnnportugal.iol.pt/bce/taxas-de-juro/bce-mantem-taxas-de-juro/20261029/6ae34812d34e9a786e75e5bf")),
]
BRIEFS_P2 = [
    dict(cat="Space", title="NASA's Artemis III moon rocket takes shape",
         text="The SLS core stage was joined to its twin boosters on Oct 25 inside Kennedy's Vehicle Assembly Building.",
         photo=P + "artemis3_sls.jpg", credit="Artemis III SLS, Kennedy | NASA, Frank Michaux / Public domain",
         source=dict(outlet="NASA", date="Oct 28", link="https://www.nasa.gov/image-article/artemis-iii-sls-core-stage-joins-boosters-at-kennedy/")),
    dict(cat="Strikes", title="Portugal's public sector will strike on Nov 20",
         text="The Frente Comum unions voted for it outside parliament, as 2027 pay rises for the sector are negotiated.",
         photo="assets/photos/briefs/sao_bento_2.jpg", credit="Parliament, Lisbon | Stefan Didam / CC BY-SA 3.0",
         source=dict(outlet="CNN Portugal", date="Oct 27", link="https://cnnportugal.iol.pt/funcao-publica/funcionarios-publicos/frente-comum-anuncia-greve-na-funcao-publica-para-20-de-novembro/20261027/6ae09b0ed34e9a786e75dfc0")),
    dict(cat="Food", title="Guatemala made a record 4,325.9-pound salad",
         text="Chefs mixed a giant fiambre in Guatemala City for a Guinness record, just before All Saints Day on Nov 1.",
         photo=P + "fiambre.jpg", credit="Fiambre, Guatemala | ignacio sagone / CC BY 2.0",
         source=dict(outlet="UPI", date="Oct 29", link="https://www.upi.com/Odd_News/2026/10/29/latam-guatemala-Guinness-world-records-largest-fiambre-salad/8871793291959/")),
]
BRIEFS_P3 = [
    dict(cat="Drops", title="The Kobe 8 'Shanghai Fireworks' returns",
         text="First released in 2013, it is back in Laser Orange with fireworks art and a Nike React foam insert.",
         price="Nov 11 on SNKRS: $200",
         photo=P + "kobe8_shanghai.jpg", credit="Image: Nike",
         source=dict(outlet="Nike SNKRS", date="Oct 29", link="https://www.nike.com/launch/t/kobe-8-protro-shanghai-fireworks-laser-orange-and-safety-orange")),
    dict(cat="Records", title="The world's largest pop-up book is in LA",
         text="Open, it measures 15.41 by 20.01 feet and needs 10 people to turn the pages. It marks the library's 100th birthday.",
         photo=P + "la_library.jpg", credit="Central Library, Los Angeles | Visitor7 / CC BY-SA 3.0",
         source=dict(outlet="UPI", date="Oct 26", link="https://www.upi.com/Odd_News/2026/10/26/guinness-world-records-largest-pop-up-book/9571793036865/")),
    dict(cat="Prices", title="Diesel in Portugal set to rise again next week",
         text="Up about 3.5 cents a litre, to around 2.219 euros. Petrol should drop by about 2 cents.",
         photo=P + "fuel_porto.jpg", credit="Fuel station, Porto | Joehawkins / CC BY-SA 4.0",
         source=dict(outlet="CNN Portugal", date="Oct 29", link="https://cnnportugal.iol.pt/precos-combustiveis/combustiveis/vem-ai-novo-sobe-e-desce-nos-combustiveis-saiba-tudo-aqui/20261029/6ae37765d34e9a786e75e6a0")),
]
BRIEFS = [BRIEFS_P1, BRIEFS_P2, BRIEFS_P3]

HOOK = "3 things that actually happened this week"

_src = [(i["source"]["outlet"], i["source"]["link"]) for i in ITEMS] + [(b["source"]["outlet"], b["source"]["link"]) for pg in BRIEFS for b in pg]
_sources = "\n".join(f"- {o}: {l}" for o, l in _src)
_photos = "\n".join(f"- {i['credit']}\n- {i['explain_credit']}" for i in ITEMS) + "\n" + "\n".join(
    f"- {b['title']}: {b['credit']}" for pg in BRIEFS for b in pg)
_lines = ("A deer crashed through a laundromat and ran across the washers.\n"
          "Police chased a runaway sheep on a 'food pursuit'.\n"
          "A man rode a motorcycle 25 miles on top of a river.")

NEWS = [dict(
    title="A deer crashed a laundromat 🦌 This really happened #shorts",
    hook=HOOK, items=ITEMS, briefs=BRIEFS,
    description=("The Noggin Times: 3 real stories from this week. Which one is the wildest?\n\n" + _lines + "\n\nSources:\n" + _sources +
                 "\n\nPhotos (Wikimedia Commons, NASA and brand press images):\n" + _photos +
                 "\n\n#shorts #news #crazynews #didyouknow #noggin"),
    caption=("3 things that actually happened this week. Swipe through The Noggin Times.\n\n" + _lines + "\n\nSources:\n" + _sources +
             "\n\nPhotos: Wikimedia Commons (USFWS, Daniel Case, Tudor Washington Collins, Mojo Hand, jim simonson, PanShiBo, Architect of the Capitol, "
             "Dr. Thomas Liptak, Stefan Didam, ignacio sagone, Visitor7, Joehawkins; licences credited on each slide), "
             "NASA / Frank Michaux, and press images from Nike.\n\n#news #crazynews #didyouknow #noggin #thenoggintimes"),
)]
