# Noggin Shorts: daily production

This repo holds the Noggin YouTube Shorts video engine (`engine/`) and the rendered videos (`videos/<date>/`).
Videos are published to the NOGGIN YouTube channel through Metricool (brand id `7672444`, timezone Europe/Lisbon).

## Daily slots (Europe/Lisbon)
Every day, on all three networks (YouTube @NOGGIN, Instagram @nogglndaily, TikTok @noggin.daily):
- **1 news edition at 10:00** ("News job" at the end): YouTube = the video Short; Instagram + TikTok = the swipeable PHOTO carousel.
- **2 puzzle/trivia videos at 12:20 and 19:00** (the puzzle scheduled task; its prompt overrides the old 7-a-day rule below):
  the same video goes to YouTube (Short), Instagram (Reel) and TikTok (video).
Posts with draft=true don't count. The 16:00 slot is no longer used.

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


## News job (real stories only) - run by the "Noggin daily news" scheduled task
Format: **"The Noggin Times"** - a retro newspaper look made for Gen Z's analog/print revival trend: paper texture and grain,
Fraktur masthead, Times-style headlines, typewriter labels, halftone black-and-white photos with tape corners, red "EXTRA!" stamp
on the first story, page-turn transitions, "Letters to the Editor" ending. Engine: `engine/news4.py`; `engine/make_news.py` renders
a day (it numbers the issues and prints the publish date on the masthead). Sample: `engine/days/news_sample4.py` (copy its style).
NO quiz, NO fake headlines, NO voting. Each video = 2-3 REAL main stories in the left column: photo + headline, then a lead
(1-2 sentences, drop cap), then FINE PRINT (`body`, 50-80 words, more real detail so it reads like a real article), then the source.
Right column on every page: "IN BRIEF" sidebar with 3-5 short real items (see step 2b) - a DIFFERENT set of briefs on each story page.
Every edition is ALSO posted as a swipeable photo carousel on Instagram (@nogglndaily, 4:5) and TikTok photo mode (@noggin.daily, 9:16),
made by `engine/carousel.py` (cover, 2 slides per story, In Brief grid slides, Letters to the Editor). make_news.py renders them too. Sound: ambient bed + paper rustles + stamp thuds, no song, no ticks.
(news2.py = old Real-or-Fake format, news3.py = old dark modern look; neither is used any more.)

1. **Target day:** Metricool `getScheduledPosts` (brand 7672444, Europe/Lisbon) from tomorrow to +7 days. Earliest day where the
   10:00 slot has no non-draft YouTube post. Make exactly 1 edition for that day. Nothing free -> report "nothing to do".
2. **Find stories** people will want to SHARE: the most recent (last 7 days, prefer last 3) jaw-dropping, funny, weird, ironic or
   dark-humor-but-harmless real news (bizarre mishaps nobody was hurt in, absurd lawsuits and laws, creepy or cursed finds, animals
   behaving badly, embarrassing company or official fails, record-breaking or "how is this real" science and space).
   Pick the strongest one as story 1 (the first 2 seconds decide if people stay). Each video 2-3 stories with a common angle if possible.
   - NOT allowed in main stories: anyone dying or badly hurt, crime with victims, disasters, war, politics/elections (votes go in the
     sidebar only, as neutral facts), religion, mocking private people,
     anything about children, sex. If in doubt, skip it.
   - Confirm each story by fetching the article itself on a trusted outlet (AP, Reuters, BBC, The Guardian, NYT, Washington Post, CNN, NBC,
     CBS, ABC, Fox News, Al Jazeera, NPR, Sky News, The Independent, Euronews, NASA/ESA, Nature, Science, New Scientist,
     National Geographic, UPI Odd News). Use its real headline, outlet, date and full link. Never trust a headline from search alone.
     Every number and detail on screen must match the article.
   - Check `engine/data/used_news.json`: never reuse a story.
   - Your headline: short, plain, punchy, under ~20 words, no emoji. `detail` (lead): 1-2 sentences, under ~25 words.
     `body` (fine print): 50-80 words in 1-2 paragraphs (split with "\n") with extra facts from the article: who, where, numbers,
     what happens next. Rewrite in your own words, never copy sentences from the article. Every fact must be in the article.
     `numbers`: 4 key facts as (big number, short label), e.g. ("1998", "the year he set off from Chile") - shown as a
     "BY THE NUMBERS" box on the carousel's second slide for each story. Every number must be in the source article.
     `explain_photo` + `explain_credit`: a SECOND, different photo for each main story (the carousel's second slide uses it,
     so the two slides of a story never show the same picture). The second slide must never repeat the headline or the lead.
2b. **In Brief sidebar** (3-5 items PER STORY PAGE, so 6-10 per video; every page and every video of the day gets different items): quick real news a Gen Z viewer cares about,
   from the last 7 days, each with a category label:
   - TECH / LAUNCH: new phones, cars, consoles, gadgets, apps (e.g. a new Tesla), with the key feature and price.
   - DROPS: sneakers, fashion and beauty drops, perfumes, collabs, store openings, with release date and price.
   - SPORT / F1: results, title races, transfers, next race date.
   - VOTES: elections, referendums, parliament votes (dates, what is being voted, results). Strictly neutral facts only: no opinions,
     no praise or criticism of any party or politician, no predictions.
   - STRIKES / SCHOOL: strikes, school holidays, exam dates, transport strikes (Portugal and Europe are good: the owner is in Portugal).
   - also good: movie/series/game releases, concerts and tour announcements, money (prices going up/down), space launches, weather records.
   Each item: `dict(cat=, title= (under ~10 words), text= (1-2 short sentences), price= (optional, e.g. "Price: $135" or
   "Out: Nov 7"), photo="assets/photos/<date>/<name>.jpg", credit="What it shows | Author / License",
   source=dict(outlet=, date="Oct 27", link=full URL))`. EVERY brief gets an ACCURATE photo of the exact thing it is about
   (the exact new car, the exact shoe colourway, the exact perfume bottle, this season's F1 car, the real building...).
   Where to get it, in this order:
     a) Wikimedia Commons, if an exact recent photo exists (search with `gsrsort=create_timestamp_desc`; e.g. this season's F1 car).
     b) For brand-new products: the BRAND'S OWN official photo, from its own product/launch page or official press/newsroom page
        (e.g. tesla.com/roadster, nike.com/launch, apple.com/newsroom, the perfume house's own site). Credit it "Image: <Brand>".
        The owner approved this ONLY as long as it can't hurt the channel's income, so: never photos from photo agencies or wires
        (Getty, AP, Reuters, Shutterstock, Alamy), never photos taken by blogs/magazines/retailers' own photographers, never
        screenshots of other videos, never photos of real people from brand sites. Brand product shots only.
     c) If no exact photo exists in a) or b), pick a different brief that has one. Don't use a "similar" stand-in photo.
   Each new site needs a one-time browser approval (Claude_Browser__request_access, scope "site"); if it is refused, use another brief. Confirm every item by fetching the article (trusted news
   outlets, or for product drops: official brand pages, Vogue, GQ, Complex, Hypebeast, Highsnobiety, Sole Retriever, The Verge).
   Prices and dates must match the source exactly. No deaths, crime, disasters or war in briefs either.
3. **Photos** (one per headline, optional explain_photo, plus one per brief - for briefs see the order of sources in 2b):
   main-story photos only from free-license Wikimedia Commons (includes NASA). Never news photos, never real people's faces as the subject, never a logo on its own (a product showing its own
   branding is fine). The cloud workspace can't reach Commons, so use the BUILT-IN browser on the
   owner's computer (load tools with ToolSearch "mcp__remote-devices__Claude_Browser__", max_results 64; commons.wikimedia.org is
   already allowed). In a Commons tab, run javascript: query the API
   (`https://commons.wikimedia.org/w/api.php?action=query&format=json&origin=*&generator=search&gsrnamespace=6&gsrsearch=<q> filetype:bitmap&prop=imageinfo&iiprop=url|size|extmetadata&iiurlwidth=1280`),
   pick photos with license Public domain / CC0 / CC BY / CC BY-SA, then fetch each `thumburl` as a blob and click an <a download> to save it.
   The files land in `C:\Users\ahmi\Downloads` with random names ending `.tmp`; match them by byte size (`device_list_dir`), stage them
   with `device_stage_files`, copy to `engine/assets/photos/<date>/<name>.jpg`, then move the .tmp files on the computer into
   `C:\Users\ahmi\Downloads\_to_delete\` if a shell is available (otherwise list them in the final report).
   Write the credit on the photo (`"Place | Author / License"`) and in the description.
   If the computer or browser can't be reached: STOP the news job and report it. Do not make news without photos.
4. **Day file** `engine/days/news_YYYY_MM_DD.py` with
   `NEWS = [dict(title=..., hook=..., items=[2-3 items], briefs=[[page-1 briefs], [page-2 briefs], ...], description=..., caption=...), ...]`
   (briefs = one list per story page, 3-5 each). caption = the Instagram/TikTok text: hook line, one line per main story, "Sources:" with
   outlet + link for each story and brief, photo credits, then `#news #crazynews #didyouknow #noggin #thenoggintimes`. Items exactly like
   news_sample4.py (text, detail, body, photo, credit, optional explain_photo/explain_credit, source with outlet/date/headline/url/link). hook = on-screen opener, e.g.
   "3 things that actually happened this week". Title: curiosity hook under 60 chars, one emoji, e.g. "This really happened this week 📰 #shorts".
   Description: one hook line, then "Sources:" with outlet + full link for every main story AND every brief, then "Photos (Wikimedia Commons):" credits,
   then `#shorts #news #crazynews #didyouknow #noggin`.
5. **Render:** `cd engine && python3 make_news.py days/news_YYYY_MM_DD.py YYYY-MM-DD`, then open `/tmp/news_check_YYYY-MM-DD.png` with Read
   and also open every carousel slide (`videos/YYYY-MM-DD/news-N-carousel/ig_*.jpg` and `tt_*.jpg`) and check every frame and slide (text fits, nothing overlaps, facts match the articles). Fix and re-render if needed (remove that date's entries from
   used_news.json and delete videos/YYYY-MM-DD/news-* first).
6. **Publish:** commit + push (fetch/rebase first), then for each entry of `videos/YYYY-MM-DD/news_manifest.json`, in its free slot, make
   THREE Metricool `createScheduledPost` calls at the same time (blogId 7672444, timezone Europe/Lisbon):
   a) YouTube Short: same body as the puzzles, media [url], tags ["news", "weird news", "crazy news", "this week", "noggin", "shorts"].
   b) Instagram carousel: providers [{"network": "instagram"}], media = `ig_media` (all slide URLs, in order), text = `caption`,
      "instagramData": {"type": "POST", "isAiGenerated": false}.
   c) TikTok photo post: providers [{"network": "tiktok"}], media = `tt_media` (in order), text = `caption`,
      "tiktokData": {"privacyOption": "PUBLIC_TO_EVERYONE", "title": <title without #shorts, under 90 chars>, "autoAddMusic": true,
      "photoCoverIndex": 0, "disableComment": false, "disableDuet": false, "disableStitch": false,
      "commercialContentThirdParty": false, "commercialContentOwnBrand": false}.
   Each call: "autoPublish": true, "draft": false, "descendants": [], "firstCommentText": "", "hasNotReadNotes": false, "mediaAltText": [],
   "shortener": false, "smartLinkData": {"ids": []}. If one network fails, still schedule the others and report the error.
7. **Report:** date, titles, every headline and brief with its source link, and which of YouTube / Instagram / TikTok got scheduled.
