# Sample "Noggin Times" Short with fine print + In Brief sidebar. Every fact checked 2026-10-27.
HOOK = "2 things that actually happened this month"
DATE = "Wednesday, October 28, 2026"
ITEMS = [
    dict(text="A man left Chile on foot in 1998. He just made it home to England. 28 years later.",
         detail="Karl Bushby walked across four continents, then swam the English Channel to finish his trip home.",
         body=("The former British paratrooper set off from Chile on November 1, 1998, on what he planned as an unbroken walk home.\n"
               "He swam from France for about 20 hours, spread over three days, and came ashore at Shakespeare Beach near Dover on October 5. "
               "About 250 miles of walking were left between him and his mother's home in Hull."),
         photo="assets/photos/road.jpg", credit="Patagonia, Chile | Vincent van Zeijst / CC BY-SA 3.0",
         explain_photo="assets/photos/dover.jpg", explain_credit="Dover, England | kallerna / CC BY-SA 4.0",
         source=dict(outlet="Fox News", date="October 10, 2026",
                     headline="Veteran walked across four continents and just swam the English Channel to return home",
                     url="foxnews.com", link="https://foxnews.com/travel/veteran-walked-across-four-continents-swam-english-channel-return-home")),
    dict(text="Divers just found what may be the oldest shipwreck ever. It sank up to 4,700 years ago.",
         detail="The wreck lies about 30 metres down near Kekova Island, off Turkey's Antalya coast.",
         body=("No wood survived, so the date comes from its cargo: more than 30 clay storage jars from the Early Bronze Age. "
               "Experts are still testing whether they held olive oil, wine or tree resin.\n"
               "Turkey's culture minister announced the find. The previous record holder, found near Dokos in Greece, is dated to around 2200 BC."),
         photo="assets/photos/kekova.jpg", credit="Kekova, Turkey | Tanya Dedyukhina / CC BY 3.0",
         source=dict(outlet="Al Jazeera", date="October 14, 2026",
                     headline="World's oldest shipwreck found off coast of Turkiye",
                     url="aljazeera.com", link="https://aljazeera.com/news/2026/10/14/worlds-oldest-shipwreck-found-off-coast-of-turkiye")),
]
BRIEFS = [
    dict(cat="Tech", title="Tesla's new Roadster hits 0-60 mph in one second",
         text="Revealed in Texas, it uses cold-gas thrusters and can hop over cars. Range: 300 miles. Deliveries planned for 2028.",
         price="Reservation: $50,000",
         photo="assets/photos/briefs/roadster.jpg", credit="Earlier prototype | Smnt / CC BY-SA 4.0",
         source=dict(outlet="TechCrunch", date="Oct 15", link="https://techcrunch.com/2026/10/15/tesla-reveals-spacex-powered-roadster-that-flies-and-falls-with-style/")),
    dict(cat="Drops", title="Union x Nike Dunks with heels that fold down",
         text="Three colourways turn into slip-on mules. Out Oct 30 at Union stores and online.",
         price="Price: $135",
         photo="assets/photos/briefs/dunk.jpg", credit="A Nike Dunk Low | Quimacian / CC BY-SA 4.0",
         source=dict(outlet="Sole Retriever", date="Oct 27", link="https://www.soleretriever.com/news/articles/union-x-nike-dunk-low-natural-selection-collection-release-date-october-2026")),
    dict(cat="F1", title="Antonelli can win the title in Mexico on Sunday",
         text="The Mercedes driver won in Austin and leads by 123 points. Ninth place or better on Nov 1 seals it.",
         photo="assets/photos/briefs/f1.jpg", credit="Mercedes W16, 2025 | Liauzh / CC BY-SA 4.0",
         source=dict(outlet="Sky Sports", date="Oct 26", link="https://www.skysports.com/f1/news/13603683/kimi-antonelli-f1-title-permutations-how-mercedes-driver-can-win-2026-formula-1-drivers-championship-at-mexico-city-gp-on-sunday")),
    dict(cat="Votes", title="Portugal's 2027 budget faces its first vote",
         text="Parliament debates the State Budget on Oct 27 and 28. The final vote is set for Nov 24.",
         photo="assets/photos/briefs/parliament.jpg", credit="Sao Bento Palace, Lisbon | Jose Manuel / CC BY-SA 3.0",
         source=dict(outlet="DN / Lusa", date="Sep 23", link="https://www.dn.pt/economia/proposta-de-oramento-do-estado-debatido-na-generalidade-a-27-e-28-de-outubro-e-votada-a-24-novembro")),
]
