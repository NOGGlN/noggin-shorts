# Noggin Shorts: daily production

This repo holds the Noggin YouTube Shorts video engine (`engine/`) and the rendered videos (`videos/<date>/`).
Videos are published to the NOGGIN YouTube channel through Metricool (brand id `7672444`, timezone Europe/Lisbon).

## Current plan (from Nov 2026): YouTube only, max 18 posts a month
The owner is on Metricool's free plan: at most **20 published posts per calendar month** (every network post counts; failed posts don't).
Owner's cap: **18 a month** (2 below 20, so the limit is never hit and posting never stops). Count before scheduling.
All posts at **16:00 Lisbon**, YouTube only:
- **Monday = Cinematic news Short** ("News job", weekly, `news6.py`, British female voice). Needs the owner's computer for photos.
- **Friday = YouTube Short**, **Wednesday + Saturday = regular YouTube video (16:9)**, made by the "YouTube formats job", rotating
  4 kinds: **Would You Rather (wyr)**, **Battle Royale (royale)**, **Satisfying Bounce (bounce)**, **Road Rules quiz (road)**.
- About 17 posts a month (4-5 news + 12-13 formats). Nothing is posted before 1 Nov 2026.
- Instagram, TikTok, the old daily puzzle Shorts, the daily battle task and the OLD retro-newspaper news look are stopped.
  (The old puzzle and battle sections below are kept for reference only.)

## Reference videos from the owner
When the owner sends a reference video or screenshot, it is INSPIRATION, not something to copy exactly: take its theme, how it talks
(tone, script style), the kind of information it shows and its overall look, then make our own version (own scenarios, own wording,
Noggin branding, no real people's faces, no copied text or images).
- Lifestyle-news reel (Oct 31): "here's the news you missed" tone, calm narrator, cinematic full-screen photos, serif captions,
  "This Week in ..." title card, category collage. -> news6.py.
- Road-rules quiz (Oct 31): top-down illustrated junction, cars labelled "You" and "Car", dotted routes, a card with a place label,
  2 short statement lines and a red "Who has to wait?" question, "Answer in the comments". -> genres/road.py (kind "road").
  Use real rules only (Portugal's Codigo da Estrada by default, the owner is in Portugal); always reveal the answer with the reason.
  Built: `make_genre.py` kind "road" (genres/road.py). Scene types: crossroads_right, crossroads_three (3 cars), crossroads_giveway
  (give-way sign, car from the left), crossroads_stop_right (STOP sign for the car on your right), ambulance_left (siren),
  left_turn, roundabout_enter, roundabout_2lane_exit. Owner wants HARDER questions with 3-4 OPTIONS: each scene has
  "options" (3-4, A-D), "correct" (index), "order" (actor names in the order they go, e.g. ["car","you","car2"]), optional "labels"
  ({"car": "Car A", "car2": "Car B"}), "why". Voice (bf_emma) reads card + options a bit FASTER (road.SPEED 1.12), 5 s countdown,
  1ST/2ND/3RD badges, cars leave in order, then the "Around the world" panel. Short = 1 scene (~40 s), video = up to 10.
  Owner wants each scene to end with "Around the world": `"compare": {"same": [countries], "different": [[country, short note]]}`
  (flags + names on a panel, read by the voice). Major countries only (Spain, France, Germany, Italy, UK, USA, Japan, Brazil, Canada,
  Australia...), and ONLY countries whose rule you are sure of from official sources (e.g. UK Highway Code, US state DMV handbooks,
  Japan Road Traffic Act); leave a country out rather than guess. Remember left-hand-traffic countries mirror left/right rules.
  Sample: `genre_days/_sample_road_short.json` -> `videos/samples/road-quiz-sample.mp4`. In the posting rotation from Nov 2026.
- "Driving Test" worksheet quiz (Oct 31): paper worksheet look, numbered road-marking questions with 3 options and a small road
  drawing each, a countdown circle, then a highlighter stroke + tick on the right answer, "Can you get 7/7?". Not built yet.

## Old daily slots (paused)
Every day, on all three networks (YouTube @NOGGIN, Instagram @nogglndaily, TikTok @noggin.daily):
- **1 news edition at 10:00 on all three** ("News job" at the end): YouTube = the video Short; Instagram + TikTok = the PHOTO carousel.
- **Puzzle 1 at 12:00 on all three.**
- **Puzzle 2 at 16:00 on YouTube, and 18:00 on Instagram + TikTok.**
  (The puzzle scheduled task; its prompt overrides the old 7-a-day rule below. Same video: YouTube Short, Instagram Reel, TikTok video.)
- **1 Noggin Battle at 14:00 on Instagram + TikTok only** ("Battle job" at the end; not on YouTube).
These times come from Metricool's best-time-to-post data (YouTube peaks ~16:00; Instagram and TikTok peak 10:00 and 18:00).
Re-check them about once a month with getBestTimeToPostByNetwork and tell the owner if they shift. Posts with draft=true don't count.

## The daily job, step by step
1. **Find the target day.** Use Metricool `getScheduledPosts` (brandId 7672444, timezone Europe/Lisbon) from tomorrow to +7 days.
   The target day is the EARLIEST day from tomorrow on that has fewer than 7 YouTube posts. Its free slots are the slot times above
   that have no post yet. Let N = number of free slots (1-7). If every day for the next 7 days is full, stop and report "nothing to do".
2. **Write a new day file** `engine/days/day_YYYY_MM_DD.py` modelled on `engine/days/day_2026_10_29.py`, with exactly N videos in PLAN
   (3 questions each: easy, medium, hard) and the 3N generators in GENS.
   - Theme: Gen Z interests (games, apps, social media, music, internet culture, memes, slang, food, space, animals, money, tech, body/science facts).
     Mix **trivia** (`_t`, uses `trivia()`) and **puzzles** (`_p`, uses `scene_q()`) at random. Aim for about half trivia.
   - Every video: exactly ONE trick question (`catch=True`) and put it on level 3 (hard).
   - Every question must be **brand new**: read `engine/data/used_questions.json` and `engine/data/retired.json` first and never reuse a
     question, fact, or near-identical variant. Generator names must be unique, prefix them with `dMMDD_`.
   - Facts must be TRUE and widely agreed. If you are not sure a fact is right, don't use it. Math must be checked by actually computing it.
   - 4 options, all different, one correct. Wrong options must be plausible.
   - **No emoji or special symbols inside question text, options, explanations or banners** (the font can't draw them; they show as boxes).
     Emoji go ONLY in the `emojis` list (the pictures above the question).
   - Do NOT use real people's faces/likeness or brand logos as pictures; naming brands/artists in trivia text is fine.
   - Keep questions short (they must fit 3-4 lines on the card). Banners end with "!".
   - PLAN titles: file title (short, no emoji) and a YouTube title (hooky, 1 emoji, under 90 chars).
3. **Render:** `cd engine && python3 make_day.py days/day_YYYY_MM_DD.py YYYY-MM-DD`
   It refuses duplicates, writes `videos/YYYY-MM-DD/*.mp4` + `manifest.json`, appends to `engine/data/used_questions.json`,
   and saves a check sheet to `/tmp/check_YYYY-MM-DD.png`.
4. **Check:** open the check sheet with the Read tool and look at every card: text fits, nothing overlaps, no boxes instead of characters,
   answer is right. Fix the day file and re-render if anything is off (first remove that date's entries from used_questions.json and
   delete `videos/YYYY-MM-DD/`).
5. **Publish files:** `git add -A && git commit -m "Add YYYY-MM-DD videos" && git push origin HEAD:main` (fetch + rebase first if needed).
6. **Schedule** each video in `manifest.json` with Metricool `createScheduledPost` into the free slots, in order (YouTube body below;
   then ALSO schedule the same video URL at the same time as an Instagram Reel: providers [{"network": "instagram"}],
   "instagramData": {"type": "REEL", "showReelOnFeed": true, "isAiGenerated": false}, text = YouTube title without "#shorts" + "\n\n" +
   description; and as a TikTok video: providers [{"network": "tiktok"}], "tiktokData": {"privacyOption": "PUBLIC_TO_EVERYONE",
   "title": <same title without #shorts>, "disableComment": false, "disableDuet": false, "disableStitch": false,
   "commercialContentThirdParty": false, "commercialContentOwnBrand": false, "autoAddMusic": false, "isAigc": false}, same text):
   blogId `7672444`; `date` = slot time with Lisbon offset; info:
   `{"autoPublish": true, "draft": false, "descendants": [], "firstCommentText": "", "hasNotReadNotes": false,
     "media": [<manifest url>], "mediaAltText": [], "providers": [{"network": "youtube"}],
     "publicationDate": {"dateTime": "YYYY-MM-DDTHH:MM:00", "timezone": "Europe/Lisbon"}, "shortener": false, "smartLinkData": {"ids": []},
     "text": <manifest description>,
     "youtubeData": {"title": <manifest title>, "type": "short", "privacy": "public",
       "tags": ["puzzle", "trivia", "brain teaser", "quiz", "noggin", "shorts"], "category": "ENTERTAINMENT",
       "madeForKids": false, "isAiGeneratedContent": false}}`
   If a post fails, report the error; do not retry more than once.
7. **Report** in one short message: the date filled, the 7 (or N) YouTube titles and the answers.


## News job (cinematic "news you missed") - run by the "Noggin weekly news" scheduled task
One edition a week, **YouTube Short only, Monday 16:00 Lisbon**. Look and tone copy the owner's lifestyle-news reference (theme, not
the exact video): calm "here's the news you missed this week" narration, full-screen real photos with a slow push/pan and warm film
grade, big centred serif captions synced to the voice, "This Week in / The Noggin Times" title card, italic category collage.
Engine: `engine/news6.py` (video), `engine/tts.py` (voice: Kokoro-82M `bf_emma`, British female, Apache 2.0, offline; models
auto-download to engine/assets/voice/, not in git), `engine/make_news6.py` (renders a day). Sample: `days/news6_sample_2026_10_31.py`.
(The old retro newspaper look - news5.py, carousel.py, make_news.py - is retired; do not use it.)

1. **Slot + budget:** Metricool `getScheduledPosts` (brand 7672444, Europe/Lisbon; ranges of max 3 days). Target = the next Monday from
   tomorrow whose 16:00 has no non-draft, non-ERROR YouTube post; if it is more than 3 days away, stop ("nothing"). Count non-draft,
   non-ERROR posts in that calendar month (all networks); if count + 1 > 18, stop ("monthly limit reached").
2. **Stories:** 3 main stories + 2-3 quick briefs from the LAST 7 DAYS, the kind of news the reference shows, for a Gen Z audience:
   new cars and gadgets (launches, prices), places (openings, hotels, restaurants, travel), money and work, health and science,
   space, sport, plus at most one weird-but-harmless story. Pick the most eye-catching as story 1. Not allowed: deaths or serious
   injuries, crime with victims, disasters, war, politics, religion, sex, anything about children, mocking private people.
   Confirm every story and brief by fetching the article on a trusted outlet (AP, Reuters, BBC, The Guardian, NYT, Washington Post,
   CNN, NBC, CBS, ABC, NPR, Sky News, The Independent, Euronews, NASA/ESA, Nature, Science, New Scientist, National Geographic,
   UPI Odd News; for product launches the brand's own newsroom, The Verge, Complex, Hypebeast). Never trust a headline from search
   alone. Every number on screen and in the voice must match the article. Check `engine/data/used_news.json`: never reuse a story.
3. **Photos** (one per story + a second one per story + one per brief, all different): free-license Wikimedia Commons (incl. NASA)
   or, for brand-new products only, the brand's own official product photo (credit "Image: <Brand>"). Never agency/wire photos,
   never blogs' or retailers' photos, never real people's faces as the subject. Photos must be BIG (long side >= 1600 px; ask
   Commons for `iiurlwidth=2560`), or they look soft full-screen. The cloud can't reach Commons: use the built-in browser on the
   owner's computer WITHOUT downloads: in a tab on the photo's own site, javascript_tool fetches the image, draws it on a canvas
   (max 2560 px long side), returns canvas.toDataURL('image/jpeg', 0.9) in chunks of at most 90,000 characters; reassemble and
   decode in the cloud, check it opens, save to `engine/assets/photos/<date>/<name>.jpg`. If the computer can't be reached: STOP.
4. **Day file** `engine/days/news_YYYY_MM_DD.py` with `NEWS = [dict(...)]`, modelled on `days/news6_sample_2026_10_31.py` + news6.py's
   docstring: items (text, detail, vo [2 short spoken lines], photo, credit, explain_photo, explain_credit,
   source {outlet, date, headline, link}), briefs (one list of 2-3, each with cat, title, vo, photo, credit, source), vo_open, cats
   (4 short category words), vo_outro, title (curiosity hook under 60 chars, 1 emoji, ends " #shorts"), description (hook line,
   "Sources:" with outlet + full link for every story and brief, "Photos:" credits, `#shorts #news #thisweek #noggin`).
   vo lines are what the narrator SAYS and the captions SHOW: short, plain, conversational ("Mercedes just showed..."), your own
   words, no copied sentences. Total must stay under 59 s (make_news6 refuses longer).
5. **Render:** `cd engine && python3 make_news6.py days/news_YYYY_MM_DD.py YYYY-MM-DD --stills`, open `/tmp/news6_check_YYYY-MM-DD.jpg`
   (captions fit, photos sharp and right, nothing overlapping), fix, then the real render without --stills.
6. **Publish:** commit + push (fetch/rebase first). Metricool `createScheduledPost` (blogId 7672444) for `videos/YYYY-MM-DD/news_manifest.json`:
   providers [{"network": "youtube"}], publicationDate {dateTime: "YYYY-MM-DDT16:00:00", timezone: "Europe/Lisbon"}, text = description,
   "youtubeData": {"title": title, "type": "short", "privacy": "public", "tags": ["news", "this week", "news you missed", "noggin", "shorts"],
   "category": "ENTERTAINMENT", "madeForKids": false, "isAiGeneratedContent": false}, plus "autoPublish": true, "draft": false,
   "descendants": [], "firstCommentText": "", "hasNotReadNotes": false, "mediaAltText": [], "shortener": false, "smartLinkData": {"ids": []}.
7. **Report:** the Monday filled, title, every story and brief with its source link, posts used / 18 that month.


## Battle job - run by the "Noggin daily battle" scheduled task
A ball battle royale: 16-30 contestants bounce inside a ring with a slowly spinning gap; whoever slips out is OUT, the last one inside wins.
Contestants can be ANYTHING that has an emoji: countries (flag emoji fill the whole ball), foods, animals, snacks, sports, jobs, planets, fruits...
Engine: `engine/battle.py` (physics + drawing + calm sound), `engine/make_battle.py` (CLI). Emoji come from assets/fonts/NotoColorEmoji.ttf.
1. **Target day:** Metricool `getScheduledPosts` from tomorrow to +7 days; earliest day with no non-draft Instagram post at 14:00 Lisbon.
2. **Battle file** `engine/battles/battle_YYYY_MM_DD.py` modelled on `battle_2026_10_30.py`: THEME (unique id, check `engine/data/used_battles.json`
   and never repeat a theme), HEADLINE (2 short ALL-CAPS lines, e.g. ("24 SNACKS ENTER.", "ONLY 1 SURVIVES.")), CONTESTANTS (16-30 (name, emoji),
   names under 16 chars, every emoji different), TITLE (hook under 60 chars, 1 emoji, no #shorts), CAPTION (title, a "pick your winner" line,
   hashtags). Rotate theme types day to day (countries one day, food or animals the next). No real people, no brand logos, nothing about
   politics, religion or war; country battles are just for fun, never call a country weak or bad.
3. **Render:** `cd engine && python3 make_battle.py battles/battle_YYYY_MM_DD.py YYYY-MM-DD` (use `--stills` first for a quick look), then open
   `/tmp/battle_check_YYYY-MM-DD.png` and check: every emoji drawn (no boxes), labels readable, the winner screen correct.
4. **Publish:** commit + push (fetch/rebase first). Then schedule `videos/YYYY-MM-DD/battle-1.mp4` (manifest url) at 14:00 Lisbon:
   a) Instagram Reel: providers [{"network": "instagram"}], "instagramData": {"type": "REEL", "showReelOnFeed": true, "isAiGenerated": false}, text = CAPTION.
   b) TikTok video: providers [{"network": "tiktok"}], "tiktokData": {"privacyOption": "PUBLIC_TO_EVERYONE", "title": TITLE, "disableComment": false,
      "disableDuet": false, "disableStitch": false, "commercialContentThirdParty": false, "commercialContentOwnBrand": false, "autoAddMusic": false,
      "isAigc": false}, text = CAPTION.
   Both with the usual fields ("autoPublish": true, "draft": false, "descendants": [], "firstCommentText": "", "hasNotReadNotes": false,
   "mediaAltText": [], "shortener": false, "smartLinkData": {"ids": []}). If one network fails, still schedule the other and report it.
5. **Report:** date, title, theme, winner, which networks were scheduled.


## YouTube formats job - run by the "Noggin YouTube uploads" scheduled task
Engine: `engine/make_genre.py` + `engine/genres/` (`wyr.py`, `royale.py`, `bounce.py`, `road.py`, shared `gcommon.py`). Each spec is a JSON file in
`engine/genre_days/YYYY_MM_DD_<kind>.json`. Two formats: `"format": "video"` = 1920x1080 regular video, `"format": "short"` = 1080x1920 Short (<60 s).
No background music (owner's rule): only the synthesized sound effects the engine makes.

1. **Slot + budget:** Metricool `getScheduledPosts` (brand 7672444, Europe/Lisbon; ranges of max 3 days, big results -> Python).
   Ignore draft=true and ERROR posts. Next slot = earliest Wednesday/Friday/Saturday from tomorrow with no non-draft YouTube post at 16:00
   (Mondays belong to the weekly news).
   If that day is more than 3 days away: stop ("nothing"). Count non-draft, non-ERROR posts already in that calendar month (all networks);
   if count + 1 > 18: stop ("monthly limit reached"; 18 is the owner's cap, 2 below Metricool's 20). Fri -> `short`, Wed/Sat -> `video`.
2. **Pick the kind:** read the last 3 entries across `videos/*/genre_manifest.json` (by date); use a kind (wyr / royale / bounce / road) that is
   NOT one of those three, so the four rotate. If YouTube analytics (getAnalyticsDataByMetrics YTVV17 + YTVV06) clearly show one kind getting far more
   views, it may appear more often, but never twice in a row.
3. **Write the spec** (fields: kind, format, id (unique, e.g. "wyr-2026-11-04"), title, description, plus the kind's own fields):
   - **wyr**: short = 3-4 questions, video = 10-12. Each `{"a": ["LINE 1", "LINE 2"], "ae": emoji, "b": [...], "be": emoji, "pick": 0|1, "why": "SHORT REASON"}`.
     Fun, harmless, Gen Z dilemmas (superpowers, food, money, school, games, travel, internet life). Lines ALL CAPS, under ~22 characters each,
     no emoji inside text. Every option must be NEW (make_genre.py refuses options in data/used_wyr.json). `why` = Noggin's funny one-liner,
     under ~32 characters. Nothing about real people, politics, religion, violence, sex, or anything gross or scary for kids.
   - **royale**: short = 16 contestants, video = 20-24. `contestants` = [["NAME", emoji]] (names ALL CAPS, max 14 chars, every emoji different),
     `headline` = ["<N> <THINGS>. 1 RING.", "ONLY 1 SURVIVES"], `label` (e.g. "COUNTRY BATTLE"), `pick_line` (e.g. "PICK YOUR COUNTRY NOW"),
     `id` = theme id, never reused (data/used_battles.json). Rotate themes: countries, foods, animals, fruits, sports, planets/space,
     vehicles, desserts, jobs, weather... Country battles are just for fun; never call a country weak or bad.
   - **bounce**: vary every run so no two look the same: `palette` (rainbow / fire / ice / neon), `start` [dx, dy] within ±150, `speed` 560-700,
     `gravity` 900-1200, optional `hook` (2 lines) and `end_text`. `id` unique (data/used_bounce.json).
   - **road**: see "Reference videos" above. short = 1 scene, video = 6-8 scenes (different scene types, getting harder). Every scene:
     3-4 options, correct, order, why, and an "Around the world" compare (major countries only, only rules you are sure of).
     `id` unique. Use real Portuguese rules (Codigo da Estrada). Title e.g. "3 cars, no signs. Who goes first? 🚗".
   - **title**: hook under 60 characters with one emoji; Shorts end with " #shorts". e.g. "Would you rather... you have 4 seconds ⏱️",
     "24 countries enter. Only 1 survives 🌍", "Every bounce it gets BIGGER 😳". **description**: 1-2 hook lines, "Comment your pick 👇",
     then hashtags (#wouldyourather / #battleroyale / #satisfying, plus #noggin; Shorts add #shorts).
4. **Render:** `cd engine && python3 make_genre.py --stills` style check first:
   `python3 make_genre.py genre_days/<file>.json YYYY-MM-DD --stills`, open `/tmp/genre_check_YYYY-MM-DD_<kind>.jpg` with Read
   (text fits, no emoji boxes, nothing overlapping), fix the spec if needed, then the real render without `--stills`.
5. **Publish:** `git add -A`, commit, fetch + rebase, `git push origin HEAD:main`. Then Metricool `createScheduledPost` (blogId 7672444) with
   media [manifest url], providers [{"network": "youtube"}], publicationDate {dateTime: "YYYY-MM-DDT16:00:00", timezone: "Europe/Lisbon"},
   text = description, "youtubeData": {"title": title, "type": "short" or "video", "privacy": "public", "tags": [relevant tags, "noggin"],
   "category": "ENTERTAINMENT", "madeForKids": false, "isAiGeneratedContent": false}, plus "autoPublish": true, "draft": false,
   "descendants": [], "firstCommentText": "", "hasNotReadNotes": false, "mediaAltText": [], "shortener": false, "smartLinkData": {"ids": []}.
6. **Report:** the date, kind, format, title, length, and posts used / 18 that month.
