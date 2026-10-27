# Noggin Shorts: daily production

This repo holds the Noggin YouTube Shorts video engine (`engine/`) and the rendered videos (`videos/<date>/`).
Videos are published to the NOGGIN YouTube channel through Metricool (brand id `7672444`, timezone Europe/Lisbon).

## Daily slots (Europe/Lisbon)
- Puzzle/trivia Shorts: **2 per day at 12:20 and 19:00** (the puzzle scheduled task; its prompt overrides the old 7-a-day rule below).
- Real-or-Fake news Shorts: **max 2 per day at 10:00 and 16:00** (see "News job" at the end).
Never more than 4 Shorts a day in total. Posts with draft=true don't count.

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
6. **Schedule** each video in `manifest.json` with Metricool `createScheduledPost` into the free slots, in order:
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


## News job (Real or Fake?) - run by the "Noggin daily news" scheduled task
Engine: `engine/news2.py` (look + sound) and `engine/make_news.py` (renders a day). Sample: `engine/days/news_sample2.py`.
Style: dark modern news look, real photo per headline, NO song (MUSIC = None gives the ambient tension bed), no ticks.

1. **Target day:** Metricool `getScheduledPosts` (brand 7672444, Europe/Lisbon) from tomorrow to +7 days. Earliest day where the
   10:00 and/or 16:00 slot has no non-draft YouTube post. Make 1 video per free news slot (max 2). Nothing free -> report "nothing to do".
2. **Find stories.** Each video = 3 headlines: 2 real + 1 fake, or 1 real + 2 fake (mix it up). Real stories:
   - published in the last 7 days (prefer last 3), shocking / funny / weird / ironic / "dark humor" (bizarre mishaps nobody was hurt in,
     absurd lawsuits and laws, cursed or creepy finds, animals behaving badly, embarrassing company or official fails, weird science).
   - NOT allowed: anyone dying or badly hurt, crime with victims, disasters, war, politics/elections, religion, mocking private people,
     anything about children, sex. If in doubt, skip it.
   - Confirm each one on at least one trusted outlet (AP, Reuters, BBC, The Guardian, NYT, Washington Post, CNN, NBC, CBS, ABC, Fox News,
     Al Jazeera, NPR, Sky News, The Independent, Euronews, NASA/ESA, Nature, Science, New Scientist, National Geographic, UPI Odd News)
     by fetching the article itself. Use the article's real headline, outlet, date and full link. Never trust a headline from search alone.
   - Check `engine/data/used_news.json`: never reuse a story.
   - Fake headlines: believable but clearly false, about the same kind of topic; the "fix" says what is actually true (and must be true).
   - Headline text you write: short, plain, punchy, under ~20 words, no emoji.
3. **Photos** (one per headline, optional explain_photo / fix_photo): only free-license photos from Wikimedia Commons (includes NASA).
   Never news photos, never real people's faces, never logos. The cloud workspace can't reach Commons, so use the BUILT-IN browser on the
   owner's computer (load tools with ToolSearch "mcp__remote-devices__Claude_Browser__", max_results 64; commons.wikimedia.org is
   already allowed). In a Commons tab, run javascript: query the API
   (`https://commons.wikimedia.org/w/api.php?action=query&format=json&origin=*&generator=search&gsrnamespace=6&gsrsearch=<q> filetype:bitmap&prop=imageinfo&iiprop=url|size|extmetadata&iiurlwidth=1280`),
   pick photos with license Public domain / CC0 / CC BY / CC BY-SA, then fetch each `thumburl` as a blob and click an <a download> to save it.
   The files land in `C:\Users\ahmi\Downloads` with random names ending `.tmp`; match them by byte size (`device_list_dir`), stage them
   with `device_stage_files`, copy to `engine/assets/photos/<date>/<name>.jpg`, then move the .tmp files on the computer into
   `C:\Users\ahmi\Downloads\_to_delete\` if a shell is available (otherwise list them in the final report).
   Write the credit on the photo (`"Place | Author / License"`) and in the description.
   If the computer or browser can't be reached: STOP the news job and report it. Do not make news without photos.
4. **Day file** `engine/days/news_YYYY_MM_DD.py` with `MUSIC = None` and
   `NEWS = [dict(title=..., items=[3 items], description=...), ...]`. Items exactly like news_sample2.py, plus `source["link"]`
   (full URL) for real ones. Title: curiosity hook under 60 chars, one emoji, e.g. "Only 1 of these is real 🤯 #shorts".
   Description: one hook line, then "Sources:" with outlet + full link for every real story, then "Photos (Wikimedia Commons):" credits,
   then `#shorts #news #realorfake #didyouknow #noggin`.
5. **Render:** `cd engine && python3 make_news.py days/news_YYYY_MM_DD.py YYYY-MM-DD`, then open `/tmp/news_check_YYYY-MM-DD.png` with Read
   and check every frame (text fits, nothing overlaps, right verdict). Fix and re-render if needed (remove that date's entries from
   used_news.json and delete videos/YYYY-MM-DD/news-* first).
6. **Publish:** commit + push (fetch/rebase first), then schedule each entry of `videos/YYYY-MM-DD/news_manifest.json` in its free slot with
   the same createScheduledPost body as the puzzles, but tags ["news", "real or fake", "weird news", "trivia", "noggin", "shorts"].
7. **Report:** date, titles, every headline with REAL/FAKE and its source link.
