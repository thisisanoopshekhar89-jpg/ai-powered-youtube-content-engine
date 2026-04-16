# 🐂🐻 AI-Powered YouTube Content Engine
### The Dumb Money Club — From News to Upload in One Command

> **`python main.py`** — That's it. The pipeline does everything else.

[![Channel](https://img.shields.io/badge/YouTube-@DumbMoneyClub2026-red?logo=youtube)](https://youtube.com/@DumbMoneyClub2026)
[![Python](https://img.shields.io/badge/Python-3.14-blue?logo=python)](https://python.org)
[![Claude](https://img.shields.io/badge/Claude-Opus-orange?logo=anthropic)](https://anthropic.com)
[![ElevenLabs](https://img.shields.io/badge/Voice-ElevenLabs-purple)](https://elevenlabs.io)

---

## What This Is

A fully automated daily YouTube Shorts show — **The Dumb Money Club** — powered entirely by AI.

Two animated characters, Bull and Bear, present the day's biggest financial, political and viral news as a live TV show. Five stories. Five chapters. Five shorts. One main episode. All published daily without any human editing.

**Bull is always wrong. Bear is always right. The comedy is watching Bull figure it out in real time.**

### Results (16 days, zero paid promotion)
- **11,200+ views** organic
- **35 subscribers**
- **13+ hours** watch time
- **463 views** on top short
- **36% retention** on best performing video

---

## The Pipeline

```
python main.py
     │
     ├── STEP 1  📰 News Scanner
     │           NewsAPI + CoinGecko + Reddit
     │           5 unique stories — Global | Person | Market | Viral | Crypto
     │
     ├── STEP 2  ✍️  Script Writer (Claude Opus)
     │           One flowing TV show conversation
     │           5 chapters with CTAs and transitions
     │           Raina energy — raw, unfiltered, true
     │
     ├── STEP 2b 🖼️  Thumbnail Generator
     │           Character PNGs composited on dark background
     │           Episode-specific text from script SEO field
     │
     ├── STEP 3  🎙️  Voice Engine (ElevenLabs)
     │           Bull, Bear and Announcer voiced
     │           All beats — cold_open, argument, CTA, transition
     │
     ├── STEP 4  🎬  Video Assembler
     │           Characters lip-synced to every beat
     │           Expression PNG swapped per dialogue beat
     │
     ├── STEP 5  🎵  Intro + Outro
     │           12s animation with jingle and announcer
     │           Branded outro slide
     │
     ├── STEP 6  🔗  Final Assembly (FFmpeg)
     │           Intro + Main + Outro concatenated
     │
     ├── STEP 7  ✂️  Shorts Cutter
     │           5 shorts cut at exact story boundaries
     │           Each short = cold_open → CTA (self-contained arc)
     │
     ├── STEP 8  🔍  QC Bot
     │           Automated quality check before upload
     │           Blocks upload if standards not met
     │
     └── STEP 9  📺  YouTube Uploader
                 Main episode + 5 shorts
                 SEO titles, descriptions, tags, thumbnail
                 Curiosity gap title format proven by analytics
```

---

## Show Format

Each episode is structured as **one continuous TV show** — not five separate segments.

```
[INTRO — 12s animation + jingle + announcer]
↓
Chapter 1 — Global News
cold_open → bull → bear → argument → CTA → transition
↓
Chapter 2 — Name Said WHAT
cold_open → bull → bear → argument → CTA → transition
↓
Chapter 3 — Market Update (BTC / BNB / Gold)
cold_open → bull → bear → argument → CTA → transition
↓
Chapter 4 — Viral / AI / Startup
cold_open → bull → bear → argument → CTA → transition
↓
Chapter 5 — The Closer (philosophical truth)
cold_open → bull → bear → argument → Bear CTA only
↓
[OUTRO — jingle slide]
```

**Shorts** are extracted from each chapter — `cold_open → CTA`. The transition belongs to the main show only. Each short has a proper beginning, middle and end.

---

## Tech Stack

| Component | Technology | Purpose |
|---|---|---|
| Script | Claude Opus (Anthropic) | Full episode as one TV show |
| Voices | ElevenLabs | Bull, Bear, Announcer |
| Video | FFmpeg + Python | Assembly, cuts, audio mixing |
| News | NewsAPI + CoinGecko + Reddit | 5 unique daily stories |
| Upload | YouTube Data API v3 | Main + 5 shorts with SEO |
| Thumbnails | Pillow | Character PNG compositing |
| QC | Custom QC Bot | Pre-upload quality gate |
| Pipeline | Python 3.14 | Orchestration |

---

## Content Strategy

### Title Format — Curiosity Gap
Based on channel analytics, unfinished titles outperform complete ones:

| Chapter | Title Format |
|---|---|
| Global | `[fact]... and nobody saw this coming` |
| Person | `[fact]... Bear has the receipt` |
| Market | `[price/impact]... your wallet already knows` |
| Viral | `[hook]... Bear is not impressed` |
| Closer | `Bear said something tonight we cannot stop thinking about` |

### Top Performing Titles (by views)
```
463 — The government found $1.5 trillion. It's not for your hospital.
438 — America owes the planet $10 trillion. Guess who's actually paying it.
350 — Someone on cable news suggested taxing the route that carries...
350 — Ford just spent millions building a car that costs more than your house.
302 — Scientists built a battery that charges a MILLION times faster...
```

### The Writing Energy
Scripts are written in the spirit of sharp, unfiltered financial commentary:
- Bear states facts. No softening. No diplomatic language.
- Bull is delusionally confident — wrong every time, funnier every episode.
- Cold opens grab before they explain — personal, almost aggressive.
- Chapter 5 closer connects all 4 stories into one human truth.

---

## Project Structure

```
dumbmoney/
├── main.py                  # Master pipeline — run this
├── news_scanner.py          # 5-category news fetcher
├── script_writer.py         # Claude Opus script writer
├── voice_engine.py          # ElevenLabs voice generator
├── video_assembler.py       # Character animation + lip sync
├── youtube_uploader.py      # YouTube API uploader
├── thumbnail_generator.py   # Auto thumbnail generator
├── qc_bot.py               # Pre-upload quality control
├── twitter_poster.py        # Twitter/X auto posting
└── sound_engine.py          # Audio processing helpers

assets/
├── characters/
│   ├── bull/bull_v2/        # 20 Bull expression PNGs
│   └── bear/bear_v2/        # 20 Bear expression PNGs
├── stage/
│   └── introtoclub.mp4      # Intro animation
└── sounds/
    ├── jingle.mp3            # Intro jingle
    └── jingleoutro.mp3       # Outro jingle

output/
├── episodes/YYYYMMDD/       # Generated episode files
├── news/                    # Daily news scans
├── thumbnails/              # Generated thumbnails
└── episode_memory.json      # Rolling 30-episode memory
```

---

## Setup

### Prerequisites
```bash
pip install anthropic elevenlabs requests python-dotenv pillow
pip install google-api-python-client google-auth-oauthlib
```

FFmpeg must be installed and in PATH.

### Environment Variables
Create `.env` in the project root:
```env
ANTHROPIC_API_KEY=your_key_here
ELEVENLABS_API_KEY=your_key_here
NEWSAPI_KEY=your_key_here
```

### YouTube OAuth
1. Create a project in Google Cloud Console
2. Enable YouTube Data API v3
3. Download `youtube_credentials.json` to project root
4. Run once to authenticate:
```bash
python -c "from youtube_uploader import get_youtube_service; get_youtube_service()"
```

### Character Assets
Place character expression PNGs in:
```
assets/characters/bull/bull_v2/*.png
assets/characters/bear/bear_v2/*.png
```

Required expressions: `neutral, excited_arms_up, adbhuta, raudra, hasya, smug,
facepalm, thinking, pointing, arms_crossed, shringara, vira, karuna, shanta,
bhayanaka, mic_drop, exaggerated_laugh, mouth_open, mouth_half, mouth_closed`

---

## Running

```bash
# Full daily episode — news to upload
python main.py

# Test news scanner only
python news_scanner.py

# Test script writer only
python script_writer.py

# QC check on today's episode
python qc_bot.py
```

---

## How It Grows

YouTube Shorts algorithm works in waves. Channels at this stage are tested with small audiences. One short breaking out resets the trajectory — all older content gets pushed simultaneously.

The content formula is already validated by the data. Curiosity gap titles, personal financial impact and the Bull vs Bear conflict drive watch time and shares.

**Target:** One short crossing 5,000 views by Day 60. Based on current trajectory and improving content quality, achievable without paid promotion.

---

## Architecture Decisions

**Why one script for the full episode?**
Claude Opus writes all 5 chapters in one API call — it knows all the stories simultaneously and writes transitions that grammatically connect to the next cold_open. This makes the full episode feel like one conversation, not 5 stitched segments.

**Why story-boundary shorts?**
Shorts cut at equal time splits miss story beginnings and endings. We map actual beat video durations to find exact `cold_open_start` and `cta_end` timestamps, giving each short a proper arc.

**Why QC bot before upload?**
Automated content can fail silently — corrupt audio, duplicate stories, missing expressions. The QC bot catches these before they go public.

**Why curiosity gap titles?**
Channel analytics prove it. Every top-performing title cuts before the reveal. The viewer must click to find out what happened.

---

## What's Next

- [ ] VPS migration for 24/7 automation (Hetzner, ~€4/month)
- [ ] Thumbnail quality v2 — larger characters, bolder text
- [ ] Community tab — Bear posts daily one-liners
- [ ] Shorts series — themed weeks around one macro topic
- [ ] Multi-language versions

---

## Author

Built by a solo founder in 16 days. Zero employees. Zero budget. One command.

**Channel:** [@DumbMoneyClub2026](https://youtube.com/@DumbMoneyClub2026)

---

*Smart Money. Stupid World.*
