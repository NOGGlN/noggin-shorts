# Sample "REAL OR FAKE?" news Short. Sources checked 2026-10-27.
ITEMS = [
    dict(text="A man left Chile on foot in 1998. He just made it back to England, 28 years later.",
         emoji="🚶", real=True,
         source=dict(outlet="Fox News", date="October 10, 2026",
                     headline="Veteran walked across four continents and just swam the English Channel to return home",
                     url="foxnews.com/travel")),
    dict(text="Scientists found a planet made of solid gold orbiting our Sun.",
         emoji="🪐", real=False,
         fix="There is no gold planet. But NASA's Psyche probe is on its way to a metal-rich asteroid."),
    dict(text="Divers found a ship that sank up to 4,700 years ago.",
         emoji="🚢", real=True,
         source=dict(outlet="Al Jazeera", date="October 14, 2026",
                     headline="World's oldest shipwreck found off coast of Turkiye",
                     url="aljazeera.com/news")),
]

LINKS = [
    "https://foxnews.com/travel/veteran-walked-across-four-continents-swam-english-channel-return-home",
    "https://aljazeera.com/news/2026/10/14/worlds-oldest-shipwreck-found-off-coast-of-turkiye",
]
