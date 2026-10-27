# Sample "REAL OR FAKE?" news Short, v2. Sources checked 2026-10-27.
ITEMS = [
    dict(text="A man left Chile on foot in 1998. He just made it back to England, 28 years later.",
         photo="assets/photos/road.jpg", credit="Patagonia, Chile  |  Vincent van Zeijst / CC BY-SA 3.0",
         explain_photo="assets/photos/dover.jpg", explain_credit="Dover, England  |  kallerna / CC BY-SA 4.0",
         real=True,
         source=dict(outlet="Fox News", date="October 10, 2026",
                     headline="Veteran walked across four continents and just swam the English Channel to return home",
                     url="foxnews.com")),
    dict(text="Scientists found a planet made of solid gold orbiting our Sun.",
         photo="assets/photos/gold.jpg", credit="James St. John / CC BY 2.0",
         real=False,
         fix="No gold planet exists. But NASA's Psyche probe is flying to a metal-rich asteroid.",
         fix_photo="assets/photos/psyche.png", fix_credit="NASA"),
    dict(text="Divers found a ship that sank up to 4,700 years ago.",
         photo="assets/photos/kekova.jpg", credit="Kekova, Turkey  |  Tanya Dedyukhina / CC BY 3.0",
         real=True,
         source=dict(outlet="Al Jazeera", date="October 14, 2026",
                     headline="World's oldest shipwreck found off coast of Turkiye",
                     url="aljazeera.com")),
]
MUSIC = None   # synthesized ambient bed, no songs

DESCRIPTION = """Real or fake? Comment your score 👇

Sources:
Fox News: https://foxnews.com/travel/veteran-walked-across-four-continents-swam-english-channel-return-home
Al Jazeera: https://aljazeera.com/news/2026/10/14/worlds-oldest-shipwreck-found-off-coast-of-turkiye

Photos (Wikimedia Commons):
Patagonia road: Vincent van Zeijst, CC BY-SA 3.0
White Cliffs of Dover: kallerna, CC BY-SA 4.0
Gold nugget: James St. John, CC BY 2.0
Psyche spacecraft: NASA, public domain
Kekova, Turkey: Tanya Dedyukhina, CC BY 3.0

#shorts #news #realorfake #didyouknow #noggin"""
