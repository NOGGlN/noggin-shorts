# Noggin Shorts: daily production

This repo holds the Noggin YouTube Shorts video engine (`engine/`) and the rendered videos (`videos/<date>/`).
Videos are published to the NOGGIN YouTube channel through Metricool (brand id `7672444`, timezone Europe/Lisbon).

## Daily slots (Europe/Lisbon)
7 Shorts per day at: **09:00, 10:40, 12:20, 14:00, 15:40, 17:20, 19:00** (100-minute gaps, never more than 7 a day).

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
